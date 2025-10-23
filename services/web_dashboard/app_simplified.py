"""
This is a simplified version of the dashboard app that works with newer versions of Flask.
It removes dependencies that cause compatibility errors but maintains the core functionality.
"""

from flask import Flask, render_template, jsonify, request
import requests
import os
import json
from datetime import datetime
import time
import random
import threading

app = Flask(__name__)

# Check if we're running in Docker or on the host
in_docker = os.path.exists('/.dockerenv')  # This file exists in Docker containers

if in_docker:
    # Use container names when inside Docker
    MAIN_HOST_URL = os.environ.get('MAIN_HOST_URL', 'http://main_host:8000')
    ML_SERVICE_URL = os.environ.get('ML_SERVICE_URL', 'http://ml_service:6000')
    PROMETHEUS_URL = os.environ.get('PROMETHEUS_URL', 'http://prometheus:9090')
    GRAFANA_URL = os.environ.get('GRAFANA_URL', 'http://grafana:3000')
    ALERTMANAGER_URL = os.environ.get('ALERTMANAGER_URL', 'http://alertmanager:9093')
    print("Running in Docker environment - using container hostnames")
else:
    # Use localhost with mapped ports when on the host machine
    MAIN_HOST_URL = os.environ.get('PUBLIC_MAIN_HOST_URL', 'http://localhost:8000')
    ML_SERVICE_URL = os.environ.get('PUBLIC_ML_SERVICE_URL', 'http://localhost:6000')
    PROMETHEUS_URL = os.environ.get('PUBLIC_PROMETHEUS_URL', 'http://localhost:9090')
    GRAFANA_URL = os.environ.get('PUBLIC_GRAFANA_URL', 'http://localhost:3001')  # Note different port mapping
    ALERTMANAGER_URL = os.environ.get('PUBLIC_ALERTMANAGER_URL', 'http://localhost:9093')
    print("Running on host machine - using localhost URLs")

# Set up CSP headers for security
@app.after_request
def add_security_headers(response):
    # Add Content Security Policy to allow WebSocket connections and localhost resources
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:*; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:* http://127.0.0.1:* "
        "https://cdn.socket.io/ https://cdn.jsdelivr.net/ https://code.jquery.com/ https://cdn.socket.io/ "
        "https://cdn.jsdelivr.net/npm/chart.js https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net/ https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/; "
        "font-src 'self' https://cdn.jsdelivr.net/ data:; "
        "img-src 'self' data:; "
        "frame-src 'self' http://localhost:* http://127.0.0.1:*; "
        "child-src 'self' http://localhost:* http://127.0.0.1:*; "
        "connect-src 'self' http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:* "
        "wss://localhost:* wss://127.0.0.1:*;"
    )
    return response

# Prometheus query functions
def query_prometheus(query):
    """Query Prometheus for metrics"""
    start_time = time.time()
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [DATA SOURCE: PROMETHEUS] Querying: {query}")
        print(f"[{timestamp}] [URL] {PROMETHEUS_URL}/api/v1/query?query={query}")
        
        # Set a timeout to avoid hanging requests
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=5  # 5 second timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "success" and result["data"]["resultType"] == "vector":
                query_time = time.time() - start_time
                result_count = len(result["data"]["result"])
                print(f"[{timestamp}] [DATA RECEIVED] Prometheus query completed in {query_time:.2f}s: {result_count} results")
                
                # Log a sample of data received (first result only to avoid flooding console)
                if result_count > 0 and "result" in result["data"] and len(result["data"]["result"]) > 0:
                    sample = result["data"]["result"][0]
                    print(f"[{timestamp}] [SAMPLE DATA] {json.dumps(sample)[:200]}..." if len(json.dumps(sample)) > 200 else json.dumps(sample))
                
                return result["data"]["result"]
            else:
                print(f"[{timestamp}] [WARNING] Prometheus query returned unexpected format: {result['status']} - {result.get('data', {}).get('resultType', 'unknown')}")
        else:
            print(f"[{timestamp}] [ERROR] Prometheus query failed with status code: {response.status_code}")
            print(f"[{timestamp}] [ERROR] Response: {response.text[:200]}...")  # Truncate long responses
            
        return []
    except requests.exceptions.Timeout:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [TIMEOUT] Prometheus query timed out after 5s: {query}")
        return []
    except requests.exceptions.ConnectionError as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [CONNECTION ERROR] Prometheus connection error: {e}")
        return []
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [ERROR] Error querying Prometheus: {str(e)}")
        return []

