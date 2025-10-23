#!/usr/bin/env python3
"""
Custom script to create patients that match the patient simulator format exactly.
This script focuses only on creating patients and vital signs that match the simulator data.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models.patient import Patient, PatientLocation, PatientVitalSign

def create_test_patients():
    """Create patients and vital signs that match the patient simulator format exactly"""
    print("🏥 Creating test patients that match patient simulator...")
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception:
        os.makedirs('instance', exist_ok=True)
    
    with app.app_context():
        try:
            # Check if we already have patients
            if Patient.query.count() > 0:
                print("⚠️ Found existing patients. Removing them...")
                # Delete existing patient records (but keep users)
                PatientVitalSign.query.delete()
                PatientLocation.query.delete()
                Patient.query.delete()
                db.session.commit()
            
            print("👥 Creating patients matching patient simulator...")
            
            # Create 15 patients to match simulator exactly
            for i in range(1, 16):
                # From patient_simulator/patients_data.xlsx, use exact same values
                # Sheet Patient_1 has hospital=1, dept=A, ward=1, patient=1
                # Sheet Patient_2 has hospital=1, dept=B, ward=2, patient=2, etc.
                hospital = "1" if i <= 8 else "2"  # First 8 patients in hospital 1, rest in hospital 2
                dept = "A" if i % 2 == 1 else "B"  # Alternate between dept A and B
                ward = str(((i-1) % 4) + 1)        # Cycle through wards 1-4
                
                dob = datetime.now() - timedelta(days=random.randint(7300, 25550))  # 20-70 years old
                admission_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                patient = Patient(
                    mrn=f"MRN{i:06d}",
                    first_name=f"Patient{i}",
                    last_name=f"Hospital{hospital}-Dept{dept}",
                    date_of_birth=dob.date(),
                    gender=random.choice(['male', 'female']),
                    blood_type=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                    admission_date=admission_date,
                    status=random.choice(['admitted', 'stable', 'critical'])
                )
                db.session.add(patient)
            
            db.session.commit()
            print("✅ Patients created successfully!")
            
            # Get all patients for reference
            patients = Patient.query.all()
            
            print("📍 Creating patient locations...")
            
            # Create locations for each patient
            for patient in patients:
                patient_num = patient.patient_id
                i = patient_num  # For clarity
                
                # Extract hospital and dept from last_name format: "Hospital{hospital}-Dept{dept}"
                hospital_num = patient.last_name.split('-')[0].replace('Hospital', '')
                dept_letter = patient.last_name.split('-')[1].replace('Dept', '')
                ward_num = str(((i-1) % 4) + 1)
                
                location = PatientLocation(
                    patient_id=patient.patient_id,
                    hospital=hospital_num,  # Keep as "1" or "2" to match simulator exactly
                    department=dept_letter, # Keep as "A" or "B" to match simulator exactly
                    ward=ward_num,          # Keep as "1", "2", "3", or "4" to match simulator exactly
                    bed=f"{random.randint(1, 20)}",
                    assigned_at=patient.admission_date,
                    active=True
                )
                db.session.add(location)
            
            db.session.commit()
            print("✅ Patient locations created successfully!")
            
            print("💓 Creating vital signs...")
            
            # Create vital signs for each patient
            base_time = datetime.now() - timedelta(hours=1)
            
            for patient in patients:
                patient_num = patient.patient_id
                i = patient_num  # For clarity
                
                # Get location information from patient record
                hospital_num = patient.last_name.split('-')[0].replace('Hospital', '')
                dept_letter = patient.last_name.split('-')[1].replace('Dept', '')
                ward_num = str(((i-1) % 4) + 1)
                
                # Create 5 sets of vitals for each patient, exactly matching Excel format
                for j in range(5):
                    recorded_at = base_time + timedelta(minutes=j*5)
                    
                    heart_rate = random.randint(60, 100)
                    spo2 = random.randint(85, 98)
                    bp_systolic = random.randint(100, 130)
                    bp_diastolic = random.randint(60, 90)
                    respiratory_rate = random.randint(12, 20)
                    temperature = round(random.uniform(36.5, 38.0), 1)
                    etco2 = random.randint(30, 45)
                    
                    # Additional fields from patient simulator
                    fio2 = 21  # Fixed value from Excel
                    wbc_count = round(random.uniform(4.0, 12.0), 1) 
                    lactate = round(random.uniform(1.0, 3.0), 1)
                    blood_glucose = random.randint(70, 180)
                    
                    # Add occasional anomalies (15% chance as in simulator)
                    if random.random() < 0.15:
                        anomaly_fields = random.sample(
                            ["heart_rate", "bp_systolic", "bp_diastolic", "respiratory_rate", "spo2", "etco2"],
                            k=random.randint(1, 2)
                        )
                        for field in anomaly_fields:
                            if field == "heart_rate":
                                heart_rate = random.choice([random.randint(30, 50), random.randint(120, 160)])
                            elif field == "bp_systolic":
                                bp_systolic = random.choice([random.randint(70, 90), random.randint(140, 170)])
                            elif field == "bp_diastolic":
                                bp_diastolic = random.choice([random.randint(40, 55), random.randint(95, 110)])
                            elif field == "respiratory_rate":
                                respiratory_rate = random.choice([random.randint(5, 10), random.randint(25, 35)])
                            elif field == "spo2":
                                spo2 = random.randint(70, 84)
                            elif field == "etco2":
                                etco2 = random.choice([random.randint(10, 25), random.randint(46, 60)])
                    
                    # Store additional fields in extra_data as JSON
                    extra_data = {
                        "hospital": hospital_num,
                        "dept": dept_letter, 
                        "ward": ward_num,
                        "patient": str(i),
                        "fio2": fio2, 
                        "wbc_count": wbc_count,
                        "lactate": lactate,
                        "blood_glucose": blood_glucose,
                        "ecg_signal": "dummy_waveform_data"
                    }
                    
                    vital = PatientVitalSign(
                        patient_id=patient.patient_id,
                        heart_rate=heart_rate,
                        spo2=spo2,
                        bp_systolic=bp_systolic,
                        bp_diastolic=bp_diastolic,
                        respiratory_rate=respiratory_rate,
                        temperature=temperature,
                        etco2=etco2,
                        extra_data=json.dumps(extra_data),
                        recorded_by=None,  # No user association needed
                        recorded_at=recorded_at
                    )
                    db.session.add(vital)
            
            db.session.commit()
            print("✅ Vital signs created successfully!")
            
            print("\n🎉 Test patients initialization complete!")
            print(f"\n📊 Created {Patient.query.count()} patients with vitals matching patient simulator")
            
        except Exception as e:
            print(f"❌ Error during test patients creation: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_test_patients()