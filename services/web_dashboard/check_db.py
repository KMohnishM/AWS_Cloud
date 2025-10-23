"""
Database check and initialization script that runs directly from app.py
"""
import os
from sqlalchemy import inspect
from datetime import datetime, timedelta
import random

def initialize_database(app, db, User, Patient, PatientLocation, PatientVitalSign, PatientMedicalHistory):
    """Initialize database with sample data if tables don't exist or are empty"""
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        
        # Check if User table exists and has any data
        inspector = inspect(db.engine)
        tables_exist = 'users' in inspector.get_table_names()
        
        if not tables_exist or User.query.count() == 0:
            print("Database tables missing or empty. Initializing with sample data...")
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@hospital.com',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            admin.set_password('admin')
            db.session.add(admin)
            
            # Create sample roles
            doctor = User(
                username='doctor',
                email='doctor@hospital.com',
                first_name='John',
                last_name='Smith',
                role='doctor',
                department='Cardiology'
            )
            doctor.set_password('doctor')
            db.session.add(doctor)
            
            nurse = User(
                username='nurse',
                email='nurse@hospital.com',
                first_name='Sarah',
                last_name='Johnson',
                role='nurse',
                department='Cardiology'
            )
            nurse.set_password('nurse')
            db.session.add(nurse)
            
            technician = User(
                username='tech',
                email='tech@hospital.com',
                first_name='David',
                last_name='Brown',
                role='technician',
                department='Radiology'
            )
            technician.set_password('tech')
            db.session.add(technician)
            
            # Commit users
            db.session.commit()
            
            # Create sample patients
            for i in range(1, 16):
                dob = datetime.now() - timedelta(days=random.randint(7300, 25550))  # 20-70 years old
                admission_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                patient = Patient(
                    mrn=f"MRN{i:06d}",
                    first_name=f"Patient{i}",
                    last_name="Test",
                    date_of_birth=dob.date(),
                    gender=random.choice(['male', 'female']),
                    blood_type=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                    admission_date=admission_date,
                    status=random.choice(['admitted', 'stable', 'critical'])
                )
                db.session.add(patient)
            
            # Commit patients
            db.session.commit()
            
            # Get all patients for reference
            patients = Patient.query.all()
            
            # Create sample locations for each patient
            departments = ['Cardiology', 'Neurology', 'Orthopedics', 'Emergency', 'ICU']
            
            for patient in patients:
                department = random.choice(departments)
                ward = f"{department[0]}{random.randint(1, 5)}"
                
                location = PatientLocation(
                    patient_id=patient.patient_id,
                    hospital='Hospital1',
                    department=department,
                    ward=ward,
                    bed=f"{random.randint(1, 20)}",
                    assigned_at=patient.admission_date,
                    active=True
                )
                db.session.add(location)
            
            # Create sample vital signs for each patient
            for patient in patients:
                # Create 5 sets of vitals for each patient at different times
                for j in range(5):
                    recorded_at = patient.admission_date + timedelta(hours=j*12)
                    
                    vital = PatientVitalSign(
                        patient_id=patient.patient_id,
                        heart_rate=random.randint(60, 100),
                        spo2=random.randint(95, 100),
                        bp_systolic=random.randint(110, 140),
                        bp_diastolic=random.randint(70, 90),
                        respiratory_rate=random.randint(12, 20),
                        temperature=round(random.uniform(36.5, 37.5), 1),
                        etco2=random.randint(35, 45),
                        recorded_by=random.choice([2, 3]),  # doctor or nurse
                        recorded_at=recorded_at
                    )
                    db.session.add(vital)
            
            # Create sample medical history for some patients
            conditions = [
                'Hypertension', 'Diabetes Type 2', 'Asthma', 'Pneumonia', 
                'Broken Arm', 'Appendicitis', 'Heart Attack', 'Stroke',
                'Allergic Reaction', 'COVID-19'
            ]
            
            for patient in random.sample(patients, 10):  # Only add history for 10 random patients
                history = PatientMedicalHistory(
                    patient_id=patient.patient_id,
                    condition=random.choice(conditions),
                    diagnosis_date=(patient.admission_date - timedelta(days=random.randint(1, 10))).date(),
                    treatment="Standard protocol treatment",
                    medication="Various medications as prescribed",
                    notes="Patient responding well to treatment",
                    recorded_by=2,  # doctor
                    recorded_at=patient.admission_date
                )
                db.session.add(history)
            
            # Commit all changes
            db.session.commit()
            print("Database initialization complete!")
        else:
            print("Database already contains data, skipping initialization.")