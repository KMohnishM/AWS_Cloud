"""
This script will apply the necessary fixes to app.py to correct the Prometheus metric queries.
"""
import os
import re
import sys
import shutil
from pathlib import Path

def backup_app_py():
    """Create a backup of app.py before making changes."""
    app_path = Path('app.py')
    backup_path = Path('app.py.bak')
    
    if not app_path.exists():
        print(f"❌ app.py not found in {os.getcwd()}")
        return False
    
    try:
        shutil.copy2(app_path, backup_path)
        print(f"✅ Created backup at {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False

def fix_prometheus_queries():
    """Fix the Prometheus query metric names in app.py."""
    app_path = Path('app.py')
    
    try:
        # Read the content of app.py
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Fix the patient count query
        content = re.sub(
            r'patient_count_result = query_prometheus\("count\(patient_heart_rate\)"\)',
            'patient_count_result = query_prometheus("count(heart_rate_bpm)")',
            content
        )
        
        # Fix the anomaly scores query
        content = re.sub(
            r'anomaly_scores = query_prometheus\("patient_anomaly_score"\)',
            'anomaly_scores = query_prometheus("anomaly_score")',
            content
        )
        
        # Fix the heart rates query
        content = re.sub(
            r'all_heart_rates = query_prometheus\("patient_heart_rate"\)',
            'all_heart_rates = query_prometheus("heart_rate_bpm")',
            content
        )
        
        # Write the fixed content back
        with open(app_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Applied fixes to {app_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to apply fixes: {e}")
        return False

def main():
    """Main function to apply fixes."""
    print("=" * 50)
    print("APPLYING PROMETHEUS QUERY FIXES TO APP.PY")
    print("=" * 50)
    
    # Create a backup
    if not backup_app_py():
        print("⚠️ Aborting due to backup failure")
        return
    
    # Apply fixes
    if fix_prometheus_queries():
        print("\n✅ Successfully fixed Prometheus query metric names in app.py")
        print("\nFixes applied:")
        print("1. Changed 'count(patient_heart_rate)' to 'count(heart_rate_bpm)'")
        print("2. Changed 'patient_anomaly_score' to 'anomaly_score'")
        print("3. Changed 'patient_heart_rate' to 'heart_rate_bpm'")
        
        print("\nThese fixes will ensure that app.py correctly queries the metrics that")
        print("exist in Prometheus, allowing it to get data for all 15 patients instead")
        print("of falling back to the default values.")
    else:
        print("\n❌ Failed to apply fixes to app.py")

if __name__ == "__main__":
    main()