def get_patient_metrics_from_prometheus():
    """Get patient metrics from Prometheus"""
    metrics = {}
    start_time = time.time()
    
    try:
        print("📊 Gathering patient metrics from Prometheus")
        
        # Get patient count - this is the most critical query
        patient_count_result = query_prometheus("count(patient_heart_rate)")
        total_patients = 0
        if patient_count_result and len(patient_count_result) > 0:
            total_patients = int(float(patient_count_result[0]["value"][1]))
            print(f"👥 Found {total_patients} patients in Prometheus")
        else:
            print("⚠️ Failed to get patient count from Prometheus")
        
        # Get anomaly scores for patients
        anomaly_scores = query_prometheus("patient_anomaly_score")
        if not anomaly_scores:
            print("⚠️ No patient anomaly scores returned from Prometheus")
            
        patients_data = []
        
        # Process anomaly scores
        normal_count = 0
        warning_count = 0
        critical_count = 0
        
        # Get all heart rates in one query to avoid multiple requests
        all_heart_rates = query_prometheus("patient_heart_rate")
        heart_rate_map = {}
        
        if all_heart_rates:
            for hr_result in all_heart_rates:
                if "metric" in hr_result and "value" in hr_result:
                    patient_id = hr_result["metric"].get("patient", "unknown")
                    heart_rate = float(hr_result["value"][1])
                    heart_rate_map[patient_id] = heart_rate
        
        # Process patient data
        for result in anomaly_scores:
            if "metric" in result and "value" in result:
                try:
                    patient_id = result["metric"].get("patient", "unknown")
                    anomaly_score = float(result["value"][1])
                    
                    # Create patient data
                    patient_data = {
                        "patient_id": patient_id,
                        "anomaly_score": anomaly_score,
                    }
                    
                    # Add heart rate from our pre-fetched map
                    if patient_id in heart_rate_map:
                        patient_data["heart_rate"] = heart_rate_map[patient_id]
                    
                    # Categorize patient status
                    if anomaly_score > 0.7:
                        patient_data["status"] = "Critical"
                        critical_count += 1
                    elif anomaly_score > 0.4:
                        patient_data["status"] = "Warning"
                        warning_count += 1
                    else:
                        patient_data["status"] = "Normal"
                        normal_count += 1
                        
                    patients_data.append(patient_data)
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Error processing patient data: {e}")
                    continue
        
        # If we didn't get any data from Prometheus, generate mock data
        if len(patients_data) == 0:
            print("⚠️ No patient data found in Prometheus, using mock data")
            # Generate mock data
            total_patients = 10
            normal_count = 6
            warning_count = 3
            critical_count = 1
            
            for i in range(1, total_patients + 1):
                if i <= normal_count:
                    status = "Normal"
                    anomaly_score = round(random.uniform(0.1, 0.3), 2)
                elif i <= normal_count + warning_count:
                    status = "Warning"
                    anomaly_score = round(random.uniform(0.5, 0.69), 2)
                else:
                    status = "Critical"
                    anomaly_score = round(random.uniform(0.71, 0.95), 2)
                
                heart_rate = random.randint(60, 100) if status == "Normal" else (
                    random.randint(100, 120) if status == "Warning" else random.randint(120, 180)
                )
                
                patients_data.append({
                    "patient_id": f"MOCK-{i}",
                    "status": status,
                    "anomaly_score": anomaly_score,
                    "heart_rate": heart_rate
                })
            
            print(f"✅ Generated {len(patients_data)} mock patients")
        
        metrics = {
            "patients": patients_data,
            "total_patients": total_patients,
            "normal_patients": normal_count,
            "warning_patients": warning_count,
            "critical_patients": critical_count
        }
        
        query_time = time.time() - start_time
        print(f"✅ Patient metrics collected in {query_time:.2f}s: {len(patients_data)} patients")
        return metrics
        
    except Exception as e:
        print(f"❌ Error gathering patient metrics: {str(e)}")
        # Return a minimal default structure
        return {
            "patients": [],
            "total_patients": 0,
            "normal_patients": 0,
            "warning_patients": 0,
            "critical_patients": 0
        }

