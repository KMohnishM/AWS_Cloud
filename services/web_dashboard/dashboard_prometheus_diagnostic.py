"""
Diagnose issues with the web dashboard's connection to Prometheus.
This script examines how the web_dashboard service retrieves data from Prometheus.
"""
import os
import sys
import json
import requests
from pathlib import Path

# Add the current directory to the path to import from app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Try to import functions from app.py
try:
    from app import get_patient_metrics_from_prometheus
    print("✅ Successfully imported functions from app.py")
except ImportError as e:
    print(f"❌ Failed to import from app.py: {e}")
    sys.exit(1)

def check_prometheus_variables():
    """Check if the required environment variables are set."""
    print("\n=== Checking Environment Variables ===")
    
    # Check if the environment variables are set
    prometheus_url = os.environ.get('PUBLIC_PROMETHEUS_URL')
    if prometheus_url:
        print(f"✅ PUBLIC_PROMETHEUS_URL is set to: {prometheus_url}")
    else:
        print("❌ PUBLIC_PROMETHEUS_URL environment variable is not set")
        print("   Setting default value: http://localhost:9090")
        os.environ['PUBLIC_PROMETHEUS_URL'] = 'http://localhost:9090'
    
    # Try to connect to Prometheus
    try:
        response = requests.get(f"{os.environ.get('PUBLIC_PROMETHEUS_URL', 'http://localhost:9090')}/-/healthy", timeout=5)
        if response.status_code == 200:
            print(f"✅ Successfully connected to Prometheus at {os.environ.get('PUBLIC_PROMETHEUS_URL', 'http://localhost:9090')}")
        else:
            print(f"❌ Failed to connect to Prometheus: Status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to Prometheus: {e}")

def test_get_patient_metrics():
    """Test the get_patient_metrics_from_prometheus function."""
    print("\n=== Testing get_patient_metrics_from_prometheus() Function ===")
    
    try:
        # Call the function
        result = get_patient_metrics_from_prometheus()
        
        # Check if the result is valid
        if not isinstance(result, dict):
            print(f"❌ Function returned {type(result).__name__}, expected dict")
            return
        
        print(f"✅ Function returned a valid dict with {len(result)} keys")
        
        # Check if patients key exists
        if 'patients' not in result:
            print("❌ 'patients' key is missing from the result")
            print(f"Available keys: {list(result.keys())}")
            return
        
        patients = result['patients']
        print(f"✅ Found 'patients' key with {len(patients)} patients")
        
        # Check if the patients are valid
        if not patients:
            print("❌ No patients in the result")
            return
        
        # Count patients by status
        status_counts = {'normal': 0, 'warning': 0, 'critical': 0, 'unknown': 0}
        for patient in patients:
            status = patient.get('status', 'unknown')
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts['unknown'] += 1
        
        print(f"Patient status distribution: {status_counts}")
        
        # Print a sample patient
        print("\nSample patient data:")
        print(json.dumps(patients[0], indent=2))
        
        # Check if the patient count matches what we expect
        if len(patients) != 15:
            print(f"⚠️ Expected 15 patients, but found {len(patients)}")
            print("This suggests the function is not retrieving all patients from Prometheus")
            print("\nPossible causes:")
            print("1. The function has hardcoded values instead of querying Prometheus")
            print("2. The function is not parsing the Prometheus response correctly")
            print("3. The fallback logic is being triggered when it shouldn't be")
        else:
            print("✅ The function returned the expected 15 patients")
            
    except Exception as e:
        print(f"❌ Error testing function: {e}")

def analyze_app_code():
    """Analyze the app.py code for potential issues with Prometheus data retrieval."""
    print("\n=== Analyzing app.py Code ===")
    
    app_path = Path(current_dir) / "app.py"
    if not app_path.exists():
        print(f"❌ Cannot find app.py at {app_path}")
        return
    
    print(f"✅ Found app.py at {app_path}")
    
    with open(app_path, 'r') as f:
        app_code = f.read()
    
    # Check if there are any hardcoded patient counts
    if "patients = [" in app_code:
        print("⚠️ Found hardcoded patient list in app.py")
        
    if "range(5)" in app_code:
        print("⚠️ Found hardcoded range(5) in app.py which may limit patient count to 5")
    
    # Check if there's fallback logic
    if "except" in app_code and "patients" in app_code:
        print("⚠️ Found exception handling around patient data retrieval")
        print("   This might be causing fallback logic to be used instead of Prometheus data")
    
    # Look for the Prometheus query code
    if "query=" in app_code and "prometheus" in app_code.lower():
        print("✅ Found Prometheus query code in app.py")
    else:
        print("❌ Could not find Prometheus query code in app.py")

def main():
    """Main function to diagnose dashboard-to-Prometheus connectivity issues."""
    print("=" * 50)
    print("WEB DASHBOARD TO PROMETHEUS CONNECTIVITY DIAGNOSTIC")
    print("=" * 50)
    
    # Step 1: Check environment variables
    check_prometheus_variables()
    
    # Step 2: Test the get_patient_metrics_from_prometheus function
    test_get_patient_metrics()
    
    # Step 3: Analyze the app.py code
    analyze_app_code()
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    main()