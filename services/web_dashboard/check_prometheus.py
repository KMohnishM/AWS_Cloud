"""
Quick check to verify Prometheus connectivity
"""
import requests
import time
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# Try localhost first (when running from host)
PROMETHEUS_URL = "http://localhost:9090"

log(f"Checking Prometheus at {PROMETHEUS_URL}...")
try:
    start_time = time.time()
    response = requests.get(f"{PROMETHEUS_URL}/-/healthy", timeout=2)
    duration = time.time() - start_time
    
    if response.status_code < 400:
        log(f"✓ Prometheus is AVAILABLE (Status: {response.status_code}, Response time: {duration:.2f}s)")
        
        # Try a simple query
        query_response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": "up"},
            timeout=2
        )
        
        if query_response.status_code == 200:
            result = query_response.json()
            if result["status"] == "success":
                log(f"✓ Query successful! Status: {result['status']}")
                log(f"✓ Got response of type: {result['data']['resultType']}")
                if "result" in result["data"]:
                    log(f"✓ Found {len(result['data']['result'])} results")
            else:
                log(f"✗ Query returned non-success status: {result['status']}")
        else:
            log(f"✗ Query failed with HTTP {query_response.status_code}")
    else:
        log(f"✗ Prometheus returned error HTTP {response.status_code}")
        
except requests.exceptions.ConnectionError:
    log("✗ CONNECTION REFUSED - Prometheus is not running or not accessible")
except requests.exceptions.Timeout:
    log("✗ REQUEST TIMED OUT - Prometheus is not responding")
except Exception as e:
    log(f"✗ ERROR: {str(e)}")
    
print("\nIf Prometheus is not accessible, make sure:")
print("1. Docker is running with 'docker-compose up' in the AWS_Cloud directory")
print("2. Prometheus container is running (check with 'docker ps')")
print("3. Port 9090 is correctly mapped in docker-compose.yml")
print("4. No firewall is blocking port 9090")