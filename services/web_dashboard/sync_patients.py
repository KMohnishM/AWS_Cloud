#!/usr/bin/env python3
"""
Direct Patient Data Reader for Web Dashboard
This module directly reads patient data from the patient_simulator's Excel file,
eliminating the need for a separate database initialization process.
"""

import os
import pandas as pd
import json
import logging
from datetime import datetime
from database import db
from models.patient import Patient, PatientLocation, PatientVitalSign, PatientMedicalHistory
from app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_patient_data_file():
    """Find the patient data Excel file in multiple possible locations"""
    possible_paths = [
        "/app/data/patients_data.xlsx",  # Docker container path
        os.path.join(os.path.dirname(__file__), '..', 'patient_simulator', 'data', 'patients_data.xlsx'),  # Local dev path
        os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'patient_samples', 'patients_data.xlsx')  # Project root path
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found patient data file at: {path}")
            return path
    
    logger.warning("Patient data file not found in any of the expected locations")
    return None

def read_patient_data_from_excel(file_path=None):
    """Read patient data directly from the patient simulator's Excel file"""
    if file_path is None:
        file_path = find_patient_data_file()
        
    if not file_path or not os.path.exists(file_path):
        logger.error(f"Error: Patient data file not found")
        return None
    
    try:
        logger.info(f"Reading patient data from {file_path}")
        df_sheets = pd.read_excel(file_path, sheet_name=None)
        return df_sheets
    except Exception as e:
        logger.error(f"Error reading the Excel file: {e}")
        return None

