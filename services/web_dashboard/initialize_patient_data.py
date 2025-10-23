#!/usr/bin/env python3
"""
Patient Data Initialization Script
This script helps ensure the patient data is properly set up between the patient simulator
and web dashboard by:
1. Checking for the presence of patient data Excel file
2. Generating sample data if needed
3. Synchronizing the database with the patient data
"""

import os
import sys
import subprocess
import pandas as pd
from pathlib import Path
import random
import json
from datetime import datetime, timedelta

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DATA_LOCATIONS = [
    Path(PROJECT_ROOT) / 'data' / 'patient_samples' / 'patients_data.xlsx',
    Path(PROJECT_ROOT) / 'services' / 'patient_simulator' / 'data' / 'patients_data.xlsx',
    Path('/app/data/patients_data.xlsx')  # Docker container path
]
NUM_PATIENTS = 15
NUM_SAMPLES_PER_PATIENT = 50

def find_excel_file():
    """Find the patient data Excel file or return None if not found"""
    for location in DATA_LOCATIONS:
        if location.exists():
            return location
    return None

def generate_excel_file(file_path):
    """Generate a sample patient data Excel file with multiple sheets"""
    print(f"🏥 Generating sample patient data at {file_path}")
    
    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Dictionary to hold DataFrames for each patient
    patient_data_frames = {}
    
    # For each patient, create a DataFrame with sample data
    for patient_id in range(1, NUM_PATIENTS + 1):
        data = []
        hospital_id = random.randint(1, 3)
        dept_id = random.randint(1, 4)
        ward_id = random.randint(1, 5)
        
        # Generate baseline vital signs for this patient
        baseline_hr = random.randint(65, 85)
        baseline_spo2 = random.randint(95, 99)
        baseline_bp_sys = random.randint(110, 130)
        baseline_bp_dia = random.randint(70, 85)
        baseline_rr = random.randint(14, 18)
        baseline_temp = round(random.uniform(36.5, 37.5), 1)
        baseline_etco2 = random.randint(35, 45)
        baseline_fio2 = random.randint(21, 30)
        baseline_wbc = round(random.uniform(4.5, 11.0), 1)
        baseline_lactate = round(random.uniform(0.5, 2.0), 1)
        baseline_glucose = random.randint(70, 140)
        
        # Generate sample data points
        start_time = datetime.now() - timedelta(hours=12)
        for i in range(NUM_SAMPLES_PER_PATIENT):
            # Add some variation to baseline values
            hr_variation = random.uniform(-5, 5)
            spo2_variation = random.uniform(-2, 1)
            bp_sys_variation = random.uniform(-10, 10)
            bp_dia_variation = random.uniform(-5, 5)
            rr_variation = random.uniform(-2, 2)
            temp_variation = random.uniform(-0.3, 0.3)
            etco2_variation = random.uniform(-5, 5)
            
            # Create a data point
            data_point = {
                'hospital': hospital_id,
                'dept': dept_id,
                'ward': ward_id,
                'patient': patient_id,
                'timestamp': start_time + timedelta(minutes=i*15),  # Each reading 15 minutes apart
                'heart_rate': max(40, min(180, baseline_hr + hr_variation)),
                'spo2': max(85, min(100, baseline_spo2 + spo2_variation)),
                'bp_systolic': max(90, min(180, baseline_bp_sys + bp_sys_variation)),
                'bp_diastolic': max(50, min(110, baseline_bp_dia + bp_dia_variation)),
                'respiratory_rate': max(8, min(30, baseline_rr + rr_variation)),
                'temperature': max(35, min(40, baseline_temp + temp_variation)),
                'etco2': max(20, min(60, baseline_etco2 + etco2_variation)),
                'fio2': baseline_fio2,
                'wbc_count': baseline_wbc + random.uniform(-0.5, 0.5),
                'lactate': baseline_lactate + random.uniform(-0.2, 0.2),
                'blood_glucose': baseline_glucose + random.randint(-10, 10),
                'ecg_signal': json.dumps([random.uniform(-0.5, 1.5) for _ in range(25)])  # Simulated ECG data
            }
            data.append(data_point)
        
        # Create DataFrame for this patient
        patient_df = pd.DataFrame(data)
        patient_data_frames[f'Patient_{patient_id}'] = patient_df
    
    # Save to Excel with each patient as a separate sheet
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in patient_data_frames.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Successfully generated sample data for {NUM_PATIENTS} patients with {NUM_SAMPLES_PER_PATIENT} readings each")
    return True

def sync_with_database():
    """Synchronize the patient data with the database"""
    print("🔄 Synchronizing patient data with database...")
    
    # Check if we're inside the web_dashboard directory
    if os.path.exists('app.py') and os.path.exists('sync_patients.py'):
        # We're in the web_dashboard directory
        subprocess.run(['python', 'sync_patients.py'], check=True)
    elif os.path.exists('services/web_dashboard/sync_patients.py'):
        # We're in the project root
        os.chdir('services/web_dashboard')
        subprocess.run(['python', 'sync_patients.py'], check=True)
    else:
        print("❌ Could not locate sync_patients.py. Please run this script from the project root or web_dashboard directory.")
        return False
    
    print("✅ Patient data synchronized with database")
    return True

def main():
    """Main function"""
    print("🏥 Patient Data Initialization Script")
    print("------------------------------------")
    
    # Step 1: Find the patient data Excel file
    excel_file = find_excel_file()
    
    # Step 2: Generate sample data if needed
    if excel_file is None:
        print("⚠️ Patient data file not found. Generating sample data...")
        # Try to generate in each possible location until one works
        for location in DATA_LOCATIONS:
            try:
                if generate_excel_file(location):
                    excel_file = location
                    break
            except Exception as e:
                print(f"Failed to generate at {location}: {e}")
    
    if excel_file is None:
        print("❌ Failed to generate patient data file. Please check permissions.")
        return 1
    
    print(f"✅ Using patient data file: {excel_file}")
    
    # Step 3: Synchronize with database
    try:
        sync_with_database()
    except Exception as e:
        print(f"❌ Error synchronizing with database: {e}")
        return 1
    
    print("✅ Patient data initialization complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())