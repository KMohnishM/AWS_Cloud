"""
Host-Based Data Console - Shows where data is coming from in the web dashboard
This version uses localhost URLs instead of container names to test from the host machine
"""

import os
import requests
import json
from datetime import datetime
import time

def print_header(title):
    """Print a header with a title"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def log(level, message):
    """Print a log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

# Use localhost with mapped ports for services
# These match the port mappings in docker-compose.yml
MAIN_HOST_URL = "http://localhost:8000"  
ML_SERVICE_URL = "http://localhost:6000"
PROMETHEUS_URL = "http://localhost:9090"
GRAFANA_URL = "http://localhost:3001"  # Note Grafana is mapped to 3001 on host
ALERTMANAGER_URL = "http://localhost:9093"

# Database information
DB_PATH = os.path.join('instance', 'healthcare.db')

# Show application header
print_header("WEB DASHBOARD DATA SOURCES (HOST ACCESS)")
print(f"Time: {datetime.now()}")
print("This script checks connectivity to services from your host machine")

# Show data sources
print_header("DATA SOURCES CONFIGURATION (MAPPED TO HOST)")
log("INFO", f"Main Host API:      {MAIN_HOST_URL}")
log("INFO", f"ML Service API:     {ML_SERVICE_URL}")
log("INFO", f"Prometheus:         {PROMETHEUS_URL}")
log("INFO", f"Grafana:            {GRAFANA_URL}")
log("INFO", f"AlertManager:       {ALERTMANAGER_URL}")
log("INFO", f"SQLite Database:    {DB_PATH}")

# Test connections if possible
print_header("CONNECTION TESTS")

# Test Prometheus
try:
    log("INFO", f"Testing connection to Prometheus ({PROMETHEUS_URL})...")
    start_time = time.time()
    response = requests.get(f"{PROMETHEUS_URL}/-/healthy", timeout=2)
    duration = time.time() - start_time
    
    if response.status_code < 400:
        log("SUCCESS", f"Prometheus is AVAILABLE (Status: {response.status_code}, Response time: {duration:.2f}s)")
        
        # Try to get a sample query
        log("INFO", "Running sample Prometheus query...")
        query_response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": "patient_heart_rate"},
            timeout=3
        )
        
        if query_response.status_code == 200:
            result = query_response.json()
            if result["status"] == "success" and "data" in result:
                result_count = len(result["data"].get("result", []))
                log("SUCCESS", f"Query returned {result_count} results")
                
                # Show a sample of the data if available
                if result_count > 0 and "result" in result["data"] and len(result["data"]["result"]) > 0:
                    sample = result["data"]["result"][0]
                    log("SAMPLE", json.dumps(sample, indent=2))
            else:
                log("WARNING", f"Prometheus query returned non-success status: {result.get('status')}")
        else:
            log("ERROR", f"Prometheus query failed with status code: {query_response.status_code}")
    else:
        log("ERROR", f"Prometheus returned error status {response.status_code}")
except requests.exceptions.ConnectionError:
    log("ERROR", "Prometheus is UNREACHABLE - Connection refused")
except requests.exceptions.Timeout:
    log("ERROR", "Prometheus connection TIMEOUT")
except Exception as e:
    log("ERROR", f"Error testing Prometheus: {str(e)}")

# Test AlertManager
try:
    log("INFO", f"Testing connection to AlertManager ({ALERTMANAGER_URL})...")
    start_time = time.time()
    response = requests.get(f"{ALERTMANAGER_URL}/-/healthy", timeout=2)
    duration = time.time() - start_time
    
    if response.status_code < 400:
        log("SUCCESS", f"AlertManager is AVAILABLE (Status: {response.status_code}, Response time: {duration:.2f}s)")
        
        # Try to get alerts
        log("INFO", "Fetching alerts from AlertManager...")
        alerts_response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=2)
        
        if alerts_response.status_code == 200:
            alerts = alerts_response.json()
            log("SUCCESS", f"Retrieved {len(alerts)} alerts from AlertManager")
            
            # Show a sample alert if available
            if alerts and len(alerts) > 0:
                sample_alert = alerts[0]
                log("SAMPLE", json.dumps(sample_alert, indent=2))
        else:
            log("ERROR", f"AlertManager alerts query failed with status code: {alerts_response.status_code}")
    else:
        log("ERROR", f"AlertManager returned error status {response.status_code}")
