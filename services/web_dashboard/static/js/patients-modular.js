// Modular Patients JavaScript for Hospital Dashboard

const PatientsModule = {
    // State
    state: {
        currentPatient: null,
        patientList: [],
        charts: {},
        refreshInterval: null
    },

    // Initialize the patients module
    init: function() {
        this.setupEventListeners();
        this.loadPatientList();
        this.setupAutoRefresh();
        console.log('Patients module initialized');
    },

    // Setup event listeners
    setupEventListeners: function() {
        // Patient selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.patient-list-item')) {
                const patientId = e.target.closest('.patient-list-item').dataset.patientId;
                this.selectPatient(patientId);
            }
        });

        // Search functionality
        const searchInput = document.getElementById('patientSearch');
        if (searchInput) {
            searchInput.addEventListener('input', HospitalDashboard.debounce((e) => {
                this.filterPatients(e.target.value);
            }, 300));
        }

        // Refresh button
        const refreshButton = document.getElementById('refreshButton');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.refreshPatientList();
            });
        }

        // Global refresh event
        document.addEventListener('dashboard:refresh', () => {
            this.refreshPatientList();
        });
    },

    // Load patient list
    async loadPatientList() {
        const result = await HospitalDashboard.apiRequest(HospitalDashboard.config.apiEndpoints.patients);
        
        if (result.success) {
            this.state.patientList = result.data.patients || [];
            this.renderPatientList();
            
            // Auto-select first patient if none selected
            if (!this.state.currentPatient && this.state.patientList.length > 0) {
                this.selectPatient(this.state.patientList[0].id);
            }
        } else {
            HospitalDashboard.showNotification('Failed to load patients', 'danger');
            this.renderPatientList([]);
        }
    },

    // Render patient list
    renderPatientList(patients = this.state.patientList) {
        const container = document.getElementById('patientListGroup');
        if (!container) return;

        if (patients.length === 0) {
            container.innerHTML = `
                <div class="list-group-item text-center py-4">
                    <p class="text-muted">No patients found</p>
                </div>
            `;
            return;
        }

        const html = patients.map(patient => {
            const statusColor = HospitalDashboard.getStatusColor(patient.anomaly_score);
            const statusText = HospitalDashboard.getStatusText(patient.anomaly_score);
            const isActive = this.state.currentPatient === patient.id ? 'active' : '';

            return `
                <div class="list-group-item list-group-item-action patient-list-item ${isActive}" 
                     data-patient-id="${patient.id}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="status-indicator status-${statusColor}"></span>
                            <strong>Patient ${patient.id}</strong>
                            <small class="d-block text-muted">${statusText}</small>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">Score: ${patient.anomaly_score.toFixed(2)}</small>
                            <br>
                            <small class="text-muted">${patient.hospital || 'Unknown'}</small>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    },

    // Filter patients
    filterPatients(searchTerm) {
        if (!searchTerm) {
            this.renderPatientList();
            return;
        }

        const filtered = this.state.patientList.filter(patient => 
            patient.id.toString().includes(searchTerm.toLowerCase()) ||
            (patient.hospital && patient.hospital.toLowerCase().includes(searchTerm.toLowerCase()))
        );

        this.renderPatientList(filtered);
    },

    // Select patient
    async selectPatient(patientId) {
        this.state.currentPatient = patientId;
        
        // Update UI
        document.querySelectorAll('.patient-list-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedItem = document.querySelector(`[data-patient-id="${patientId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }

        // Load patient details
        await this.loadPatientDetails(patientId);
    },

    // Load patient details
    async loadPatientDetails(patientId) {
        const result = await HospitalDashboard.apiRequest(
            `${HospitalDashboard.config.apiEndpoints.patient}/${patientId}`
        );

        if (result.success) {
            this.renderPatientDetails(result.data);
            this.updateCharts(result.data);
        } else {
            this.renderPatientDetails(null, result.error);
        }
    },

    // Render patient details
    renderPatientDetails(patient, error = null) {
        const container = document.getElementById('patientDetails');
        if (!container) return;

        if (error) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error loading patient data</h5>
                    <p>${error}</p>
                    <button class="btn btn-outline-danger btn-sm" onclick="PatientsModule.loadPatientDetails('${this.state.currentPatient}')">
                        <i class="fas fa-sync-alt"></i> Retry
                    </button>
                </div>
            `;
            return;
        }

        if (!patient) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-person-x display-1 text-muted"></i>
                    <p class="text-muted mt-3">No patient data available</p>
                </div>
            `;
            return;
        }

        const statusColor = HospitalDashboard.getStatusColor(patient.anomaly_score);
        const statusText = HospitalDashboard.getStatusText(patient.anomaly_score);

        container.innerHTML = `
            <div class="fade-in">
                <div class="card mb-4">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            ${patient.first_name} ${patient.last_name}
                            <span class="badge bg-${statusColor} float-end">${statusText}</span>
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>MRN:</strong> ${patient.mrn}</p>
                                <p><strong>Age:</strong> ${patient.age}</p>
                                <p><strong>Gender:</strong> ${patient.gender}</p>
                                <p><strong>Blood Type:</strong> ${patient.blood_type}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Department:</strong> ${patient.department}</p>
                                <p><strong>Room:</strong> ${patient.room}</p>
                                <p><strong>Anomaly Score:</strong></p>
                                <div class="progress" style="height: 25px;">
                                    <div class="progress-bar bg-${statusColor}" 
                                         style="width: ${patient.anomaly_score * 100}%">
                                        ${(patient.anomaly_score * 100).toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    ${this.renderVitalSigns(patient)}
                </div>

                <div class="row mt-4">
                    <div class="col-12">
                        <div class="chart-container">
                            <canvas id="patientVitalsChart" height="300"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // Render vital signs
    renderVitalSigns(patient) {
        const vitals = [
            { key: 'heart_rate', label: 'Heart Rate', unit: 'bpm', value: patient.heart_rate },
            { key: 'temperature', label: 'Temperature', unit: '°C', value: patient.temperature },
            { key: 'respiratory_rate', label: 'Respiratory Rate', unit: 'breaths/min', value: patient.respiratory_rate },
            { key: 'oxygen_saturation', label: 'Oxygen Saturation', unit: '%', value: patient.oxygen_saturation }
        ];

        return vitals.map(vital => {
            const status = HospitalDashboard.validateVital(vital.value, vital.key);
            const statusClass = status === 'critical' ? 'danger' : status === 'warning' ? 'warning' : 'success';

            return `
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="vital-card">
                        <div class="vital-label">${vital.label}</div>
                        <div class="vital-value text-${statusClass}">
                            ${vital.value} <span class="vital-unit">${vital.unit}</span>
                        </div>
                        <div class="text-center">
                            <span class="badge bg-${statusClass}">${status.toUpperCase()}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // Update charts
    updateCharts(patient) {
        // Destroy existing chart
        if (this.state.charts.vitals) {
            ChartUtils.destroyChart(this.state.charts.vitals);
        }

        // Generate mock time-series data
        const mockData = HospitalDashboard.generateMockData(patient.id, 20);
        
        const chartData = {
            labels: mockData.map(d => new Date(d.timestamp).toLocaleTimeString()),
            datasets: [
                {
                    label: 'Heart Rate',
                    data: mockData.map(d => d.heart_rate),
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.3
                },
                {
                    label: 'Temperature',
                    data: mockData.map(d => d.temperature),
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.3,
                    yAxisID: 'y1'
                }
            ]
        };

        const chartOptions = {
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Heart Rate (bpm)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Patient Vital Signs Trend'
                }
            }
        };

        this.state.charts.vitals = ChartUtils.createLineChart('patientVitalsChart', chartData, chartOptions);
    },

    // Refresh patient list
    async refreshPatientList() {
        const refreshIndicator = document.getElementById('refreshIndicator');
        if (refreshIndicator) {
            refreshIndicator.classList.remove('d-none');
        }

        try {
            await this.loadPatientList();
            
            // Update last refreshed time
            const lastRefreshed = document.getElementById('lastRefreshed');
            if (lastRefreshed) {
                lastRefreshed.textContent = new Date().toLocaleTimeString();
            }
        } finally {
            if (refreshIndicator) {
                refreshIndicator.classList.add('d-none');
            }
        }
    },

    // Setup auto-refresh
    setupAutoRefresh() {
        this.state.refreshInterval = setInterval(() => {
            this.refreshPatientList();
        }, HospitalDashboard.config.refreshInterval);
    },

    // Cleanup
    cleanup() {
        if (this.state.refreshInterval) {
            clearInterval(this.state.refreshInterval);
        }
        
        Object.values(this.state.charts).forEach(chart => {
            ChartUtils.destroyChart(chart);
        });
        
        this.state.charts = {};
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on a patients page
    if (document.getElementById('patientListGroup')) {
        PatientsModule.init();
    }
});

// Export for global access
window.PatientsModule = PatientsModule;
