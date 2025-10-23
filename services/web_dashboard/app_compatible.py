from flask import Flask, render_template, jsonify
import json
import time
import os
from datetime import datetime
import logging

# Enable logging for debug
logging.basicConfig(level=logging.DEBUG)

# Create a simple Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key'

# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Routes
@app.route('/')
def index():
    return "WebSocket Test App - Compatible Version"

@app.route('/test')
def test_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .card { background: #f9f9f9; border-radius: 5px; padding: 15px; margin-bottom: 15px; }
            .normal { background-color: #d4edda; }
            .warning { background-color: #fff3cd; }
            .critical { background-color: #f8d7da; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 5px 0; padding: 10px; border-radius: 4px; }
            button { padding: 10px 15px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Dashboard Test</h1>
        
        <div class="card">
            <h2>Patient Statistics</h2>
            <p>Total Patients: <span id="total-patients">15</span></p>
            <p>Normal: <span id="normal-patients">8</span></p>
            <p>Warning: <span id="warning-patients">5</span></p>
            <p>Critical: <span id="critical-patients">2</span></p>
        </div>
        
        <div class="card">
            <h2>Patient List</h2>
            <ul id="patient-list">
                <!-- Test patients will be displayed here -->
            </ul>
        </div>
        
        <button onclick="loadTestPatients()">Load Test Patients</button>
        
        <script>
            function loadTestPatients() {
                // Generate 15 test patients
                const patients = [];
                
                for (let i = 1; i <= 15; i++) {
                    const anomalyScore = Math.random();
                    let status = "Normal";
                    
                    if (anomalyScore > 0.7) {
                        status = "Critical";
                    } else if (anomalyScore > 0.4) {
                        status = "Warning";
                    }
                    
                    patients.push({
                        patient_id: `patient-${i}`,
                        anomaly_score: anomalyScore.toFixed(2),
                        heart_rate: Math.floor(60 + Math.random() * 60),
                        status: status
                    });
                }
                
                // Update statistics
                const normalPatients = patients.filter(p => p.status === "Normal").length;
                const warningPatients = patients.filter(p => p.status === "Warning").length;
                const criticalPatients = patients.filter(p => p.status === "Critical").length;
                
                document.getElementById("total-patients").textContent = patients.length;
                document.getElementById("normal-patients").textContent = normalPatients;
                document.getElementById("warning-patients").textContent = warningPatients;
                document.getElementById("critical-patients").textContent = criticalPatients;
                
                // Display patient list
                const patientList = document.getElementById("patient-list");
                patientList.innerHTML = "";
                
                patients.forEach(patient => {
                    const li = document.createElement("li");
                    li.className = patient.status.toLowerCase();
                    li.innerHTML = `
                        <strong>ID:</strong> ${patient.patient_id} | 
                        <strong>Status:</strong> ${patient.status} |
                        <strong>Heart Rate:</strong> ${patient.heart_rate} bpm |
                        <strong>Anomaly Score:</strong> ${patient.anomaly_score}
                    `;
                    patientList.appendChild(li);
                });
            }
            
            // Load test patients when page loads
            window.addEventListener('load', loadTestPatients);
        </script>
    </body>
    </html>
    """

@app.route('/api/patients')
def get_patients():
    """Generate test patient data"""
    import random
    
    test_data = []
    
    # Generate 15 test patients
    for i in range(1, 16):
        anomaly_score = round(random.uniform(0, 1), 2)
        heart_rate = round(random.uniform(60, 120))
        
        status = "Normal"
        if anomaly_score > 0.7:
            status = "Critical"
        elif anomaly_score > 0.4:
            status = "Warning"
            
        test_data.append({
            "patient_id": f"test-patient-{i}",
            "anomaly_score": anomaly_score,
            "heart_rate": heart_rate,
            "status": status
        })
    
    normal_count = sum(1 for p in test_data if p["status"] == "Normal")
    warning_count = sum(1 for p in test_data if p["status"] == "Warning")
    critical_count = sum(1 for p in test_data if p["status"] == "Critical")
    
    return jsonify({
        "status": "success",
        "data": {
            "patients": test_data,
            "total_patients": len(test_data),
            "normal_patients": normal_count,
            "warning_patients": warning_count,
            "critical_patients": critical_count
        }
    })

if __name__ == '__main__':
    print("Starting compatible test server...")
    app.run(host='0.0.0.0', port=5000, debug=True)