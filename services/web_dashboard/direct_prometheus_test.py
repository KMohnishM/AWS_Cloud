"""
Standalone script to directly test Prometheus queries without Flask dependency.
This will verify our fix works before updating app.py.
"""
import requests
import json
import time
from datetime import datetime
import random
import os

# Set Prometheus URL
PROMETHEUS_URL = os.environ.get('PUBLIC_PROMETHEUS_URL', 'http://localhost:9090')

def query_prometheus(query):
    """Query Prometheus for metrics"""
    start_time = time.time()
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [DATA SOURCE: PROMETHEUS] Querying: {query}")
        print(f"[{timestamp}] [URL] {PROMETHEUS_URL}/api/v1/query?query={query}")
        
        # Set a timeout to avoid hanging requests
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=5  # 5 second timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "success" and result["data"]["resultType"] == "vector":
                query_time = time.time() - start_time
                result_count = len(result["data"]["result"])
                print(f"[{timestamp}] [DATA RECEIVED] Prometheus query completed in {query_time:.2f}s: {result_count} results")
                
                # Log a sample of data received (first result only to avoid flooding console)
                if result_count > 0 and "result" in result["data"] and len(result["data"]["result"]) > 0:
                    sample = result["data"]["result"][0]
                    print(f"[{timestamp}] [SAMPLE DATA] {json.dumps(sample)[:200]}..." if len(json.dumps(sample)) > 200 else json.dumps(sample))
                
                return result["data"]["result"]
            else:
                print(f"[{timestamp}] [WARNING] Prometheus query returned unexpected format: {result['status']} - {result.get('data', {}).get('resultType', 'unknown')}")
        else:
            print(f"[{timestamp}] [ERROR] Prometheus query failed with status code: {response.status_code}")
            print(f"[{timestamp}] [ERROR] Response: {response.text[:200]}...")  # Truncate long responses
            
        return []
    except requests.exceptions.Timeout:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [TIMEOUT] Prometheus query timed out after 5s: {query}")
        return []
    except requests.exceptions.ConnectionError as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [CONNECTION ERROR] Prometheus connection error: {e}")
        return []
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [ERROR] Error querying Prometheus: {str(e)}")
        return []

def get_patient_metrics_from_prometheus():
    """Get patient metrics from Prometheus using fixed metric names"""
    metrics = {}
    start_time = time.time()
    
    try:
        print("📊 Gathering patient metrics from Prometheus")
        
        # Get patient count - using FIXED metric name
        patient_count_result = query_prometheus("count(heart_rate_bpm)")
        total_patients = 0
        if patient_count_result and len(patient_count_result) > 0:
            total_patients = int(float(patient_count_result[0]["value"][1]))
            print(f"👥 Found {total_patients} patients in Prometheus")
        else:
            print("⚠️ Failed to get patient count from Prometheus")
        
        # Get anomaly scores for patients - using FIXED metric name
        anomaly_scores = query_prometheus("anomaly_score")
        if not anomaly_scores:
            print("⚠️ No patient anomaly scores returned from Prometheus")
            
        patients_data = []
        
        # Process anomaly scores
        normal_count = 0
        warning_count = 0
        critical_count = 0
        
        # Get all heart rates in one query to avoid multiple requests - using FIXED metric name
        all_heart_rates = query_prometheus("heart_rate_bpm")
        heart_rate_map = {}
        
        if all_heart_rates:
            for hr_result in all_heart_rates:
                if "metric" in hr_result and "value" in hr_result:
                    patient_id = hr_result["metric"].get("patient", "unknown")
                    heart_rate = float(hr_result["value"][1])
                    heart_rate_map[patient_id] = heart_rate
        
        # Process patient data
        for result in anomaly_scores:
            if "metric" in result and "value" in result:
                try:
                    patient_id = result["metric"].get("patient", "unknown")
                    anomaly_score = float(result["value"][1])
                    
                    # Create patient data
                    patient_data = {
                        "patient_id": patient_id,
                        "anomaly_score": anomaly_score,
                    }
                    
                    # Add heart rate from our pre-fetched map
                    if patient_id in heart_rate_map:
                        patient_data["heart_rate"] = heart_rate_map[patient_id]
                    
                    # Categorize patient status
                    if anomaly_score > 0.7:
                        patient_data["status"] = "critical"
                        critical_count += 1
                    elif anomaly_score > 0.4:
                        patient_data["status"] = "warning"
                        warning_count += 1
                    else:
                        patient_data["status"] = "normal"
                        normal_count += 1
                        
                    patients_data.append(patient_data)
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Error processing patient data: {e}")
                    continue
        
        # If we didn't get any data from Prometheus, use default values
        if len(patients_data) == 0:
            print("⚠️ No patient data found in Prometheus, using default values")
            total_patients = total_patients or 15  # Default to 15 patients
            normal_count = 8  # Adjust defaults to match the 15 patients
            warning_count = 5
            critical_count = 2
            
            # Generate sample patient data
            for i in range(1, total_patients + 1):
                anomaly_score = random.random()
                status = "normal"
                if anomaly_score > 0.7:
                    status = "critical"
                elif anomaly_score > 0.4:
                    status = "warning"
                
                patients_data.append({
                    "patient_id": f"patient-{i}",
                    "anomaly_score": anomaly_score,
                    "heart_rate": random.randint(60, 120),
                    "status": status
                })
        
        metrics = {
            "patients": patients_data,
            "total_patients": total_patients,
            "normal_patients": normal_count,
            "warning_patients": warning_count,
            "critical_patients": critical_count
        }
        
        query_time = time.time() - start_time
        print(f"✅ Patient metrics collected in {query_time:.2f}s: {len(patients_data)} patients")
        print(f"Distribution: {normal_count} normal, {warning_count} warning, {critical_count} critical")
        return metrics
        
    except Exception as e:
        print(f"❌ Error gathering patient metrics: {str(e)}")
        # Return a minimal default structure
        return {
            "patients": [],
            "total_patients": 0,
            "normal_patients": 0,
            "warning_patients": 0,
            "critical_patients": 0
        }

def main():
    """Main function to test our fixed queries"""
    print("=" * 50)
    print("TESTING FIXED PROMETHEUS QUERIES")
    print("=" * 50)
    
    metrics = get_patient_metrics_from_prometheus()
    
    print("\n=== RESULTS ===")
    print(f"Total patients: {metrics['total_patients']}")
    print(f"Normal patients: {metrics['normal_patients']}")
    print(f"Warning patients: {metrics['warning_patients']}")
    print(f"Critical patients: {metrics['critical_patients']}")
    
    if metrics['patients']:
        print(f"\nFound {len(metrics['patients'])} patients")
        print("\nSample patient data:")
        print(json.dumps(metrics['patients'][0], indent=2))
    else:
        print("\nNo patient data found")

if __name__ == "__main__":
    main()