"""
Data Sources Console - Shows where data is coming from in the web dashboard
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

# Get environment variables for data sources
MAIN_HOST_URL = os.environ.get('MAIN_HOST_URL', 'http://main_host:8000')
ML_SERVICE_URL = os.environ.get('ML_SERVICE_URL', 'http://ml_service:6000')
PROMETHEUS_URL = os.environ.get('PROMETHEUS_URL', 'http://prometheus:9090')
GRAFANA_URL = os.environ.get('GRAFANA_URL', 'http://grafana:3000')
ALERTMANAGER_URL = os.environ.get('ALERTMANAGER_URL', 'http://alertmanager:9093')

# Database information
RDS_USER = os.environ.get('RDS_USERNAME')
RDS_PASS = os.environ.get('RDS_PASSWORD') 
RDS_HOST = os.environ.get('RDS_HOSTNAME')
RDS_PORT = os.environ.get('RDS_PORT')
RDS_DB = os.environ.get('RDS_DB_NAME')

# Show application header
print_header("WEB DASHBOARD DATA SOURCES")
print(f"Time: {datetime.now()}")
print("This script shows where data is coming from in the web dashboard.")

# Show data sources
print_header("DATA SOURCES CONFIGURATION")
log("INFO", f"Main Host API:      {MAIN_HOST_URL}")
log("INFO", f"ML Service API:     {ML_SERVICE_URL}")
log("INFO", f"Prometheus:         {PROMETHEUS_URL}")
log("INFO", f"Grafana:            {GRAFANA_URL}")
log("INFO", f"AlertManager:       {ALERTMANAGER_URL}")

# Database info
print_header("DATABASE CONFIGURATION")
if all([RDS_USER, RDS_PASS, RDS_HOST, RDS_PORT, RDS_DB]):
    rds_uri = f"mysql+pymysql://{RDS_USER}:{RDS_PASS}@{RDS_HOST}:{RDS_PORT}/{RDS_DB}"
    log("INFO", "Using MySQL/RDS Database")
    log("INFO", f"Database Host:      {RDS_HOST}")
    log("INFO", f"Database Name:      {RDS_DB}")
    log("INFO", f"Database User:      {RDS_USER}")
    log("INFO", f"Database Port:      {RDS_PORT}")
else:
    log("INFO", "Using SQLite Database (RDS environment variables not found)")
    log("INFO", "Database Path:     instance/healthcare.db")

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

# Check SQLite database if it exists
try:
    import os.path
    import sqlite3
    
    db_path = os.path.join('instance', 'healthcare.db')
    
    if os.path.exists(db_path):
        log("INFO", f"Found SQLite database at {db_path}")
        
        # Try to connect and query
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        log("INFO", f"Database contains {len(tables)} tables: {', '.join([t[0] for t in tables])}")
        
        # Check if patient table exists
        if any(t[0] == 'patient' for t in tables):
            cursor.execute("SELECT COUNT(*) FROM patient")
            count = cursor.fetchone()[0]
            log("INFO", f"Found {count} records in patient table")
            
            # Get sample data if available
            if count > 0:
                cursor.execute("SELECT * FROM patient LIMIT 1")
                columns = [desc[0] for desc in cursor.description]
                sample = cursor.fetchone()
                log("INFO", f"Patient table columns: {', '.join(columns)}")
                
                # Create a dictionary of column name to value
                sample_dict = {columns[i]: sample[i] for i in range(len(columns))}
                log("SAMPLE", json.dumps(sample_dict, indent=2))
    else:
        log("INFO", f"SQLite database not found at {db_path}")
except Exception as e:
    log("ERROR", f"Error checking SQLite database: {str(e)}")

print_header("DATA FLOW SUMMARY")
print("""
The first page of the web dashboard gets data from multiple sources:

1. REAL-TIME DATA VIA WEBSOCKETS:
   - Background thread in app.py polls Prometheus every 5 seconds
   - Data is sent to clients via Socket.IO WebSockets
   - This includes patient metrics, system status, and alerts

2. DATABASE DATA:
   - User authentication from SQLite/MySQL database
   - Cached patient data if Prometheus is unavailable

3. REST API ENDPOINTS:
   - Patient list from Main Host service API
   - System metrics from Prometheus API
   - Alert information from AlertManager API

When the dashboard first loads, it:
1. Gets initial data from the database
2. Connects to WebSocket for real-time updates
3. Makes API calls to get the latest information

For more detailed logging, run the main app.py and check the console output.
""")