def sync_patients_from_simulator(app=None):
    """Sync patients from patient simulator Excel file to the web dashboard"""
    logger.info("🏥 Syncing patients from patient simulator data...")
    
    # Create app context if not provided
    if app is None:
        app = create_app()
    
    with app.app_context():
        try:
            # Read patient data from Excel
            sheets = read_patient_data_from_excel()
            if not sheets:
                logger.error("❌ Failed to read patient data from Excel file.")
                return False
            
            # Clear existing data to avoid duplicates
            logger.info("Clearing existing patient data...")
            PatientVitalSign.query.delete()
            PatientLocation.query.delete()
            PatientMedicalHistory.query.delete()
            Patient.query.delete()
            
            # Dictionary to store patient IDs by sheet name
            patient_ids = {}
            
            # Process each sheet (each sheet represents a patient)
            for sheet_name, df in sheets.items():
                if not df.empty:
                    try:
                        # Extract patient number from sheet name (e.g., "Patient_1" → 1)
                        patient_num = int(sheet_name.split('_')[1])
                        
                        # Get patient metadata from the first row
                        first_row = df.iloc[0]
                        hospital = str(first_row.get('hospital', 'General'))
                        dept = str(first_row.get('dept', 'Internal Medicine'))
                        ward = str(first_row.get('ward', 'A'))
                        
                        # Create new patient
                        logger.info(f"➕ Creating patient from {sheet_name}...")
                        
                        # Create patient record
                        patient = Patient(
                            mrn=f"MRN{patient_num:06d}",
                            first_name=f"Patient{patient_num}",
                            last_name=f"Hospital{hospital}-Dept{dept}",
                            date_of_birth=datetime.now().replace(year=datetime.now().year - 40).date(),
                            gender="male" if patient_num % 2 == 0 else "female",
                            blood_type=["A+", "B+", "O+", "AB+"][patient_num % 4],
                            admission_date=datetime.now().replace(day=1),
                            status="stable"
                        )
                        db.session.add(patient)
                        db.session.flush()  # Get the patient ID before committing
                        
                        # Create patient location
                        location = PatientLocation(
                            patient_id=patient.patient_id,
                            hospital=hospital,
                            department=dept,
                            ward=ward,
                            bed=f"{patient_num}",
                            assigned_at=datetime.now(),
                            active=True
                        )
                        db.session.add(location)
                        
                        # Create medical history with random conditions
                        conditions = [
                            "Hypertension", "Diabetes Type 2", "Asthma", "COPD",
                            "Coronary Artery Disease", "Congestive Heart Failure"
                        ]
                        history = PatientMedicalHistory(
                            patient_id=patient.patient_id,
                            condition=conditions[patient_num % len(conditions)],
                            diagnosis_date=datetime.now().replace(month=1),
                            notes=f"Patient has a history of {conditions[patient_num % len(conditions)]}."
                        )
                        db.session.add(history)
                        
                        # Store the patient ID for later use
                        patient_ids[sheet_name] = patient.patient_id
                        
                        # Add vital signs for this patient
                        # We limit to first 15 rows to avoid overwhelming the database
                        row_count = 0
                        for _, row in df.head(15).iterrows():
                            try:
                                # Extract vital signs with fallbacks
                                heart_rate = float(row.get('heart_rate', 75))
                                spo2 = float(row.get('spo2', 98))
                                bp_systolic = int(row.get('bp_systolic', 120))
                                bp_diastolic = int(row.get('bp_diastolic', 80))
                                respiratory_rate = float(row.get('respiratory_rate', 16))
                                temperature = float(row.get('temperature', 37.0))
                                etco2 = float(row.get('etco2', 35))
                                
                                # Calculate anomaly score based on vitals
                                # Simple algorithm that looks at key vitals
                                anomaly_score = 0.1  # Default low score
                                
                                # High anomaly if vitals are significantly outside normal ranges
                                if (heart_rate < 60 or heart_rate > 100 or 
                                   spo2 < 90 or 
                                   temperature < 36 or temperature > 38):
                                    anomaly_score = round(max(0.6, anomaly_score), 2)  # High anomaly
                                # Medium anomaly if vitals are slightly outside normal ranges
                                elif (heart_rate < 65 or heart_rate > 95 or 
                                     spo2 < 94 or 
                                     temperature < 36.4 or temperature > 37.6):
                                    anomaly_score = round(max(0.3, anomaly_score), 2)  # Medium anomaly
                                
                                # Build extra data dictionary with all additional fields
                                extra_data = {
                                    'anomaly_score': anomaly_score  # Add anomaly score to extra data
                                }
                                
                                for key, value in row.items():
                                    if key not in ['heart_rate', 'spo2', 'bp_systolic', 'bp_diastolic', 
                                                  'respiratory_rate', 'temperature', 'etco2']:
                                        # Convert pandas/numpy types to Python native types
                                        if hasattr(value, 'item'):
                                            value = value.item()
                                        # Handle NaN values
                                        if pd.isna(value):
                                            continue
                                        # Convert timestamps
                                        if isinstance(value, pd.Timestamp):
                                            value = value.strftime('%Y-%m-%d %H:%M:%S')
                                        extra_data[key] = value
                                
                                # Determine timestamp
                                recorded_at = datetime.now()
                                if 'timestamp' in row and not pd.isna(row['timestamp']):
                                    try:
                                        recorded_at = pd.to_datetime(row['timestamp'])
                                    except:
                                        pass
                                
                                # Create vital sign record
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
                                    recorded_at=recorded_at
                                )
                                db.session.add(vital)
                                row_count += 1
                            except Exception as e:
                                logger.warning(f"Error processing row for patient {patient_num}: {e}")
                                continue
                        
                        logger.info(f"Added {row_count} vital records for patient {patient_num}")
                    
                    except Exception as e:
                        logger.error(f"Error processing sheet {sheet_name}: {e}")
                        continue
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"✅ Successfully synced {len(patient_ids)} patients from patient simulator!")
            logger.info(f"📊 Added vitals for all patients from Excel data")
            return True
            
        except Exception as e:
            logger.exception(f"❌ Error during patient sync: {e}")
            db.session.rollback()
            return False

def init_admin_user():
    """Ensure admin user exists in the database"""
    from models.user import User
    
    app = create_app()
    with app.app_context():
        # Check if admin user exists
        if User.query.filter_by(username="admin").first() is None:
            from werkzeug.security import generate_password_hash
            
            # Create admin user
            admin = User(
                username="admin",
                password_hash=generate_password_hash("admin"),
                email="admin@example.com",
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Created admin user (username: admin, password: admin)")
    
if __name__ == "__main__":
    success = sync_patients_from_simulator()
    init_admin_user()
    
    if success:
        print("✅ Successfully synchronized patients from Excel data")
    else:
        print("❌ Failed to synchronize patients from Excel data")