// Core JavaScript utilities for the Hospital Monitoring Dashboard

// ===== CORE UTILITIES =====
const HospitalDashboard = {
    // Configuration
    config: {
        refreshInterval: 10000, // 10 seconds for full refresh (faster for real-time updates)
        chartUpdateInterval: 3000, // 3 seconds for chart updates
        criticalDataInterval: 5000, // 5 seconds for critical data
        apiEndpoints: {
            metrics: '/api/metrics',
            patients: '/api/patients',
            patient: '/api/patients',
            systemStatus: '/api/system-status',
            alerts: '/api/recent-alerts'
        }
    },

    // Global state
    state: {
        currentPatient: null,
        charts: {},
        intervals: {},
        isOnline: navigator.onLine
    },

    // Initialize the dashboard
    init: function() {
        this.setupEventListeners();
        this.setupNetworkStatus();
        this.setupErrorHandling();
        console.log('Hospital Dashboard initialized');
    },

    // Setup global event listeners
    setupEventListeners: function() {
        // Network status
        window.addEventListener('online', () => {
            this.state.isOnline = true;
            this.showNotification('Connection restored', 'success');
            this.refreshAllData();
        });

        window.addEventListener('offline', () => {
            this.state.isOnline = false;
            this.showNotification('Connection lost', 'warning');
        });

        // Global error handling
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showNotification('An error occurred', 'danger');
        });

        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showNotification('An error occurred', 'danger');
        });
    },

    // Setup network status monitoring
    setupNetworkStatus: function() {
        const statusIndicator = document.getElementById('network-status');
        if (statusIndicator) {
            setInterval(() => {
                statusIndicator.className = this.state.isOnline ? 
                    'badge bg-success' : 'badge bg-danger';
                statusIndicator.textContent = this.state.isOnline ? 
                    'Online' : 'Offline';
            }, 1000);
        }
    },

    // Setup error handling
    setupErrorHandling: function() {
        // Override console.error to also show notifications
        const originalError = console.error;
        console.error = (...args) => {
            originalError.apply(console, args);
            if (args[0] && typeof args[0] === 'string' && args[0].includes('Error')) {
                this.showNotification('An error occurred', 'danger');
            }
        };
    },

    // API request wrapper with error handling
    apiRequest: async function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return { success: true, data };
        } catch (error) {
            console.error(`API request failed for ${url}:`, error);
            return { success: false, error: error.message };
        }
    },

    // Show notification
    showNotification: function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    },

    // Format timestamp
    formatTimestamp: function(timestamp) {
        if (!timestamp) return 'N/A';
        const date = new Date(timestamp);
        return date.toLocaleString();
    },

    // Format relative time
    formatRelativeTime: function(timestamp) {
        if (!timestamp) return 'N/A';
        const now = new Date();
        const date = new Date(timestamp);
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Refresh all data
    refreshAllData: function() {
        if (!this.state.isOnline) return;

        // Trigger custom event for components to refresh
        document.dispatchEvent(new CustomEvent('dashboard:refresh'));
    },

    // Set up auto-refresh
    setupAutoRefresh: function(interval = this.config.refreshInterval) {
        if (this.state.intervals.autoRefresh) {
            clearInterval(this.state.intervals.autoRefresh);
        }

        this.state.intervals.autoRefresh = setInterval(() => {
            this.refreshAllData();
        }, interval);
    },

    // Clean up intervals
    cleanup: function() {
        Object.values(this.state.intervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });
        this.state.intervals = {};
    },

    // Get patient status color
    getStatusColor: function(anomalyScore) {
        // Handle undefined, null or NaN values
        if (anomalyScore === undefined || anomalyScore === null || isNaN(anomalyScore)) {
            return 'secondary';
        }
        
        if (anomalyScore > 0.7) return 'danger';
        if (anomalyScore > 0.4) return 'warning';
        return 'success';
    },

    // Get patient status text
    getStatusText: function(anomalyScore) {
        // Handle undefined, null or NaN values
        if (anomalyScore === undefined || anomalyScore === null || isNaN(anomalyScore)) {
            return 'Unknown';
        }
        
        if (anomalyScore > 0.7) return 'Critical';
        if (anomalyScore > 0.4) return 'Warning';
        return 'Normal';
    },

    // Validate vital sign
    validateVital: function(value, type) {
        // Handle null, undefined, or NaN values
        if (value === null || value === undefined || isNaN(value)) {
            return 'unknown';
        }

        const ranges = {
            heart_rate: { min: 30, max: 200 },
            temperature: { min: 30, max: 45 },
            bp_systolic: { min: 60, max: 250 },
            bp_diastolic: { min: 40, max: 150 },
            respiratory_rate: { min: 5, max: 50 },
            spo2: { min: 70, max: 100 },
            etco2: { min: 20, max: 60 },
            wbc_count: { min: 2, max: 20 },
            lactate: { min: 0, max: 10 },
            blood_glucose: { min: 50, max: 400 }
        };

        const range = ranges[type];
        if (!range) return 'normal';

        // Convert value to number just in case
        const numValue = parseFloat(value);
        
        if (numValue < range.min || numValue > range.max) return 'critical';
        if (numValue < range.min * 1.1 || numValue > range.max * 0.9) return 'warning';
        return 'normal';
    },

    // Generate random data for testing
    generateMockData: function(patientId, count = 10) {
        const data = [];
        const now = new Date();
        
        for (let i = 0; i < count; i++) {
            const timestamp = new Date(now.getTime() - (i * 5 * 60 * 1000)); // 5 minutes apart
            data.push({
                timestamp: timestamp.toISOString(),
                heart_rate: Math.floor(Math.random() * 40) + 60,
                temperature: (Math.random() * 2 + 36).toFixed(1),
                bp_systolic: Math.floor(Math.random() * 40) + 100,
                bp_diastolic: Math.floor(Math.random() * 20) + 60,
                respiratory_rate: Math.floor(Math.random() * 8) + 12,
                spo2: Math.floor(Math.random() * 10) + 90,
                anomaly_score: Math.random()
            });
        }
        
        return data;
    }
};

// ===== CHART UTILITIES =====
const ChartUtils = {
    // Default chart options
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top'
            }
        },
        scales: {
            x: {
                display: true,
                grid: {
                    display: false
                }
            },
            y: {
                display: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.1)'
                }
            }
        },
        elements: {
            point: {
                radius: 3,
                hoverRadius: 6
            },
            line: {
                tension: 0.3
            }
        }
    },

    // Create a line chart
    createLineChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = {
            type: 'line',
            data: data,
            options: { ...this.defaultOptions, ...options }
        };

        return new Chart(ctx, config);
    },

    // Create a bar chart
    createBarChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = {
            type: 'bar',
            data: data,
            options: { ...this.defaultOptions, ...options }
        };

        return new Chart(ctx, config);
    },

    // Create a doughnut chart
    createDoughnutChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                ...options
            }
        };

        return new Chart(ctx, config);
    },

    // Update chart data
    updateChart: function(chart, newData) {
        if (!chart) return;
        
        chart.data = newData;
        chart.update('none'); // No animation for real-time updates
    },

    // Destroy chart
    destroyChart: function(chart) {
        if (chart) {
            chart.destroy();
        }
    }
};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    HospitalDashboard.init();
});

// Export for use in other modules
window.HospitalDashboard = HospitalDashboard;
window.ChartUtils = ChartUtils;
