"""
Test that our fix for the Prometheus queries actually works.
This script directly calls the get_patient_metrics_from_prometheus function.
"""
import os
import sys
import json

# Add the current directory to the path to import from app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Set required environment variables
os.environ['PUBLIC_PROMETHEUS_URL'] = 'http://localhost:9090'
os.environ['PUBLIC_GRAFANA_URL'] = 'http://localhost:3001'
os.environ['PUBLIC_ALERTMANAGER_URL'] = 'http://localhost:9093'

try:
    from app import get_patient_metrics_from_prometheus
    print("✅ Successfully imported get_patient_metrics_from_prometheus from app.py")
except ImportError as e:
    print(f"❌ Failed to import from app.py: {e}")
    sys.exit(1)

def test_patient_metrics():
    """Test the get_patient_metrics_from_prometheus function with our fix."""
    print("\n=== Testing get_patient_metrics_from_prometheus function ===")
    
    try:
        result = get_patient_metrics_from_prometheus()
        
        if not isinstance(result, dict):
            print(f"❌ Function returned {type(result).__name__}, expected dict")
            return
        
        print(f"✅ Function returned a valid dict with {len(result)} keys")
        print(f"Keys: {list(result.keys())}")
        
        # Check if patients key exists and contains data
        if 'patients' not in result:
            print("❌ 'patients' key is missing from the result")
            return
        
        patients = result['patients']
        patient_count = len(patients)
        print(f"✅ Found {patient_count} patients in the result")
        
        # Check the patient count against what we expect
        if patient_count == 15:
            print("✅ The function returned the expected 15 patients")
        else:
            print(f"⚠️ Expected 15 patients, but found {patient_count}")
            
            # Check if we're using fallback data
            if patient_count == 5:
                print("❌ Still getting 5 patients - likely still using fallback data")
            elif patient_count == 0:
                print("❌ Got 0 patients - function is returning empty patient list")
        
        # Check other metrics
        print(f"Total patients: {result.get('total_patients', 'missing')}")
        print(f"Normal patients: {result.get('normal_patients', 'missing')}")
        print(f"Warning patients: {result.get('warning_patients', 'missing')}")
        print(f"Critical patients: {result.get('critical_patients', 'missing')}")
        
        # Print a sample patient record
        if patients:
            print("\nSample patient data:")
            print(json.dumps(patients[0], indent=2))
        
    except Exception as e:
        print(f"❌ Error testing function: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("TESTING FIX FOR PROMETHEUS QUERIES")
    print("=" * 50)
    
    test_patient_metrics()