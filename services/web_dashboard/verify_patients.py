#!/usr/bin/env python3
"""
Verify that patients match the patient simulator format
"""
from app import app
from models.patient import Patient, PatientVitalSign, PatientLocation
from database import db
import json

with app.app_context():
    # Count patients and vitals
    patients = Patient.query.all()
    vitals_count = PatientVitalSign.query.count()
    locations_count = PatientLocation.query.count()
    
    print(f"Total patients: {len(patients)}")
    print(f"Total vital sign records: {vitals_count}")
    print(f"Total location records: {locations_count}")
    print("\nSAMPLE PATIENT DATA:")
    
    # Show first 3 patients
    for p in patients[:3]:
        print(f"\nPatient {p.patient_id}: {p.first_name} {p.last_name}")
        
        # Get location
        location = PatientLocation.query.filter_by(patient_id=p.patient_id).first()
        if location:
            print(f"  Location: Hospital {location.hospital}, Dept {location.department}, Ward {location.ward}")
        
        # Get vitals
        vitals = PatientVitalSign.query.filter_by(patient_id=p.patient_id).first()
        if vitals:
            print(f"  Vitals: HR={vitals.heart_rate}, SPO2={vitals.spo2}, BP={vitals.bp_systolic}/{vitals.bp_diastolic}")
            
            if vitals.extra_data:
                try:
                    extra = json.loads(vitals.extra_data)
                    print(f"  Extra data: {json.dumps(extra, indent=2)}")
                except:
                    print(f"  Extra data (raw): {vitals.extra_data}")