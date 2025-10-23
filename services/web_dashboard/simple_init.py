#!/usr/bin/env python3
"""
Simple database initialization script that creates tables without importing the full Flask app
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random
import hashlib

def create_database():
    """Create the database and tables"""
    print("🏥 Creating Hospital Monitoring Database...")
    
    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)
    
    # Connect to SQLite database
    conn = sqlite3.connect('instance/healthcare.db')
    cursor = conn.cursor()
    
    try:
        # Create users table
        print("📋 Creating users table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                department VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create patients table
        print("📋 Creating patients table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                mrn VARCHAR(20) UNIQUE NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                date_of_birth DATE NOT NULL,
                gender VARCHAR(10) NOT NULL,
                blood_type VARCHAR(5),
                admission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                discharge_date TIMESTAMP,
                status VARCHAR(20) DEFAULT 'admitted',
                notes TEXT
            )
        ''')
        
        # Create patient_locations table
        print("📋 Creating patient_locations table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                hospital VARCHAR(50) NOT NULL,
                department VARCHAR(50) NOT NULL,
                ward VARCHAR(20) NOT NULL,
                bed VARCHAR(10) NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        ''')
        
        # Create patient_vital_signs table
        print("📋 Creating patient_vital_signs table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_vital_signs (
                vital_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                heart_rate INTEGER,
                spo2 INTEGER,
                bp_systolic INTEGER,
                bp_diastolic INTEGER,
                respiratory_rate INTEGER,
                temperature DECIMAL(4,1),
                etco2 INTEGER,
                recorded_by INTEGER,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                FOREIGN KEY (recorded_by) REFERENCES users (id)
            )
        ''')
        
        # Create patient_medical_history table
        print("📋 Creating patient_medical_history table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_medical_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                condition VARCHAR(100) NOT NULL,
                diagnosis_date DATE NOT NULL,
                treatment TEXT,
                medication TEXT,
                notes TEXT,
                recorded_by INTEGER,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                FOREIGN KEY (recorded_by) REFERENCES users (id)
            )
        ''')
        
        # Create user_sessions table
        print("📋 Creating user_sessions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token VARCHAR(128) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("✅ All tables created successfully!")
        
        # Check if users already exist
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("👥 Creating sample users...")
            
            # Simple password hashing function
            def hash_password(password):
                return hashlib.sha256(password.encode()).hexdigest()
            
            # Create sample users
            users = [
                ('admin', 'admin@hospital.com', hash_password('admin'), 'System', 'Administrator', 'admin', None),
                ('doctor', 'doctor@hospital.com', hash_password('doctor'), 'John', 'Smith', 'doctor', 'Cardiology'),
                ('nurse', 'nurse@hospital.com', hash_password('nurse'), 'Sarah', 'Johnson', 'nurse', 'Cardiology'),
                ('tech', 'tech@hospital.com', hash_password('tech'), 'David', 'Brown', 'technician', 'Radiology')
            ]
            
            cursor.executemany('''
                INSERT INTO users (username, email, password_hash, first_name, last_name, role, department)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', users)
            
            print("✅ Sample users created successfully!")
            
            print("🏥 Creating sample patients...")
            
            # Create sample patients
            for i in range(1, 16):
                dob = datetime.now() - timedelta(days=random.randint(7300, 25550))  # 20-70 years old
                admission_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                cursor.execute('''
                    INSERT INTO patients (mrn, first_name, last_name, date_of_birth, gender, blood_type, admission_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"MRN{i:06d}",
                    f"Patient{i}",
                    "Test",
                    dob.date(),
                    random.choice(['male', 'female']),
                    random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                    admission_date,
                    random.choice(['admitted', 'stable', 'critical'])
                ))
            
            print("✅ Sample patients created successfully!")
            
            # Create patient locations
            print("📍 Creating patient locations...")
            departments = ['Cardiology', 'Neurology', 'Orthopedics', 'Emergency', 'ICU']
            
            for i in range(1, 16):
                department = random.choice(departments)
                ward = f"{department[0]}{random.randint(1, 5)}"
                
                cursor.execute('''
                    INSERT INTO patient_locations (patient_id, hospital, department, ward, bed, assigned_at, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    i,
                    'Main Hospital',
                    department,
                    ward,
                    f"{random.randint(1, 20)}",
                    datetime.now() - timedelta(days=random.randint(1, 30)),
                    1
                ))
            
            print("✅ Patient locations created successfully!")
            
            # Create vital signs
            print("💓 Creating vital signs...")
            
            for i in range(1, 16):
                for j in range(3):
                    recorded_at = datetime.now() - timedelta(hours=j*8)
                    
                    cursor.execute('''
                        INSERT INTO patient_vital_signs (patient_id, heart_rate, spo2, bp_systolic, bp_diastolic, respiratory_rate, temperature, etco2, recorded_by, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        i,
                        random.randint(60, 100),
                        random.randint(95, 100),
                        random.randint(110, 140),
                        random.randint(70, 90),
                        random.randint(12, 20),
                        round(random.uniform(36.5, 37.5), 1),
                        random.randint(35, 45),
                        random.choice([2, 3]),  # doctor or nurse
                        recorded_at
                    ))
            
            print("✅ Vital signs created successfully!")
            
            # Create medical history
            print("📋 Creating medical history...")
            conditions = [
                'Hypertension', 'Diabetes Type 2', 'Asthma', 'Pneumonia', 
                'Broken Arm', 'Appendicitis', 'Heart Attack', 'Stroke',
                'Allergic Reaction', 'COVID-19'
            ]
            
            for i in random.sample(range(1, 16), 8):  # Only add history for 8 random patients
                cursor.execute('''
                    INSERT INTO patient_medical_history (patient_id, condition, diagnosis_date, treatment, medication, notes, recorded_by, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    i,
                    random.choice(conditions),
                    (datetime.now() - timedelta(days=random.randint(1, 10))).date(),
                    "Standard protocol treatment",
                    "Various medications as prescribed",
                    "Patient responding well to treatment",
                    2,  # doctor
                    datetime.now() - timedelta(days=random.randint(1, 30))
                ))
            
            print("✅ Medical history created successfully!")
            
            conn.commit()
            
            print("\n🎉 Database initialization complete!")
            print("\n📝 Default Login Credentials:")
            print("   Admin:     username=admin,     password=admin")
            print("   Doctor:    username=doctor,    password=doctor")
            print("   Nurse:     username=nurse,     password=nurse")
            print("   Tech:      username=tech,      password=tech")
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM patients")
            patient_count = cursor.fetchone()[0]
            
            print(f"\n📊 Created {user_count} users and {patient_count} patients")
            
        else:
            print(f"ℹ️  Database already contains {user_count} users. Skipping initialization.")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    create_database()
