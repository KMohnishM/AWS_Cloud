#!/usr/bin/env python3
"""
Script to diagnose database connection issues.
Run this inside the Docker container to check database state.
"""
import os
import sqlite3
from pathlib import Path

def main():
    """Check database status and accessibility"""
    print("Database Diagnostic Tool")
    print("------------------------")
    
    # Check instance directory
    instance_path = Path('/app/instance')
    print(f"Checking instance directory: {instance_path}")
    
    if not instance_path.exists():
        print("ERROR: Instance directory does not exist!")
        print("Creating directory...")
        os.makedirs(instance_path, exist_ok=True)
    else:
        print("Instance directory exists")
    
    # Check permissions
    perms = oct(os.stat(instance_path).st_mode)[-3:]
    print(f"Instance directory permissions: {perms}")
    
    # List files in instance directory
    print("\nFiles in instance directory:")
    files = list(instance_path.glob('*'))
    if files:
        for file in files:
            size = os.path.getsize(file)
            perms = oct(os.stat(file).st_mode)[-3:]
            print(f"  - {file.name} ({size} bytes, permissions: {perms})")
    else:
        print("  No files found!")
    
    # Check SQLite database
    db_path = instance_path / 'healthcare.db'
    print(f"\nChecking SQLite database: {db_path}")
    
    if not db_path.exists():
        print("ERROR: Database file does not exist!")
    else:
        print(f"Database file exists ({os.path.getsize(db_path)} bytes)")
        
        # Try to open the database
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables
            print("\nDatabase tables:")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if tables:
                for table in tables:
                    print(f"  - {table[0]}")
                    
                    # Count rows
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                        count = cursor.fetchone()[0]
                        print(f"    ({count} rows)")
                    except sqlite3.Error as e:
                        print(f"    Error counting rows: {e}")
            else:
                print("  No tables found!")
                
            conn.close()
            
        except sqlite3.Error as e:
            print(f"ERROR opening database: {e}")
    
    print("\nDiagnosis complete.")

if __name__ == "__main__":
    main()