except requests.exceptions.ConnectionError:
    log("ERROR", "AlertManager is UNREACHABLE - Connection refused")
except requests.exceptions.Timeout:
    log("ERROR", "AlertManager connection TIMEOUT")
except Exception as e:
    log("ERROR", f"Error testing AlertManager: {str(e)}")

# Test Main Host
try:
    log("INFO", f"Testing connection to Main Host API ({MAIN_HOST_URL})...")
    start_time = time.time()
    response = requests.get(f"{MAIN_HOST_URL}/api/patients", timeout=2)
    duration = time.time() - start_time
    
    if response.status_code < 400:
        log("SUCCESS", f"Main Host is AVAILABLE (Status: {response.status_code}, Response time: {duration:.2f}s)")
        
        # Try to parse response data
        try:
            data = response.json()
            log("SUCCESS", f"Retrieved data from Main Host API")
            log("SAMPLE", json.dumps(data, indent=2)[:500] + "..." if len(json.dumps(data)) > 500 else json.dumps(data, indent=2))
        except Exception as e:
            log("ERROR", f"Error parsing Main Host API response: {str(e)}")
    else:
        log("ERROR", f"Main Host API returned error status {response.status_code}")
except requests.exceptions.ConnectionError:
    log("ERROR", "Main Host API is UNREACHABLE - Connection refused")
except requests.exceptions.Timeout:
    log("ERROR", "Main Host API connection TIMEOUT")
except Exception as e:
    log("ERROR", f"Error testing Main Host API: {str(e)}")

# Test ML Service
try:
    log("INFO", f"Testing connection to ML Service API ({ML_SERVICE_URL})...")
    start_time = time.time()
    response = requests.get(f"{ML_SERVICE_URL}/health", timeout=2)
    duration = time.time() - start_time
    
    if response.status_code < 400:
        log("SUCCESS", f"ML Service is AVAILABLE (Status: {response.status_code}, Response time: {duration:.2f}s)")
    else:
        log("ERROR", f"ML Service returned error status {response.status_code}")
except requests.exceptions.ConnectionError:
    log("ERROR", "ML Service is UNREACHABLE - Connection refused")
except requests.exceptions.Timeout:
    log("ERROR", "ML Service connection TIMEOUT")
except Exception as e:
    log("ERROR", f"Error testing ML Service: {str(e)}")

print_header("DATA CONNECTIVITY RECOMMENDATION")
print("""
Based on your Docker setup, here's how to connect to your services:

1. WHEN RUNNING CODE INSIDE DOCKER CONTAINERS:
   - Use container names with internal ports:
     - Prometheus:    http://prometheus:9090
     - AlertManager:  http://alertmanager:9093
     - Main Host:     http://main_host:8000
     - ML Service:    http://ml_service:6000
     - Grafana:       http://grafana:3000

2. WHEN RUNNING CODE ON YOUR HOST MACHINE:
   - Use localhost with mapped ports:
     - Prometheus:    http://localhost:9090
     - AlertManager:  http://localhost:9093
     - Main Host:     http://localhost:8000
     - ML Service:    http://localhost:6000
     - Grafana:       http://localhost:3001  (Note the different port!)

3. TO FIX YOUR DASHBOARD:
   - Make sure Docker is running with all services up
   - If you access the dashboard at http://localhost:5000, the WebSocket connection
     should also use localhost, not container names
   
To test that your services are truly running inside Docker:
  - Run 'docker ps' to see if containers are active
  - Run 'docker logs prometheus' to check Prometheus logs
  - Run 'docker logs alertmanager' to check AlertManager logs
""")