# Main route that renders the dashboard
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    print("\n================ DASHBOARD ACCESSED ================")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data sources:")
    print(f"- Prometheus: {PROMETHEUS_URL}")
    print(f"- AlertManager: {ALERTMANAGER_URL}")
    print(f"- Main Host: {MAIN_HOST_URL}")
    print("===================================================\n")
    
    # Try to get metrics from Prometheus for display
    metrics = get_patient_metrics_from_prometheus()
    
    # Pass metrics to the template
    return render_template('dashboard.html', 
                          metrics=metrics,
                          prometheus_url=PROMETHEUS_URL,
                          alertmanager_url=ALERTMANAGER_URL)

# API endpoint to get metrics
@app.route('/api/metrics')
def get_metrics():
    """Get latest metrics from Prometheus"""
    try:
        # Query Prometheus for dashboard data
        metrics = get_patient_metrics_from_prometheus()
        
        return jsonify({
            "status": "success",
            "data": metrics
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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

# Route for debugging service connections
@app.route('/api/debug/check-services')
def check_services():
    """Check if all services are reachable"""
    results = {}
    
    # Check Prometheus
    try:
        start_time = time.time()
        response = requests.get(f"{PROMETHEUS_URL}/-/healthy", timeout=2)
        results["prometheus"] = {
            "status": "online" if response.status_code < 400 else "error",
            "response_time": time.time() - start_time,
            "status_code": response.status_code,
            "url": PROMETHEUS_URL
        }
    except Exception as e:
        results["prometheus"] = {
            "status": "offline",
            "error": str(e),
            "url": PROMETHEUS_URL
        }
    
    # Check AlertManager
    try:
        start_time = time.time()
        response = requests.get(f"{ALERTMANAGER_URL}/-/healthy", timeout=2)
        results["alertmanager"] = {
            "status": "online" if response.status_code < 400 else "error",
            "response_time": time.time() - start_time,
            "status_code": response.status_code,
            "url": ALERTMANAGER_URL
        }
    except Exception as e:
        results["alertmanager"] = {
            "status": "offline",
            "error": str(e),
            "url": ALERTMANAGER_URL
        }
    
    # Check Main Host
    try:
        start_time = time.time()
        response = requests.get(f"{MAIN_HOST_URL}/health", timeout=2)
        results["main_host"] = {
            "status": "online" if response.status_code < 400 else "error",
            "response_time": time.time() - start_time,
            "status_code": response.status_code,
            "url": MAIN_HOST_URL
        }
    except Exception as e:
        results["main_host"] = {
            "status": "offline",
            "error": str(e),
            "url": MAIN_HOST_URL
        }
    
    return jsonify({
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "services": results
    })

@app.route('/api/ping')
def ping():
    """Simple endpoint to test API connectivity"""
    return jsonify({
        "status": "success",
        "message": "Simplified dashboard API is responding",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("\n========== HOSPITAL DASHBOARD (SIMPLIFIED VERSION) ==========")
    print(f"Starting server at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Prometheus URL: {PROMETHEUS_URL}")
    print(f"AlertManager URL: {ALERTMANAGER_URL}")
    print(f"Main Host URL: {MAIN_HOST_URL}")
    print("===========================================================\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)