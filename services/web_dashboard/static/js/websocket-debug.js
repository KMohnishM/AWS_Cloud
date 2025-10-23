/**
 * WebSocket Debug Console for Hospital Monitoring System
 * This module adds extensive console debugging tools for WebSocket connections
 */

const WebSocketDebug = {
    // State
    state: {
        enabled: false,
        connectionEvents: [],
        lastPingTime: null,
        pingResults: [],
        prometheusStatus: 'unknown',
        maxEvents: 50, // Maximum number of events to keep in history
        startTime: new Date(),
        socketOptions: null
    },
    
    // Initialize the debug panel
    init: function() {
        // Check if debug mode is already enabled in localStorage
        this.state.enabled = localStorage.getItem('websocketDebug') === 'true';
        
        // Create debug panel in DOM
        this.createDebugPanel();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Log initialization
        this.log('WebSocket Debug Console initialized');
        console.log('🐛 WebSocket Debug Console initialized');
        
        return this;
    },
    
    // Create the debug panel in the DOM
    createDebugPanel: function() {
        // Create the debug panel container if it doesn't exist
        if (!document.getElementById('websocket-debug-panel')) {
            const debugPanel = document.createElement('div');
            debugPanel.id = 'websocket-debug-panel';
            debugPanel.className = 'websocket-debug-panel';
            debugPanel.style.display = this.state.enabled ? 'block' : 'none';
            
            debugPanel.innerHTML = `
                <div class="debug-panel-header">
                    <h4>WebSocket Debug Console</h4>
                    <div class="debug-panel-controls">
                        <button id="ws-debug-clear" class="debug-btn" title="Clear logs">🗑️</button>
                        <button id="ws-debug-ping" class="debug-btn" title="Test connection">🏓</button>
                        <button id="ws-debug-prometheus" class="debug-btn" title="Test Prometheus">📊</button>
                        <button id="ws-debug-close" class="debug-btn" title="Close debug panel">✖️</button>
                    </div>
                </div>
                <div class="debug-panel-content">
                    <div class="debug-status-section">
                        <div class="status-indicator">
                            <span class="status-label">Status:</span>
                            <span id="ws-debug-status" class="status-value disconnected">Disconnected</span>
                        </div>
                        <div class="status-indicator">
                            <span class="status-label">Latency:</span>
                            <span id="ws-debug-latency" class="status-value">-</span>
                        </div>
                        <div class="status-indicator">
                            <span class="status-label">Transport:</span>
                            <span id="ws-debug-transport" class="status-value">-</span>
                        </div>
                        <div class="status-indicator">
                            <span class="status-label">Prometheus:</span>
                            <span id="ws-debug-prometheus-status" class="status-value unknown">Unknown</span>
                        </div>
                    </div>
                    <div class="debug-details-section">
                        <div class="debug-tabs">
                            <button class="debug-tab-btn active" data-tab="events">Events</button>
                            <button class="debug-tab-btn" data-tab="stats">Stats</button>
                            <button class="debug-tab-btn" data-tab="config">Config</button>
                        </div>
                        <div class="debug-tab-content active" id="debug-tab-events">
                            <div id="ws-debug-events" class="event-log"></div>
                        </div>
                        <div class="debug-tab-content" id="debug-tab-stats">
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <span class="stat-label">Connected for:</span>
                                    <span id="ws-debug-uptime" class="stat-value">-</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Connection attempts:</span>
                                    <span id="ws-debug-connect-attempts" class="stat-value">0</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Avg. Latency:</span>
                                    <span id="ws-debug-avg-latency" class="stat-value">-</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Disconnect count:</span>
                                    <span id="ws-debug-disconnect-count" class="stat-value">0</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Last error:</span>
                                    <span id="ws-debug-last-error" class="stat-value">-</span>
                                </div>
                            </div>
                        </div>
                        <div class="debug-tab-content" id="debug-tab-config">
                            <div id="ws-debug-config" class="debug-config">
                                <div class="config-item">Loading config...</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Append to body
            document.body.appendChild(debugPanel);
            
            // Create toggle button
            const toggleBtn = document.createElement('button');
            toggleBtn.id = 'websocket-debug-toggle';
            toggleBtn.className = 'websocket-debug-toggle';
            toggleBtn.innerHTML = '🛠️';
            toggleBtn.title = 'Toggle WebSocket Debug Console';
            document.body.appendChild(toggleBtn);
        }
    },
    
    // Setup event listeners for the debug panel
    setupEventListeners: function() {
        // Toggle debug panel
        const toggleBtn = document.getElementById('websocket-debug-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
        
        // Panel controls
        document.addEventListener('click', (e) => {
            if (e.target.id === 'ws-debug-close') {
                this.toggle(false);
            } else if (e.target.id === 'ws-debug-clear') {
                this.clearLogs();
            } else if (e.target.id === 'ws-debug-ping') {
                this.ping();
            } else if (e.target.id === 'ws-debug-prometheus') {
                this.checkPrometheus();
            }
        });
        
        // Tab navigation
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('debug-tab-btn')) {
                const tab = e.target.getAttribute('data-tab');
                this.showTab(tab);
            }
        });
        
        // Hook into global socket events if available
        document.addEventListener('DOMContentLoaded', () => {
            this.hookGlobalSocket();
            
            // Start uptime counter
            setInterval(() => this.updateUptime(), 1000);
        });
    },
    
    // Hook into global socket events
    hookGlobalSocket: function() {
        if (window.globalSocket) {
            console.log('🔌 Hooking into global socket');
            
            // Store socket options
            this.state.socketOptions = window.globalSocket.io.opts;
            this.updateConfigTab();
            
            // Connection events
            window.globalSocket.on('connect', () => {
                this.updateStatus('connected');
                this.log('Socket connected', 'success');
                this.state.connectAttempts = 0;
                this.updateStatsTab();
            });
            
            window.globalSocket.on('disconnect', (reason) => {
                this.updateStatus('disconnected');
                this.log(`Socket disconnected: ${reason}`, 'error');
                this.state.disconnectCount = (this.state.disconnectCount || 0) + 1;
                this.updateStatsTab();
            });
            
            window.globalSocket.on('connect_error', (error) => {
                this.updateStatus('error');
                this.log(`Connection error: ${error.message}`, 'error');
                this.state.lastError = error.message;
                this.updateStatsTab();
            });
            
            window.globalSocket.on('reconnect_attempt', (attemptNumber) => {
                this.updateStatus('reconnecting');
                this.log(`Reconnection attempt ${attemptNumber}`, 'warning');
                this.state.connectAttempts = attemptNumber;
                this.updateStatsTab();
            });
            
            window.globalSocket.on('reconnect', (attemptNumber) => {
                this.updateStatus('connected');
                this.log(`Reconnected after ${attemptNumber} attempts`, 'success');
                this.updateStatsTab();
            });
            
            // Prometheus status
            window.globalSocket.on('prometheus_status', (data) => {
                this.updatePrometheusStatus(data.status, data);
                if (data.status === 'healthy') {
                    this.log(`Prometheus healthy: ${data.latency_ms}ms`, 'success');
                } else {
                    this.log(`Prometheus ${data.status}: ${data.error || ''}`, 'error');
                }
            });
            
            window.globalSocket.on('prometheus_error', (data) => {
                this.updatePrometheusStatus('error', data);
                this.log(`Prometheus error: ${data.message}`, 'error');
            });
            
            // Latency testing
            window.globalSocket.on('pong_response', (data) => {
                const latency = Date.now() - data.client_timestamp;
                this.updateLatency(latency);
                this.log(`Ping: ${latency}ms`, 'info');
                
                // Store ping result for stats
                this.state.pingResults.push(latency);
                if (this.state.pingResults.length > 10) {
                    this.state.pingResults.shift();
                }
                this.updateStatsTab();
            });
            
            // Connection info
            window.globalSocket.on('connection_info', (data) => {
                this.log(`Connected to server: ${data.socket_id}`, 'info');
                
                // Update transport info if available
                if (window.globalSocket.io.engine && window.globalSocket.io.engine.transport) {
                    const transport = window.globalSocket.io.engine.transport.name;
                    document.getElementById('ws-debug-transport').textContent = transport;
                }
            });
        } else {
            console.log('⚠️ Global socket not available yet');
            setTimeout(() => this.hookGlobalSocket(), 1000);
        }
    },
    
    // Toggle debug panel
    toggle: function(force) {
        const debugPanel = document.getElementById('websocket-debug-panel');
        if (!debugPanel) return;
        
        this.state.enabled = force !== undefined ? force : !this.state.enabled;
        debugPanel.style.display = this.state.enabled ? 'block' : 'none';
        
        // Store preference
        localStorage.setItem('websocketDebug', this.state.enabled);
        
        // Log
        if (this.state.enabled) {
            console.log('🐛 WebSocket Debug Console enabled');
            this.updateStatus();
            this.updateStatsTab();
            this.updateConfigTab();
        } else {
            console.log('🐛 WebSocket Debug Console disabled');
        }
    },
    
    // Show a specific tab
    showTab: function(tabName) {
        // Update tab buttons
        const tabBtns = document.querySelectorAll('.debug-tab-btn');
        tabBtns.forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
        });
        
        // Update tab content
        const tabContents = document.querySelectorAll('.debug-tab-content');
        tabContents.forEach(content => {
            content.classList.remove('active');
        });
        
        const activeTab = document.getElementById(`debug-tab-${tabName}`);
        if (activeTab) activeTab.classList.add('active');
        
        // Special actions for specific tabs
        if (tabName === 'stats') {
            this.updateStatsTab();
        } else if (tabName === 'config') {
            this.updateConfigTab();
        }
    },
    
    // Log an event
    log: function(message, type = 'info') {
        if (!this.state.enabled && type !== 'error') return;
        
        // Add to events array
        this.state.connectionEvents.push({
            time: new Date(),
            message,
            type
        });
        
        // Limit array size
        if (this.state.connectionEvents.length > this.state.maxEvents) {
            this.state.connectionEvents.shift();
        }
        
        // Update the UI
        this.updateEventsTab();
        
        // Log to console with color
        const styles = {
            info: 'color: #3498db',
            success: 'color: #2ecc71',
            warning: 'color: #f39c12',
            error: 'color: #e74c3c'
        };
        
        console.log(`%c[WS Debug] ${message}`, styles[type] || '');
    },
    
    // Clear logs
    clearLogs: function() {
        this.state.connectionEvents = [];
        this.updateEventsTab();
        this.log('Logs cleared');
    },
    
    // Update events tab
    updateEventsTab: function() {
        const eventsContainer = document.getElementById('ws-debug-events');
        if (!eventsContainer) return;
        
        const events = this.state.connectionEvents.slice().reverse();
        eventsContainer.innerHTML = events.length === 0 ? 
            '<div class="no-events">No events logged yet</div>' : 
            events.map(event => `
                <div class="event-item event-${event.type}">
                    <span class="event-time">${this.formatTime(event.time)}</span>
                    <span class="event-message">${event.message}</span>
                </div>
            `).join('');
    },
    
    // Update stats tab
    updateStatsTab: function() {
        // Update uptime
        this.updateUptime();
        
        // Update connection attempts
        document.getElementById('ws-debug-connect-attempts').textContent = this.state.connectAttempts || 0;
        
        // Update disconnect count
        document.getElementById('ws-debug-disconnect-count').textContent = this.state.disconnectCount || 0;
        
        // Update average latency
        if (this.state.pingResults && this.state.pingResults.length > 0) {
            const avgLatency = this.state.pingResults.reduce((a, b) => a + b, 0) / this.state.pingResults.length;
            document.getElementById('ws-debug-avg-latency').textContent = `${Math.round(avgLatency)}ms`;
        }
        
        // Update last error
        if (this.state.lastError) {
            document.getElementById('ws-debug-last-error').textContent = this.state.lastError;
        }
    },
    
    // Update config tab
    updateConfigTab: function() {
        const configContainer = document.getElementById('ws-debug-config');
        if (!configContainer) return;
        
        if (this.state.socketOptions) {
            const configItems = [];
            
            for (const [key, value] of Object.entries(this.state.socketOptions)) {
                configItems.push(`
                    <div class="config-item">
                        <span class="config-key">${key}:</span>
                        <span class="config-value">${JSON.stringify(value)}</span>
                    </div>
                `);
            }
            
            // Browser info
            configItems.push(`
                <div class="config-item">
                    <span class="config-key">Browser:</span>
                    <span class="config-value">${navigator.userAgent}</span>
                </div>
            `);
            
            // Network info (if available)
            if (navigator.connection) {
                configItems.push(`
                    <div class="config-item">
                        <span class="config-key">Network type:</span>
                        <span class="config-value">${navigator.connection.type || 'unknown'}</span>
                    </div>
                `);
                
                configItems.push(`
                    <div class="config-item">
                        <span class="config-key">Effective type:</span>
                        <span class="config-value">${navigator.connection.effectiveType || 'unknown'}</span>
                    </div>
                `);
            }
            
            configContainer.innerHTML = configItems.join('');
        } else {
            configContainer.innerHTML = '<div class="config-item">No socket configuration available</div>';
        }
    },
    
    // Update connection status
    updateStatus: function(status) {
        const statusElem = document.getElementById('ws-debug-status');
        if (!statusElem) return;
        
        let currentStatus = status;
        
        // If no status provided, check global socket
        if (!currentStatus && window.globalSocket) {
            currentStatus = window.globalSocket.connected ? 'connected' : 'disconnected';
        }
        
        statusElem.className = `status-value ${currentStatus || 'unknown'}`;
        
        switch(currentStatus) {
            case 'connected':
                statusElem.textContent = 'Connected';
                break;
            case 'disconnected':
                statusElem.textContent = 'Disconnected';
                break;
            case 'reconnecting':
                statusElem.textContent = 'Reconnecting...';
                break;
            case 'error':
                statusElem.textContent = 'Error';
                break;
            default:
                statusElem.textContent = 'Unknown';
        }
    },
    
    // Update Prometheus status
    updatePrometheusStatus: function(status, data) {
        const statusElem = document.getElementById('ws-debug-prometheus-status');
        if (!statusElem) return;
        
        this.state.prometheusStatus = status;
        statusElem.className = `status-value ${status || 'unknown'}`;
        
        switch(status) {
            case 'healthy':
                statusElem.textContent = `Healthy (${data.latency_ms}ms)`;
                break;
            case 'unhealthy':
                statusElem.textContent = 'Unhealthy';
                break;
            case 'timeout':
                statusElem.textContent = 'Timeout';
                break;
            case 'connection_error':
                statusElem.textContent = 'Connection Error';
                break;
            case 'error':
                statusElem.textContent = 'Error';
                break;
            default:
                statusElem.textContent = 'Unknown';
        }
    },
    
    // Update latency display
    updateLatency: function(latency) {
        const latencyElem = document.getElementById('ws-debug-latency');
        if (!latencyElem) return;
        
        let colorClass = 'good';
        if (latency > 300) colorClass = 'medium';
        if (latency > 500) colorClass = 'poor';
        
        latencyElem.textContent = `${latency}ms`;
        latencyElem.className = `status-value ${colorClass}`;
        
        this.state.lastPingTime = new Date();
    },
    
    // Update uptime display
    updateUptime: function() {
        if (!this.state.enabled) return;
        
        const uptimeElem = document.getElementById('ws-debug-uptime');
        if (!uptimeElem) return;
        
        const now = new Date();
        const diff = now - this.state.startTime;
        
        const hours = Math.floor(diff / 1000 / 60 / 60);
        const minutes = Math.floor(diff / 1000 / 60) % 60;
        const seconds = Math.floor(diff / 1000) % 60;
        
        uptimeElem.textContent = `${hours}h ${minutes}m ${seconds}s`;
    },
    
    // Send ping to test latency
    ping: function() {
        if (window.globalSocket && window.globalSocket.connected) {
            this.log('Sending ping test');
            window.globalSocket.emit('ping_test', {
                timestamp: Date.now()
            });
        } else {
            this.log('Cannot ping - socket not connected', 'warning');
        }
    },
    
    // Check Prometheus connection
    checkPrometheus: function() {
        if (window.globalSocket && window.globalSocket.connected) {
            this.log('Testing Prometheus connection');
            window.globalSocket.emit('check_prometheus');
        } else {
            this.log('Cannot check Prometheus - socket not connected', 'warning');
        }
    },
    
    // Format time for display
    formatTime: function(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    WebSocketDebug.init();
});

// Export for global access
window.WebSocketDebug = WebSocketDebug;