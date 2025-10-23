// Modular Dashboard JavaScript for Hospital Monitoring System

const DashboardModule = {
    // State
    state: {
        metrics: {},
        systemStatus: {},
        alerts: [],
        charts: {},
        refreshInterval: null,
        lastUpdateTime: null,
        socket: null, // WebSocket connection
        updateCounter: {
            metrics: 0,
            systemStatus: 0,
            alerts: 0,
            patients: 0
        }
    },

    // Initialize the dashboard module
    init: function() {
        this.setupEventListeners();
        this.setupWebSocket(); // Setup WebSocket before loading data
        this.loadDashboardData(); // Initial data load via REST API
        this.setupUpdateTimestamp();
        console.log('Dashboard module initialized with WebSocket real-time updates');
    },
    
    // Setup WebSocket connection for real-time updates
    setupWebSocket: function() {
        try {
            // Check if Socket.IO is loaded
            if (typeof io === 'undefined') {
                console.error('🔴 Socket.IO not loaded. Falling back to polling.');
                console.warn('⚠️ Please check your network connection and ensure the Socket.IO script is loading properly');
                console.log('💡 Attempting to load Socket.IO dynamically...');
                
                // Show loading notification
                this.showSocketLoadingNotification('Loading Socket.IO library...');
                
                // Create progress bar for loading
                const progressBar = document.getElementById('socket-load-progress');
                if (progressBar) {
                    progressBar.style.width = '10%'; // Start progress
                    
                    // Animate progress gradually
                    let progress = 10;
                    const progressInterval = setInterval(() => {
                        progress += 5;
                        if (progress > 90) clearInterval(progressInterval);
                        progressBar.style.width = progress + '%';
                    }, 300);
                }
                
                // Try to load Socket.IO dynamically
                const script = document.createElement('script');
                script.src = 'https://cdn.socket.io/4.7.2/socket.io.min.js';
                script.onload = () => {
                    // Complete progress bar
                    if (progressBar) {
                        progressBar.style.width = '100%';
                        setTimeout(() => {
                            progressBar.style.opacity = '0';
                            setTimeout(() => {
                                progressBar.style.width = '0';
                                setTimeout(() => {
                                    progressBar.style.opacity = '1';
                                }, 300);
                            }, 300);
                        }, 500);
                    }
                    
                    console.log('✅ Socket.IO loaded dynamically! Retrying connection...');
                    this.updateSocketLoadingNotification('Socket.IO loaded successfully!', 'success');
                    this.createConsoleNotification('Socket.IO loaded dynamically. Retrying connection...', 'success');
                    
                    // Short delay to allow the notification to display
                    setTimeout(() => {
                        this.setupWebSocketAfterLoad();
                    }, 1000);
                };
                script.onerror = () => {
                    // Reset progress bar
                    if (progressBar) {
                        progressBar.style.width = '0';
                    }
                    
                    console.error('❌ Failed to load Socket.IO dynamically. Using polling instead.');
                    this.updateSocketLoadingNotification('Failed to load Socket.IO library. Falling back to polling.', 'error');
                    this.createConsoleNotification('Failed to load Socket.IO. Using polling fallback.', 'error');
                    this.setupAutoRefresh(); // Fall back to polling
                };
                document.head.appendChild(script);
                return;
            }
            
            console.log('🔄 Setting up WebSocket connection...');
            this.createConsoleNotification('Initializing real-time connection...', 'info');
            
            // Connect to the server
            const socketUrl = window.location.protocol + '//' + window.location.host;
            console.log(`🔌 Connecting to WebSocket at ${socketUrl}`);
            
            // Log browser information for debugging
            console.log('🌐 Browser:', navigator.userAgent);
            console.log('📡 Available transports:', io.protocol);
            
            // Create socket with detailed logging and debug options
            this.state.socket = io(socketUrl, { 
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: Infinity,
                timeout: 20000, // Increase timeout for connection
                transports: ['websocket', 'polling'], // Try WebSocket first, fallback to polling
                forceNew: true, // Force new connection
                debug: true // Enable debug logging
            });
            
            // Setup event handlers
            this.state.socket.on('connect', () => {
                const socketId = this.state.socket.id || 'Unknown';
                console.log('✅ WebSocket connected!', socketId);
                this.showConnectionStatus('connected');
                this.createConsoleNotification(`WebSocket connected! Socket ID: ${socketId}`, 'success');
                
                // Log transport type
                const transport = this.state.socket.io.engine.transport.name;
                console.log(`🔌 Using transport: ${transport}`);
                this.createConsoleNotification(`Connected using: ${transport}`, 'info');
                
                // Request initial data
                this.state.socket.emit('request_initial_data');
                console.log('📊 Requested initial data from server');
                
                // Test Prometheus connection
                this.testPrometheusConnection();
                
                // Setup ping test for latency measurement
                this.startPingTest();
            });
            
            this.state.socket.on('disconnect', (reason) => {
                console.log(`🔴 WebSocket disconnected: ${reason}`);
                this.showConnectionStatus('disconnected');
                this.createConsoleNotification(`WebSocket disconnected: ${reason}`, 'error');
                
                // Fall back to polling if WebSocket is disconnected
                console.log('⚠️ Falling back to polling for updates');
                this.setupAutoRefresh();
                
                // Clear ping interval
                if (this.state.pingInterval) {
                    clearInterval(this.state.pingInterval);
                    this.state.pingInterval = null;
                }
            });
            
            this.state.socket.on('connect_error', (error) => {
                console.error('❌ WebSocket connection error:', error);
                this.showConnectionStatus('error');
                this.createConsoleNotification(`Connection error: ${error.message}`, 'error');
                
                // Log details about the error
                this.logConnectionDetails();
            });
            
            this.state.socket.on('reconnect_attempt', (attemptNumber) => {
                console.log(`🔄 WebSocket reconnection attempt ${attemptNumber}`);
                this.showConnectionStatus('reconnecting');
                this.createConsoleNotification(`Reconnection attempt ${attemptNumber}...`, 'warning');
                
                // Log connection details on multiple failed attempts
                if (attemptNumber > 3) {
                    this.logConnectionDetails();
                }
            });
            
            this.state.socket.on('reconnect', (attemptNumber) => {
                console.log(`✅ WebSocket reconnected after ${attemptNumber} attempts`);
                this.showConnectionStatus('connected');
                this.createConsoleNotification(`Reconnected after ${attemptNumber} attempts`, 'success');
                
                // Test Prometheus connection
                this.testPrometheusConnection();
            });
            
            this.state.socket.on('error', (error) => {
                console.error('❌ WebSocket error:', error);
                this.createConsoleNotification(`WebSocket error: ${error}`, 'error');
                
                // Send error to server for logging
                if (this.state.socket && this.state.socket.connected) {
                    this.state.socket.emit('client_log', {
                        type: 'error',
                        message: `WebSocket error: ${error}`
                    });
                }
            });
            
            // Listen for dashboard data updates
            this.state.socket.on('dashboard_stats', (data) => {
                console.log('📈 Received dashboard stats update [Source: WebSocket Real-time]:', data);
                if (!data) {
                    console.error('❌ Received empty dashboard stats data');
                    this.createConsoleNotification('Received empty dashboard stats data', 'warning');
                    return;
                }
                try {
                    this.updateDashboardStatsFromWebSocket(data);
                    this.updateLastUpdatedTimestamp();
                } catch (error) {
                    console.error('❌ Error processing dashboard stats:', error);
                    this.createConsoleNotification(`Error processing stats: ${error.message}`, 'error');
                }
            });
            
            this.state.socket.on('patients_update', (data) => {
                console.log('👥 Received patients update [Source: WebSocket Real-time]:', data);
                if (!data || !data.patients) {
                    console.error('❌ Received invalid patients data');
                    this.createConsoleNotification('Received invalid patients data', 'warning');
                    return;
                }
                try {
                    this.updateRecentPatientsFromWebSocket(data.patients);
                    this.updateLastUpdatedTimestamp();
                } catch (error) {
                    console.error('❌ Error processing patients update:', error);
                    this.createConsoleNotification(`Error processing patients: ${error.message}`, 'error');
                }
            });
            
            this.state.socket.on('system_status', (data) => {
                console.log('🖥️ Received system status update [Source: WebSocket Real-time]:', data);
                if (!data || !data.system_status) {
                    console.error('❌ Received invalid system status data');
                    this.createConsoleNotification('Received invalid system status data', 'warning');
                    return;
                }
                try {
                    this.updateSystemStatus(data.system_status);
                    this.updateLastUpdatedTimestamp();
                } catch (error) {
                    console.error('❌ Error processing system status:', error);
                    this.createConsoleNotification(`Error processing status: ${error.message}`, 'error');
                }
            });
            
            this.state.socket.on('alerts_update', (data) => {
                console.log('🚨 Received alerts update [Source: WebSocket Real-time]:', data);
                if (!data || !data.alerts) {
                    console.error('❌ Received invalid alerts data');
                    this.createConsoleNotification('Received invalid alerts data', 'warning');
                    return;
                }
                try {
                    this.updateRecentAlerts(data.alerts);
                    this.updateLastUpdatedTimestamp();
                } catch (error) {
                    console.error('❌ Error processing alerts update:', error);
                    this.createConsoleNotification(`Error processing alerts: ${error.message}`, 'error');
                }
            });
            
            // Handle Prometheus errors
            this.state.socket.on('prometheus_error', (data) => {
                console.error('🔴 Prometheus error:', data);
                this.createConsoleNotification(`Prometheus error: ${data.message}`, 'error');
                
                // Update UI to show Prometheus error
                this.showPrometheusError(data.message);
            });
            
            // Handle server messages
            this.state.socket.on('dashboard_message', (data) => {
                console.log('📝 Dashboard message:', data);
                this.createConsoleNotification(data.message, data.type || 'info');
            });
            
            // Handle connection info from server
            this.state.socket.on('connection_info', (data) => {
                console.log('ℹ️ Connection info:', data);
                this.state.connectionInfo = data;
                
                // Display connection info in console
                console.log(`🔌 Connected to server: ${data.socket_id}`);
                console.log(`⏱️ Server time: ${data.server_time}`);
                console.log(`🔗 Prometheus URL: ${data.prometheus_url}`);
            });
            
            // Handle ping response for latency calculation
            this.state.socket.on('pong_response', (data) => {
                const roundTripTime = Date.now() - data.client_timestamp;
                console.log(`🏓 WebSocket ping: ${roundTripTime}ms`);
                
                // Update latency info
                this.state.latency = roundTripTime;
                this.updateLatencyIndicator(roundTripTime);
                
                // Log high latency
                if (roundTripTime > 500) {
                    this.createConsoleNotification(`High latency detected: ${roundTripTime}ms`, 'warning');
                }
            });
            
            // Handle Prometheus status check response
            this.state.socket.on('prometheus_status', (data) => {
                console.log('📊 Prometheus status:', data);
                
                if (data.status === 'healthy') {
                    this.createConsoleNotification(`Prometheus is healthy (${data.latency_ms}ms)`, 'success');
                    // Clear any previous error
                    this.clearPrometheusError();
                } else {
                    this.createConsoleNotification(`Prometheus is ${data.status}: ${data.error || 'Unknown issue'}`, 'error');
                    // Show error in UI
                    this.showPrometheusError(data.error || `Status: ${data.status}`);
                }
            });
            
        } catch (error) {
            console.error('❌ Error setting up WebSocket:', error);
            this.createConsoleNotification(`Failed to setup WebSocket: ${error.message}`, 'error');
            this.setupAutoRefresh(); // Fall back to polling if WebSocket setup fails
        }
    },
    
    // Start ping test for latency measurement
    startPingTest: function() {
        // Clear existing interval
        if (this.state.pingInterval) {
            clearInterval(this.state.pingInterval);
        }
        
        // Send initial ping
        this.sendPing();
        
        // Set up regular pings
        this.state.pingInterval = setInterval(() => {
            this.sendPing();
        }, 15000); // Every 15 seconds
    },
    
    // Send ping to measure latency
    sendPing: function() {
        if (this.state.socket && this.state.socket.connected) {
            console.log('🏓 Sending ping test...');
            this.state.socket.emit('ping_test', {
                timestamp: Date.now()
            });
        }
    },
    
    // Update latency indicator in UI
    updateLatencyIndicator: function(latency) {
        // Find or create latency indicator
        let indicator = document.getElementById('latency-indicator');
        
        if (!indicator) {
            const statusElem = document.getElementById('dashboard-update-status');
            if (statusElem) {
                indicator = document.createElement('span');
                indicator.id = 'latency-indicator';
                indicator.className = 'ms-2 badge rounded-pill';
                statusElem.appendChild(indicator);
            }
        }
        
        if (indicator) {
            // Set color based on latency
            let color = 'bg-success';
            if (latency > 300) color = 'bg-warning';
            if (latency > 500) color = 'bg-danger';
            
            indicator.className = `ms-2 badge rounded-pill ${color}`;
            indicator.textContent = `${latency}ms`;
        }
    },
    
    // Show Socket.IO loading notification
    showSocketLoadingNotification: function(message) {
        // Remove any existing notification
        const existingNotification = document.getElementById('socket-loading-notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Create new notification
        const notification = document.createElement('div');
        notification.id = 'socket-loading-notification';
        notification.className = 'socket-loading-notification';
        notification.innerHTML = `
            <div class="spinner"></div>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 8 seconds to prevent stale notifications
        setTimeout(() => {
            if (document.getElementById('socket-loading-notification')) {
                document.getElementById('socket-loading-notification').remove();
            }
        }, 8000);
    },
    
    // Update Socket.IO loading notification
    updateSocketLoadingNotification: function(message, status) {
        const notification = document.getElementById('socket-loading-notification');
        if (notification) {
            notification.className = `socket-loading-notification ${status || ''}`;
            notification.innerHTML = `<span>${message}</span>`;
            
            // Auto-remove success/error notifications
            setTimeout(() => {
                if (notification && document.body.contains(notification)) {
                    notification.style.opacity = '0';
                    notification.style.transform = 'translateY(-20px) translateX(-50%)';
                    setTimeout(() => {
                        if (notification && document.body.contains(notification)) {
                            notification.remove();
                        }
                    }, 500);
                }
            }, 3000);
        } else {
            // Create new notification if it doesn't exist
            this.showSocketLoadingNotification(message);
            if (status) {
                const newNotification = document.getElementById('socket-loading-notification');
                if (newNotification) {
                    newNotification.className = `socket-loading-notification ${status}`;
                }
            }
        }
    },
    
    // Test Prometheus connection explicitly
    testPrometheusConnection: function() {
        if (this.state.socket && this.state.socket.connected) {
            console.log('🔍 Testing Prometheus connection...');
            this.state.socket.emit('check_prometheus');
        }
    },
    
    // Show Prometheus error in UI
    showPrometheusError: function(message) {
        // Find or create error container
        let errorContainer = document.getElementById('prometheus-error');
        
        if (!errorContainer) {
            // Find a good place to insert the error - top of dashboard stats
            const dashboardStats = document.querySelector('.dashboard-stats');
            
            if (dashboardStats) {
                errorContainer = document.createElement('div');
                errorContainer.id = 'prometheus-error';
                errorContainer.className = 'alert alert-danger mb-4';
                dashboardStats.parentNode.insertBefore(errorContainer, dashboardStats);
            } else {
                // Fallback - create at top of content
                const content = document.querySelector('.content');
                if (content) {
                    errorContainer = document.createElement('div');
                    errorContainer.id = 'prometheus-error';
                    errorContainer.className = 'alert alert-danger mb-4';
                    content.prepend(errorContainer);
                }
            }
        }
        
        if (errorContainer) {
            errorContainer.innerHTML = `
                <strong>⚠️ Prometheus Connection Error:</strong> ${message}
                <button type="button" class="btn-close" aria-label="Close" 
                    onclick="document.getElementById('prometheus-error').style.display='none'"></button>
                <div class="mt-2">
                    <button class="btn btn-sm btn-outline-danger" onclick="DashboardModule.testPrometheusConnection()">
                        Test Connection
                    </button>
                </div>
            `;
            errorContainer.style.display = 'block';
        }
    },
    
    // Clear Prometheus error from UI
    clearPrometheusError: function() {
        const errorContainer = document.getElementById('prometheus-error');
        if (errorContainer) {
            errorContainer.style.display = 'none';
        }
    },
    
    // Log connection details for debugging
    logConnectionDetails: function() {
        console.log('--- CONNECTION DETAILS ---');
        console.log('🌐 Browser:', navigator.userAgent);
        console.log('🔗 URL:', window.location.href);
        console.log('⚙️ Socket options:', this.state.socket ? this.state.socket.io.opts : 'Socket not initialized');
        
        // Check if navigator.connection is available (Network Information API)
        if (navigator.connection) {
            console.log('📶 Network type:', navigator.connection.type);
            console.log('📡 Effective type:', navigator.connection.effectiveType);
            console.log('📊 Downlink:', navigator.connection.downlink, 'Mbps');
            console.log('⏱️ RTT:', navigator.connection.rtt, 'ms');
        }
        
        // Check for Prometheus URL
        console.log('🔗 Prometheus URL:', this.state.connectionInfo?.prometheus_url || 'Unknown');
        
        // Send connection details to server for logging
        if (this.state.socket && this.state.socket.connected) {
            this.state.socket.emit('client_log', {
                type: 'info',
                message: `Connection details: Browser=${navigator.userAgent}, URL=${window.location.href}`
            });
        }
        
        console.log('-------------------------');
    },
    
    // Create a console notification for debugging
    createConsoleNotification: function(message, type = 'info') {
        if (typeof message !== 'string') {
            message = JSON.stringify(message);
        }
        
        const styles = {
            info: 'background: #3498db; color: white; padding: 2px 5px; border-radius: 3px;',
            success: 'background: #2ecc71; color: white; padding: 2px 5px; border-radius: 3px;',
            warning: 'background: #f39c12; color: white; padding: 2px 5px; border-radius: 3px;',
            error: 'background: #e74c3c; color: white; padding: 2px 5px; border-radius: 3px;'
        };
        
        console.log(`%c${type.toUpperCase()}`, styles[type], message);
        
        // Create a visual notification for all types
        // Use notifications container if it exists
        const notificationContainer = document.getElementById('notifications-container') || document.body;
        
        const notificationDiv = document.createElement('div');
        notificationDiv.className = `notification notification-${type}`;
        notificationDiv.innerHTML = `
            <strong>${type.toUpperCase()}:</strong> ${message}
            <span class="notification-close">×</span>
        `;
        notificationContainer.appendChild(notificationDiv);
        
        // Add close functionality
        const closeBtn = notificationDiv.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notificationDiv.remove();
        });
        
        // Auto-remove after different times based on type
        let timeout = 8000; // default
        if (type === 'success') timeout = 5000;
        if (type === 'info') timeout = 6000;
        if (type === 'error') timeout = 10000;
        
        setTimeout(() => {
            if (notificationDiv.parentNode === notificationContainer) {
                notificationDiv.style.opacity = '0';
                notificationDiv.style.transform = 'translateX(100px)';
                setTimeout(() => {
                    if (notificationDiv.parentNode === notificationContainer) {
                        notificationDiv.remove();
                    }
                }, 500);
            }
        }, timeout);
    },
    
    // Show WebSocket connection status
    showConnectionStatus: function(status) {
        // Update the status badge in the dashboard header
        this.updateConnectionStatus(status);
        
        // Also show a temporary notification for status changes
        const statusElem = document.getElementById('websocket-status');
        if (!statusElem) {
            // Create status indicator if it doesn't exist
            const indicator = document.createElement('div');
            indicator.id = 'websocket-status';
            indicator.className = 'websocket-status';
            document.body.appendChild(indicator);
        }
        
        const indicator = document.getElementById('websocket-status');
        
        switch(status) {
            case 'connected':
                indicator.className = 'websocket-status connected';
                indicator.innerHTML = '<i class="bi bi-lightning-fill"></i> Real-time';
                // Hide after 3 seconds
                setTimeout(() => {
                    indicator.classList.add('fade-out');
                }, 3000);
                break;
            case 'disconnected':
                indicator.className = 'websocket-status disconnected';
                indicator.innerHTML = '<i class="bi bi-x-circle"></i> Connection lost';
                break;
            case 'error':
                indicator.className = 'websocket-status error';
                indicator.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Connection error';
                break;
            case 'reconnecting':
                indicator.className = 'websocket-status reconnecting';
                indicator.innerHTML = '<i class="bi bi-arrow-repeat"></i> Reconnecting...';
                break;
        }
    },

    // Setup event listeners
    setupEventListeners: function() {
        // Global refresh event
        document.addEventListener('dashboard:refresh', () => {
            this.loadDashboardData();
        });

        // Quick action buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.quick-action-btn')) {
                const action = e.target.closest('.quick-action-btn').dataset.action;
                this.handleQuickAction(action);
            }
        });
        
        // Manual refresh button
        const refreshBtn = document.getElementById('manual-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.showRefreshIndicator();
                this.loadDashboardData();
            });
        }
    },
    
    // Setup update timestamp display
    setupUpdateTimestamp: function() {
        // Create timestamp element if it doesn't exist
        if (!document.getElementById('dashboard-last-updated')) {
            const welcomeBanner = document.querySelector('.welcome-banner .row');
            if (welcomeBanner) {
                // Create status indicator container
                const statusDiv = document.createElement('div');
                statusDiv.className = 'col-12 mt-3';
                statusDiv.innerHTML = `
                    <div class="d-flex align-items-center justify-content-between">
                        <div>
                            <small class="text-white">
                                <i class="bi bi-arrow-repeat me-1"></i>
                                Last updated: <span id="dashboard-last-updated">Just now</span>
                            </small>
                            <span class="badge rounded-pill bg-light text-primary ms-2" id="dashboard-update-status">
                                <i class="bi bi-check-circle-fill"></i> Real-time
                            </span>
                        </div>
                        <button id="manual-refresh-btn" class="btn btn-sm btn-outline-light">
                            <i class="bi bi-arrow-clockwise"></i> Refresh Now
                        </button>
                    </div>
                `;
                welcomeBanner.parentNode.appendChild(statusDiv);
                
                // Re-attach event listener
                const refreshBtn = document.getElementById('manual-refresh-btn');
                if (refreshBtn) {
                    refreshBtn.addEventListener('click', () => {
                        this.showRefreshIndicator();
                        this.loadDashboardData();
                    });
                }
            }
        }
    },
    
    // Show refresh indicator animation
    showRefreshIndicator: function() {
        const indicator = document.getElementById('dashboard-update-status');
        if (indicator) {
            indicator.innerHTML = '<i class="bi bi-arrow-repeat"></i> Updating...';
            indicator.className = 'badge rounded-pill bg-light text-primary ms-2 pulse';
            
            // Reset after animation
            setTimeout(() => {
                indicator.innerHTML = '<i class="bi bi-check-circle-fill"></i> Real-time';
                indicator.className = 'badge rounded-pill bg-light text-primary ms-2';
                
                // Update timestamp
                this.updateLastUpdatedTimestamp();
            }, 1000);
        }
    },
    
    // Update the timestamp shown
    updateLastUpdatedTimestamp: function() {
        const timestampElement = document.getElementById('dashboard-last-updated');
        if (timestampElement) {
            this.state.lastUpdateTime = new Date();
            timestampElement.textContent = 'Just now';
            
            // Update timestamp every minute
            if (!this.state.timestampInterval) {
                this.state.timestampInterval = setInterval(() => {
                    if (this.state.lastUpdateTime) {
                        timestampElement.textContent = HospitalDashboard.formatRelativeTime(this.state.lastUpdateTime);
                    }
                }, 60000); // Update relative time every minute
            }
        }
    },

    // Load all dashboard data
    async loadDashboardData() {
        this.showRefreshIndicator();
        
        await Promise.all([
            this.loadMetrics(),
            this.loadSystemStatus(),
            this.loadRecentAlerts(),
            this.loadRecentPatients()
        ]);
        
        // Update timestamp after all data is loaded
        this.updateLastUpdatedTimestamp();
    },

    // Load metrics data
    async loadMetrics() {
        const result = await HospitalDashboard.apiRequest(HospitalDashboard.config.apiEndpoints.metrics);
        
        if (result.success) {
            this.state.metrics = result.data;
            this.updateDashboardStats(result.data);
            this.state.updateCounter.metrics++;
            
            // Add update animation to metrics cards
            this.addUpdateAnimation(['total-patients', 'normal-patients', 'warning-patients', 'critical-patients']);
        } else {
            console.error('Failed to load metrics:', result.error);
        }
    },

    // Load system status
    async loadSystemStatus() {
        const result = await HospitalDashboard.apiRequest(HospitalDashboard.config.apiEndpoints.systemStatus);
        
        if (result.success) {
            this.state.systemStatus = result.data.system_status;
            this.updateSystemStatus(result.data.system_status);
            this.state.updateCounter.systemStatus++;
            
            // Add update animation to system status container
            const container = document.getElementById('system-status-list');
            if (container) {
                container.classList.add('update-flash');
                setTimeout(() => {
                    container.classList.remove('update-flash');
                }, 1000);
            }
        } else {
            console.error('Failed to load system status:', result.error);
        }
    },

    // Load recent alerts
    async loadRecentAlerts() {
        const result = await HospitalDashboard.apiRequest(HospitalDashboard.config.apiEndpoints.alerts);
        
        if (result.success) {
            // Check if alerts have changed
            const hasChanged = JSON.stringify(this.state.alerts) !== JSON.stringify(result.data.alerts);
            
            this.state.alerts = result.data.alerts;
            this.updateRecentAlerts(result.data.alerts);
            this.state.updateCounter.alerts++;
            
            // Add update animation if alerts changed
            if (hasChanged) {
                const container = document.getElementById('recent-alerts-list');
                if (container) {
                    container.classList.add('update-flash');
                    setTimeout(() => {
                        container.classList.remove('update-flash');
                    }, 1000);
                }
            }
        } else {
            console.error('Failed to load alerts:', result.error);
        }
    },

    // Load recent patients
    async loadRecentPatients() {
        const result = await HospitalDashboard.apiRequest(HospitalDashboard.config.apiEndpoints.patients);
        
        if (result.success) {
            this.updateRecentPatients(result.data.patients);
            this.state.updateCounter.patients++;
            
            // Add update animation
            const container = document.getElementById('recent-patients-list');
            if (container) {
                container.classList.add('update-flash');
                setTimeout(() => {
                    container.classList.remove('update-flash');
                }, 1000);
            }
        } else {
            console.error('Failed to load patients:', result.error);
        }
    },
    
    // Add update animation to elements
    addUpdateAnimation(elementIds) {
        elementIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                // Find parent card to animate
                const parentCard = element.closest('.stats-card');
                if (parentCard) {
                    parentCard.classList.add('update-flash');
                    setTimeout(() => {
                        parentCard.classList.remove('update-flash');
                    }, 1000);
                }
            }
        });
    },

    // Update dashboard statistics from REST API data
    updateDashboardStats(data) {
        if (!data) return;

        const patientRecords = Object.values(data);
        const uniquePatients = new Set();
        let totalHeartRate = 0;
        let totalAnomalyScore = 0;
        let criticalPatients = 0;
        let warningPatients = 0;
        let normalPatients = 0;

        patientRecords.forEach(record => {
            uniquePatients.add(record.patient);
            totalHeartRate += record.heart_rate || 0;
            totalAnomalyScore += record.anomaly_score || 0;
            
            const anomalyScore = record.anomaly_score || 0;
            if (anomalyScore > 0.7) {
                criticalPatients++;
            } else if (anomalyScore > 0.4) {
                warningPatients++;
            } else {
                normalPatients++;
            }
        });

        // Update UI elements
        this.updateElement('total-patients', uniquePatients.size);
        this.updateElement('critical-patients', criticalPatients);
        this.updateElement('warning-patients', warningPatients);
        this.updateElement('normal-patients', normalPatients);
        
        const avgHeartRate = patientRecords.length > 0 ? 
            Math.round(totalHeartRate / patientRecords.length) : 0;
        const avgAnomalyScore = patientRecords.length > 0 ? 
            (totalAnomalyScore / patientRecords.length).toFixed(2) : 0;
        
        this.updateElement('avg-heart-rate', avgHeartRate + ' BPM');
        this.updateElement('avg-anomaly-score', avgAnomalyScore);
        
        // Log source of update
        console.log('📈 Received dashboard stats update [Source: REST API Fetch]:', data);
    },
    
    // Update dashboard statistics directly from WebSocket data
    updateDashboardStatsFromWebSocket(data) {
        if (!data) return;

        // Update with animation
        this.updateElementWithAnimation('total-patients', data.total_patients);
        this.updateElementWithAnimation('critical-patients', data.critical_patients);
        this.updateElementWithAnimation('warning-patients', data.warning_patients);
        this.updateElementWithAnimation('normal-patients', data.normal_patients);
    },
    
    // Update element with animation
    updateElementWithAnimation(id, value) {
        const element = document.getElementById(id);
        if (element) {
            // Get current value
            const currentValue = parseInt(element.textContent) || 0;
            
            // Only animate if value has changed
            if (currentValue !== value) {
                // Add highlight animation
                element.classList.add('highlight-change');
                
                // Change value
                element.textContent = value;
                
                // Find parent card to animate
                const parentCard = element.closest('.stats-card');
                if (parentCard) {
                    parentCard.classList.add('update-flash');
                    setTimeout(() => {
                        parentCard.classList.remove('update-flash');
                    }, 1000);
                }
                
                // Remove highlight after animation
                setTimeout(() => {
                    element.classList.remove('highlight-change');
                }, 1500);
            }
        }
    },
    
    // Update recent patients from WebSocket data
    updateRecentPatientsFromWebSocket(patients) {
        if (!patients || patients.length === 0) return;
        
        // Add animation class to container
        const container = document.getElementById('recent-patients-list');
        if (container) {
            container.classList.add('update-flash');
            setTimeout(() => {
                container.classList.remove('update-flash');
            }, 1000);
        }
        
        // Update patients
        this.updateRecentPatients(patients);
    },

    // Update system status
    updateSystemStatus(status) {
        const container = document.getElementById('system-status-list');
        if (!container) return;

        if (!status || Object.keys(status).length === 0) {
            container.innerHTML = `
                <li class="list-group-item text-center py-4">
                    <p class="text-muted">No system status data available</p>
                </li>
            `;
            return;
        }

        const serviceNames = {
            'main_host': 'Main Host',
            'ml_service': 'ML Service',
            'patient_simulator': 'Patient Simulator',
            'grafana': 'Grafana',
            'prometheus': 'Prometheus',
            'alertmanager': 'AlertManager'
        };

        const html = Object.entries(status).map(([service, details]) => {
            let statusClass = 'success';
            let iconClass = 'check-circle-fill';
            let statusText = 'Online';

            if (details.status === 'warning') {
                statusClass = 'warning';
                iconClass = 'exclamation-triangle-fill';
                statusText = 'Warning';
            } else if (details.status === 'offline') {
                statusClass = 'danger';
                iconClass = 'x-circle-fill';
                statusText = 'Offline';
            }

            return `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <i class="bi bi-${iconClass} text-${statusClass} me-2"></i>
                        ${serviceNames[service] || service.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        <small class="text-muted ms-2">Uptime: ${details.uptime || 'Unknown'}</small>
                    </div>
                    <span class="badge bg-${statusClass}">${statusText}</span>
                </li>
            `;
        }).join('');

        container.innerHTML = html;
    },

    // Update recent alerts
    updateRecentAlerts(alerts) {
        const container = document.getElementById('recent-alerts-list');
        if (!container) return;

        if (!alerts || alerts.length === 0) {
            container.innerHTML = `
                <li class="list-group-item text-center py-4">
                    <p class="text-muted">No recent alerts</p>
                </li>
            `;
            return;
        }

        const html = alerts.slice(0, 5).map(alert => {
            const levelClass = alert.level === 'warning' ? 'warning' : 'danger';
            const iconClass = alert.level === 'warning' ? 'exclamation-triangle' : 'exclamation-circle';

            return `
                <li class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1 text-${levelClass}">
                            <i class="bi bi-${iconClass}-fill me-2"></i>
                            ${alert.message}
                        </h6>
                    </div>
                    <small class="text-muted">${HospitalDashboard.formatRelativeTime(alert.timestamp)}</small>
                </li>
            `;
        }).join('');

        container.innerHTML = html;
    },

    // Update recent patients
    updateRecentPatients(patients) {
        const container = document.getElementById('recent-patients-list');
        if (!container) return;

        if (!patients || patients.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <p class="text-muted">No patients found</p>
                </div>
            `;
            return;
        }

        const html = patients.slice(0, 5).map(patient => {
            // Handle missing anomaly_score
            const anomalyScore = patient.anomaly_score !== undefined && patient.anomaly_score !== null 
                ? patient.anomaly_score 
                : 0;
                
            const statusColor = HospitalDashboard.getStatusColor(anomalyScore);
            const statusText = HospitalDashboard.getStatusText(anomalyScore);
            const scoreDisplay = anomalyScore !== undefined ? anomalyScore.toFixed(2) : "N/A";

            return `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <span class="status-indicator status-${statusColor}"></span>
                        <strong>Patient ${patient.id || patient.patient_id || 'Unknown'}</strong>
                        <small class="d-block text-muted">${statusText}</small>
                    </div>
                    <div class="text-end">
                        <small class="text-muted">Score: ${scoreDisplay}</small>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    },

    // Update element text content
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    },

    // Handle quick actions
    handleQuickAction(action) {
        switch (action) {
            case 'add-patient':
                window.location.href = '/patients/create';
                break;
            case 'monitoring':
                window.location.href = '/monitoring';
                break;
            case 'analytics':
                window.location.href = '/analytics';
                break;
            case 'manage-users':
                window.location.href = '/auth/admin/users';
                break;
            default:
                console.log('Unknown action:', action);
        }
    },

    // Setup auto-refresh with more frequent updates (fallback if WebSockets not available)
    setupAutoRefresh() {
        // Only set up polling if WebSocket is not connected
        if (this.state.socket && this.state.socket.connected) {
            console.log('WebSocket connected, skipping auto-refresh setup');
            return;
        }
        
        console.log('Setting up fallback polling for updates');
        
        // Set a faster refresh interval for more real-time updates (5 seconds)
        const fastRefreshInterval = 5000; // 5 seconds
        
        // Create different intervals for different components
        this.state.refreshIntervals = {
            // Fast refresh for critical components
            criticalData: setInterval(() => {
                // Load patients and alerts more frequently
                Promise.all([
                    this.loadRecentPatients(),
                    this.loadRecentAlerts()
                ]);
            }, fastRefreshInterval),
            
            // Standard refresh for all data
            allData: setInterval(() => {
                this.loadDashboardData();
            }, HospitalDashboard.config.refreshInterval)
        };
        
        // Create a heartbeat indicator to show real-time updates
        this.setupHeartbeatIndicator();
    },
    
    // Setup heartbeat indicator to show real-time activity
    setupHeartbeatIndicator() {
        // Create a small heartbeat indicator if it doesn't exist
        if (!document.getElementById('realtime-heartbeat')) {
            const updateStatus = document.getElementById('dashboard-update-status');
            if (updateStatus) {
                const heartbeat = document.createElement('span');
                heartbeat.id = 'realtime-heartbeat';
                heartbeat.className = 'ms-1';
                heartbeat.innerHTML = '•';
                updateStatus.appendChild(heartbeat);
                
                // Add connection status indicator next to heartbeat
                const connectionStatus = document.createElement('span');
                connectionStatus.id = 'connection-status-indicator';
                connectionStatus.className = 'connection-indicator ms-2 badge rounded-pill';
                connectionStatus.innerHTML = 'Connecting...';
                updateStatus.parentNode.appendChild(connectionStatus);
                
                // Pulse the heartbeat
                setInterval(() => {
                    heartbeat.classList.add('pulse-dot');
                    setTimeout(() => {
                        heartbeat.classList.remove('pulse-dot');
                    }, 1000);
                }, 2000);
            }
        }
    },
    
    // Update the connection status indicator
    updateConnectionStatus(status) {
        const indicator = document.getElementById('connection-status-indicator');
        if (!indicator) return;
        
        switch(status) {
            case 'connected':
                indicator.className = 'connection-indicator ms-2 badge rounded-pill bg-success';
                indicator.innerHTML = '<i class="bi bi-lightning-fill"></i> Real-time Connected';
                break;
            case 'disconnected':
                indicator.className = 'connection-indicator ms-2 badge rounded-pill bg-danger';
                indicator.innerHTML = '<i class="bi bi-x-circle"></i> Offline';
                break;
            case 'error':
                indicator.className = 'connection-indicator ms-2 badge rounded-pill bg-warning';
                indicator.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Connection Error';
                break;
            case 'reconnecting':
                indicator.className = 'connection-indicator ms-2 badge rounded-pill bg-info';
                indicator.innerHTML = '<i class="bi bi-arrow-repeat"></i> Reconnecting...';
                break;
            default:
                indicator.className = 'connection-indicator ms-2 badge rounded-pill bg-secondary';
                indicator.innerHTML = '<i class="bi bi-question-circle"></i> Unknown';
        }
    },

    // Cleanup
    cleanup() {
        // Clear all intervals
        if (this.state.refreshIntervals) {
            Object.values(this.state.refreshIntervals).forEach(interval => {
                if (interval) clearInterval(interval);
            });
        }
        
        if (this.state.timestampInterval) {
            clearInterval(this.state.timestampInterval);
        }
        
        // Clear charts
        Object.values(this.state.charts).forEach(chart => {
            ChartUtils.destroyChart(chart);
        });
        
        this.state.charts = {};
    },
    
    // Setup WebSocket after Socket.IO is dynamically loaded
    setupWebSocketAfterLoad: function() {
        try {
            console.log('🔄 Setting up WebSocket connection after dynamic load...');
            
            // Connect to the server
            const socketUrl = window.location.protocol + '//' + window.location.host;
            console.log(`🔌 Connecting to WebSocket at ${socketUrl}`);
            
            // Create socket with detailed logging and debug options
            this.state.socket = io(socketUrl, { 
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: Infinity,
                timeout: 20000,
                transports: ['websocket', 'polling'],
                forceNew: true,
                debug: true
            });
            
            // Setup all the same event handlers as in the main setupWebSocket method
            this.state.socket.on('connect', () => {
                const socketId = this.state.socket.id || 'Unknown';
                console.log('✅ WebSocket connected after dynamic load!', socketId);
                this.showConnectionStatus('connected');
                this.createConsoleNotification(`WebSocket connected! Socket ID: ${socketId}`, 'success');
                
                const transport = this.state.socket.io.engine.transport.name;
                console.log(`🔌 Using transport: ${transport}`);
                this.createConsoleNotification(`Connected using: ${transport}`, 'info');
                
                this.state.socket.emit('request_initial_data');
                this.testPrometheusConnection();
                this.startPingTest();
            });
            
            // Copy the rest of the event handlers from setupWebSocket
            this.state.socket.on('disconnect', (reason) => {
                console.log(`🔴 WebSocket disconnected: ${reason}`);
                this.showConnectionStatus('disconnected');
                this.createConsoleNotification(`WebSocket disconnected: ${reason}`, 'error');
                this.setupAutoRefresh();
                if (this.state.pingInterval) {
                    clearInterval(this.state.pingInterval);
                    this.state.pingInterval = null;
                }
            });
            
            // Add all other event handlers from the original setupWebSocket method
            this.state.socket.on('connect_error', (error) => {
                console.error('❌ WebSocket connection error:', error);
                this.showConnectionStatus('error');
                this.createConsoleNotification(`Connection error: ${error.message}`, 'error');
                this.logConnectionDetails();
            });
            
            this.state.socket.on('reconnect_attempt', (attemptNumber) => {
                console.log(`🔄 WebSocket reconnection attempt ${attemptNumber}`);
                this.showConnectionStatus('reconnecting');
                this.createConsoleNotification(`Reconnection attempt ${attemptNumber}...`, 'warning');
                if (attemptNumber > 3) {
                    this.logConnectionDetails();
                }
            });
            
            this.state.socket.on('reconnect', (attemptNumber) => {
                console.log(`✅ WebSocket reconnected after ${attemptNumber} attempts`);
                this.showConnectionStatus('connected');
                this.createConsoleNotification(`Reconnected after ${attemptNumber} attempts`, 'success');
                this.testPrometheusConnection();
            });
            
            this.state.socket.on('error', (error) => {
                console.error('❌ WebSocket error:', error);
                this.createConsoleNotification(`WebSocket error: ${error}`, 'error');
                if (this.state.socket && this.state.socket.connected) {
                    this.state.socket.emit('client_log', {
                        type: 'error',
                        message: `WebSocket error: ${error}`
                    });
                }
            });
            
            // Listen for dashboard data updates
            this.state.socket.on('dashboard_stats', (data) => {
                console.log('📈 Received dashboard stats update [Source: WebSocket Dynamic Load]:', data);
                if (!data) {
                    console.error('❌ Received empty dashboard stats data');
                    this.createConsoleNotification('Received empty dashboard stats data', 'warning');
                    return;
                }
                try {
                    this.updateDashboardStatsFromWebSocket(data);
                    this.updateLastUpdatedTimestamp();
                } catch (error) {
                    console.error('❌ Error processing dashboard stats:', error);
                    this.createConsoleNotification(`Error processing stats: ${error.message}`, 'error');
                }
            });
            
            this.state.socket.on('patients_update', (data) => {
                console.log('👥 Received patients update [Source: WebSocket Dynamic Load]:', data);
                if (!data || !data.patients) {
                    console.error('❌ Received invalid patients data');
                    this.createConsoleNotification('Received invalid patients data', 'warning');
                    return;
                }
                try {
                    this.updateRecentPatientsFromWebSocket(data.patients);
                    this.updateLastUpdatedTimestamp();
                } catch (error) {
                    console.error('❌ Error processing patients update:', error);
                    this.createConsoleNotification(`Error processing patients: ${error.message}`, 'error');
                }
            });
            
            this.state.socket.on('system_status', (data) => {
                console.log('🖥️ Received system status update [Source: WebSocket Dynamic Load]:', data);
                if (!data || !data.system_status) {
                    console.error('❌ Received invalid system status data');
                    this.createConsoleNotification('Received invalid system status data', 'warning');
                    return;
                }
                try {
                    this.updateSystemStatus(data.system_status);
                    this.updateLastUpdatedTimestamp();
                } catch (error) {
                    console.error('❌ Error processing system status:', error);
                    this.createConsoleNotification(`Error processing status: ${error.message}`, 'error');
                }
            });
            
            this.state.socket.on('alerts_update', (data) => {
                console.log('🚨 Received alerts update [Source: WebSocket Dynamic Load]:', data);
                if (!data || !data.alerts) {
                    console.error('❌ Received invalid alerts data');
                    this.createConsoleNotification('Received invalid alerts data', 'warning');
                    return;
                }
                try {
                    this.updateRecentAlerts(data.alerts);
                    this.updateLastUpdatedTimestamp();
                } catch (error) {
                    console.error('❌ Error processing alerts update:', error);
                    this.createConsoleNotification(`Error processing alerts: ${error.message}`, 'error');
                }
            });
            
            // Handle Prometheus errors
            this.state.socket.on('prometheus_error', (data) => {
                console.error('🔴 Prometheus error:', data);
                this.createConsoleNotification(`Prometheus error: ${data.message}`, 'error');
                this.showPrometheusError(data.message);
            });
            
            // Handle server messages
            this.state.socket.on('dashboard_message', (data) => {
                console.log('📝 Dashboard message:', data);
                this.createConsoleNotification(data.message, data.type || 'info');
            });
            
            // Handle connection info from server
            this.state.socket.on('connection_info', (data) => {
                console.log('ℹ️ Connection info:', data);
                this.state.connectionInfo = data;
                console.log(`🔌 Connected to server: ${data.socket_id}`);
                console.log(`⏱️ Server time: ${data.server_time}`);
                console.log(`🔗 Prometheus URL: ${data.prometheus_url}`);
            });
            
            // Handle ping response for latency calculation
            this.state.socket.on('pong_response', (data) => {
                const roundTripTime = Date.now() - data.client_timestamp;
                console.log(`🏓 WebSocket ping: ${roundTripTime}ms`);
                this.state.latency = roundTripTime;
                this.updateLatencyIndicator(roundTripTime);
                if (roundTripTime > 500) {
                    this.createConsoleNotification(`High latency detected: ${roundTripTime}ms`, 'warning');
                }
            });
            
            // Handle Prometheus status check response
            this.state.socket.on('prometheus_status', (data) => {
                console.log('📊 Prometheus status:', data);
                if (data.status === 'healthy') {
                    this.createConsoleNotification(`Prometheus is healthy (${data.latency_ms}ms)`, 'success');
                    this.clearPrometheusError();
                } else {
                    this.createConsoleNotification(`Prometheus is ${data.status}: ${data.error || 'Unknown issue'}`, 'error');
                    this.showPrometheusError(data.error || `Status: ${data.status}`);
                }
            });
            
        } catch (error) {
            console.error('❌ Error setting up WebSocket after dynamic load:', error);
            this.createConsoleNotification(`Failed to setup WebSocket: ${error.message}`, 'error');
            this.setupAutoRefresh(); // Fall back to polling if WebSocket setup fails
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the dashboard page
    if (document.getElementById('total-patients')) {
        DashboardModule.init();
    }
});

// Export for global access
window.DashboardModule = DashboardModule;