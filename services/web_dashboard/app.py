from flask import Flask, render_template, jsonify, request, send_file
import requests
import os
import json
from datetime import datetime
import io
import time
import random

app = Flask(__name__)

# Configuration
MAIN_HOST_URL = os.environ.get('MAIN_HOST_URL', 'http://main_host:8000')
ML_SERVICE_URL = os.environ.get('ML_SERVICE_URL', 'http://ml_service:6000')
PROMETHEUS_URL = os.environ.get('PROMETHEUS_URL', 'http://prometheus:9090')
GRAFANA_URL = os.environ.get('GRAFANA_URL', 'http://grafana:3000')
ALERTMANAGER_URL = os.environ.get('ALERTMANAGER_URL', 'http://alertmanager:9093')

# In-memory cache for system status
system_status = {
    'main_host': {'status': 'online', 'uptime': '0 days, 0 hours', 'last_check': time.time()},
    'ml_service': {'status': 'online', 'uptime': '0 days, 0 hours', 'last_check': time.time()},
    'patient_simulator': {'status': 'online', 'uptime': '0 days, 0 hours', 'last_check': time.time()},
    'grafana': {'status': 'online', 'uptime': '0 days, 0 hours', 'last_check': time.time()},
    'prometheus': {'status': 'online', 'uptime': '0 days, 0 hours', 'last_check': time.time()},
    'alertmanager': {'status': 'online', 'uptime': '0 days, 0 hours', 'last_check': time.time()},
}

# In-memory cache for recent alerts
recent_alerts = []

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/patients')
def patients():
    """Patient monitoring page"""
    return render_template('patients.html')

@app.route('/analytics')
def analytics():
    """Analytics and visualization page"""
    return render_template('analytics.html')

@app.route('/api/patients')
def get_patients():
    """Get list of all patients"""
    try:
        # Query the main_host for a list of patients
        response = requests.get(f"{MAIN_HOST_URL}/api/patients")
        return response.json()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/patient/<patient_id>')
def get_patient_data(patient_id):
    """Get data for a specific patient"""
    try:
        # Query the main_host for data for the specified patient
        response = requests.get(f"{MAIN_HOST_URL}/api/patient/{patient_id}")
        return response.json()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/metrics')
def get_metrics():
    """Get latest metrics from main_host"""
    try:
        # Query the main_host for dashboard data
        response = requests.get(f"{MAIN_HOST_URL}/api/dashboard-data")
        return response.json()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/monitoring')
def monitoring():
    """Monitoring integration page"""
    return render_template('monitoring.html')

@app.route('/api/monitoring-urls')
def get_monitoring_urls():
    """Get URLs for monitoring services"""
    try:
        # Return URLs for Prometheus, Grafana, and AlertManager
        return jsonify({
            "status": "success",
            "urls": {
                "prometheus": PROMETHEUS_URL,
                "grafana": GRAFANA_URL,
                "alertmanager": ALERTMANAGER_URL
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/simulate/<patient_id>')
def simulate_patient(patient_id):
    """Trigger a simulation for a specific patient"""
    try:
        # In a real implementation, this would trigger the patient_simulator
        # For now, we'll just return a success message
        return jsonify({"status": "success", "message": f"Simulation triggered for patient {patient_id}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/grafana-preview')
def get_grafana_preview():
    """Get a preview image of the Grafana dashboard
    
    In a real implementation, this would:
    1. Take a screenshot of the Grafana dashboard using Selenium or another tool
    2. Cache the image for a period of time to avoid overloading Grafana
    3. Return the image
    
    For this example, we'll use a simple text response since we can't generate an image without PIL
    """
    try:
        return jsonify({
            "status": "success",
            "message": "Preview generation requires additional libraries (PIL). In a production environment, this would return an actual screenshot of the Grafana dashboard.",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/system-status')
def get_system_status():
    """Get the current status of all services
    
    In a real implementation, this would:
    1. Query Prometheus for the status of each service
    2. Calculate uptime based on metrics
    3. Return the status for display
    
    For this example, we'll simulate this by updating our in-memory cache
    """
    try:
        # Update the simulated system status
        for service in system_status:
            # In a real implementation, this would check if the service is actually online
            current_time = time.time()
            elapsed_time = current_time - system_status[service]['last_check']
            
            # Convert uptime string to seconds, add elapsed time, and convert back
            uptime_parts = system_status[service]['uptime'].split(', ')
            days = int(uptime_parts[0].split()[0])
            hours = int(uptime_parts[1].split()[0])
            
            total_hours = days * 24 + hours + elapsed_time / 3600
            new_days = int(total_hours / 24)
            new_hours = int(total_hours % 24)
            
            system_status[service]['uptime'] = f"{new_days} days, {new_hours} hours"
            system_status[service]['last_check'] = current_time
            
            # Simulate occasional status changes for demo purposes
            if random.random() < 0.05:  # 5% chance of status change
                system_status[service]['status'] = random.choice(['online', 'warning', 'offline'])
        
        return jsonify({
            "status": "success",
            "system_status": system_status
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/recent-alerts')
def get_recent_alerts():
    """Get recent alerts from AlertManager
    
    In a real implementation, this would:
    1. Query AlertManager for recent alerts
    2. Format the alerts for display
    3. Return the alerts
    
    For this example, we'll simulate this by generating random alerts
    """
    try:
        # Generate some simulated alerts if our cache is empty
        if not recent_alerts:
            # Simulate 3-5 random alerts
            num_alerts = random.randint(3, 5)
            alert_types = [
                {"level": "warning", "message": "Patient {} has anomaly score above threshold ({:.4f})"},
                {"level": "danger", "message": "Patient {} showing respiratory rate above normal range ({})"},
                {"level": "warning", "message": "Patient {} has blood pressure below normal range ({} diastolic)"},
                {"level": "danger", "message": "Patient {} temperature spike detected ({:.1f}°C)"},
                {"level": "warning", "message": "Patient {} heart rate below normal range ({} BPM)"}
            ]
            
            for _ in range(num_alerts):
                alert_type = random.choice(alert_types)
                patient_id = random.randint(1, 15)
                value = random.uniform(0.8, 1.2) if "anomaly" in alert_type["message"] else random.randint(30, 180)
                
                # Generate a random timestamp in the last 24 hours
                hours_ago = random.uniform(0, 24)
                timestamp = datetime.now().timestamp() - (hours_ago * 3600)
                alert_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                recent_alerts.append({
                    "level": alert_type["level"],
                    "message": alert_type["message"].format(patient_id, value),
                    "timestamp": alert_time
                })
            
            # Sort by timestamp (most recent first)
            recent_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return jsonify({
            "status": "success",
            "alerts": recent_alerts
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)