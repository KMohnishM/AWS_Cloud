# Data Console Logger
# This script logs data source information to help track where data is coming from in the web dashboard

import os
import requests
import json
import time
from datetime import datetime
import sys

# Configure data source URLs from environment or default values
MAIN_HOST_URL = os.environ.get('MAIN_HOST_URL', 'http://main_host:8000')
ML_SERVICE_URL = os.environ.get('ML_SERVICE_URL', 'http://ml_service:6000')
PROMETHEUS_URL = os.environ.get('PROMETHEUS_URL', 'http://prometheus:9090')
GRAFANA_URL = os.environ.get('GRAFANA_URL', 'http://grafana:3000')
ALERTMANAGER_URL = os.environ.get('ALERTMANAGER_URL', 'http://alertmanager:9093')

def log_header(title):
    """Print a formatted header in the console"""
    line = "=" * 80
    print("\n" + line)
    print(f" {title} ".center(80, '='))
    print(line + "\n")

def log_info(message):
    """Print information with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [INFO] {message}")

def log_warning(message):
    """Print warning with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [WARNING] {message}")

def log_error(message):
    """Print error with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [ERROR] {message}")

def log_success(message):
    """Print success message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [SUCCESS] {message}")

def check_data_source_connectivity(url, name):
    """Check if a data source is reachable and log result"""
    start_time = time.time()
    try:
        log_info(f"Testing connectivity to {name} at {url}...")
        response = requests.get(url, timeout=3)
        duration = time.time() - start_time
        
        if response.status_code < 400:
            log_success(f"{name} is AVAILABLE (Status: {response.status_code}, Response time: {duration:.2f}s)")
            return True
        else:
            log_warning(f"{name} returned error status {response.status_code} (Response time: {duration:.2f}s)")
            return False
    except requests.exceptions.ConnectionError:
        log_error(f"{name} is UNREACHABLE - Connection refused")
        return False
    except requests.exceptions.Timeout:
        log_error(f"{name} is TIMEOUT - Request timed out after 3s")
        return False
    except Exception as e:
        log_error(f"{name} check failed: {str(e)}")
        return False

def query_prometheus(query_text):
    """Query Prometheus and return results"""
    try:
        log_info(f"Querying Prometheus: {query_text}")
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query_text},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "success":
                result_count = len(result["data"]["result"])
                log_success(f"Prometheus query returned {result_count} results")
                return result["data"]["result"]
            else:
                log_warning(f"Prometheus query returned non-success status: {result['status']}")
        else:
            log_error(f"Prometheus query failed with status code: {response.status_code}")
        
        return []
    except Exception as e:
        log_error(f"Error querying Prometheus: {str(e)}")
        return []

def query_alertmanager():
    """Query AlertManager for alerts"""
    try:
        log_info("Querying AlertManager for alerts")
        response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=3)
        
        if response.status_code == 200:
            alerts = response.json()
            log_success(f"AlertManager returned {len(alerts)} alerts")
            return alerts
        else:
            log_error(f"AlertManager query failed: {response.status_code}")
        
        return []
    except Exception as e:
        log_error(f"Error querying AlertManager: {str(e)}")
        return []

def query_main_host():
    """Query the main_host service for patient data"""
    try:
        log_info(f"Querying main_host service at {MAIN_HOST_URL}/api/patients")
        response = requests.get(f"{MAIN_HOST_URL}/api/patients", timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"main_host returned data successfully")
            return data
        else:
            log_error(f"main_host query failed: {response.status_code}")
        
        return None
    except Exception as e:
        log_error(f"Error querying main_host: {str(e)}")
        return None

