"""
Patient Data Validator

This script checks if the patient data is consistently showing 15 patients
by calling the relevant function in app.py directly.
"""
import sys
import os
import json

# Add the parent directory to the path so we can import from app.py
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from app import get_patient_metrics_from_prometheus
    print("Successfully imported the get_patient_metrics_from_prometheus function")
except ImportError as e:
    print(f"Error importing function from app.py: {e}")
    sys.exit(1)

def validate_patient_count():
    """Check if the patient data consistently shows 15 patients."""
    try:
        # Call the function that gets patient data
        result = get_patient_metrics_from_prometheus()
        
        # Check if we have patient data
        if 'patients' not in result:
            print("ERROR: No 'patients' key in the result!")
            return False
        
        # Count the patients
        patient_count = len(result['patients'])
        print(f"Patient count: {patient_count}")
        
        # Check if we have 15 patients
        if patient_count == 15:
            print("SUCCESS: Patient count is 15 as expected!")
            
            # Count patients by status
            status_counts = {'normal': 0, 'warning': 0, 'critical': 0}
            for patient in result['patients']:
                status = patient.get('status', 'unknown')
                if status in status_counts:
                    status_counts[status] += 1
            
            print(f"Patient distribution: {status_counts}")
            print("\nSample patient data:")
            print(json.dumps(result['patients'][0], indent=2))
            
            return True
        else:
            print(f"ERROR: Patient count is {patient_count}, expected 15!")
            return False
            
    except Exception as e:
        print(f"Error validating patient count: {e}")
        return False

if __name__ == "__main__":
    print("Starting patient data validation...")
    validate_patient_count()