def check_sqlite_database():
    """Check the SQLite database existence and patients table"""
    import os.path
    import sqlite3
    
    try:
        # Check if instance folder exists
        if not os.path.exists('instance'):
            log_warning("Instance folder does not exist")
            return False
            
        # Check if database file exists
        db_path = os.path.join('instance', 'healthcare.db')
        if not os.path.exists(db_path):
            log_warning(f"SQLite database file not found at {db_path}")
            return False
            
        # Try to connect and query
        log_info(f"Checking SQLite database at {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if patients table exists and count records
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='patient'")
        if cursor.fetchone()[0] == 0:
            log_warning("Patient table does not exist in database")
            return False
            
        # Count patients
        cursor.execute("SELECT count(*) FROM patient")
        patient_count = cursor.fetchone()[0]
        log_success(f"Found {patient_count} patients in SQLite database")
        
        # Get sample data if available
        if patient_count > 0:
            cursor.execute("SELECT * FROM patient LIMIT 1")
            columns = [desc[0] for desc in cursor.description]
            sample = cursor.fetchone()
            log_info(f"Patient table columns: {', '.join(columns)}")
            
        return True
    except Exception as e:
        log_error(f"Error checking SQLite database: {str(e)}")
        return False

def run_console():
    """Run the data console to check all data sources"""
    log_header("HOSPITAL DASHBOARD DATA CONSOLE")
    
    print("This tool shows where data is coming from in the web dashboard.")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {os.name}")
    
    log_header("CHECKING DATA SOURCE CONNECTIVITY")
    
    # Check connectivity to all data sources
    check_data_source_connectivity(PROMETHEUS_URL, "Prometheus")
    check_data_source_connectivity(ALERTMANAGER_URL, "AlertManager")
    check_data_source_connectivity(MAIN_HOST_URL, "Main Host Service")
    check_data_source_connectivity(ML_SERVICE_URL, "Machine Learning Service")
    check_data_source_connectivity(GRAFANA_URL, "Grafana")
    
    # Check SQLite database
    log_header("CHECKING LOCAL DATABASE")
    check_sqlite_database()
    
    # Query Prometheus for patient data
    log_header("SAMPLE DATA FROM PROMETHEUS")
    patient_metrics = query_prometheus("patient_heart_rate")
    if patient_metrics:
        print("\nSample patient heart rate data:")
        for i, metric in enumerate(patient_metrics[:3]):
            print(f"\nPatient {i+1}:")
            print(json.dumps(metric, indent=2))
        
        if len(patient_metrics) > 3:
            print(f"\n...and {len(patient_metrics) - 3} more patients")
    else:
        print("\nNo patient heart rate data available from Prometheus")
    
    # Query AlertManager for alerts
    log_header("SAMPLE ALERTS FROM ALERTMANAGER")
    alerts = query_alertmanager()
    if alerts:
        print("\nCurrent alerts:")
        for i, alert in enumerate(alerts[:3]):
            print(f"\nAlert {i+1}:")
            if "annotations" in alert and "summary" in alert["annotations"]:
                print(f"Summary: {alert['annotations']['summary']}")
            if "labels" in alert and "severity" in alert["labels"]:
                print(f"Severity: {alert['labels']['severity']}")
            if "startsAt" in alert:
                print(f"Started: {alert['startsAt']}")
        
        if len(alerts) > 3:
            print(f"\n...and {len(alerts) - 3} more alerts")
    else:
        print("\nNo alerts available from AlertManager")
    
    # Query Main Host for patient data
    log_header("SAMPLE DATA FROM MAIN HOST SERVICE")
    patients_data = query_main_host()
    if patients_data:
        if isinstance(patients_data, dict) and "patients" in patients_data:
            patients = patients_data["patients"]
            print(f"\nFound {len(patients)} patients from Main Host")
            for i, patient in enumerate(patients[:3]):
                print(f"\nPatient {i+1}:")
                print(json.dumps(patient, indent=2))
            
            if len(patients) > 3:
                print(f"\n...and {len(patients) - 3} more patients")
        else:
            print("\nUnexpected data format from Main Host")
            print(json.dumps(patients_data, indent=2)[:500])
    else:
        print("\nNo patient data available from Main Host service")
    
    # Show data flow summary
    log_header("DATA FLOW SUMMARY")
    print("""
Data Flow in the Web Dashboard:

1. REAL-TIME DATA VIA WEBSOCKETS:
   - Background thread in app.py polls Prometheus every 5 seconds
   - Fetches patient metrics, system status and alerts
   - Sends to connected clients via WebSocket (Socket.IO)
   - Client JavaScript receives and updates dashboard in real-time

2. REST API ENDPOINTS:
   - /api/patients - Fetches patient list from Main Host service
   - /api/metrics - Gets metrics directly from Prometheus
   - /api/system-status - Gets system status from Prometheus
   - /api/recent-alerts - Gets alerts from AlertManager

3. LOCAL DATABASE:
   - SQLite/MySQL stores user accounts and authentication data
   - May store cached patient data if external services are unavailable
   - Database initialized in app.py with default users

4. FALLBACK MECHANISMS:
   - If Prometheus/AlertManager unavailable, uses cached data
   - If all external services down, generates mock data
   
5. MONITORING INTEGRATION:
   - Grafana provides visualization dashboards at port 3000
   - Prometheus collects and stores metrics at port 9090
   - AlertManager processes and manages alerts at port 9093
""")

if __name__ == "__main__":
    run_console()