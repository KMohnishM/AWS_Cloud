import requests
import json
import sys
import time
from datetime import datetime

def query_prometheus(url, query):
    """Query Prometheus for metrics"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Querying: {query}")
        print(f"[{timestamp}] URL: {url}/api/v1/query?query={query}")
        
        # Set a timeout to avoid hanging requests
        response = requests.get(
            f"{url}/api/v1/query",
            params={"query": query},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "success" and result["data"]["resultType"] == "vector":
                result_count = len(result["data"]["result"])
                print(f"[{timestamp}] Retrieved {result_count} results")
                
                # Print full JSON for inspection
                print("\nRESULT JSON:")
                print(json.dumps(result, indent=2))
                
                # Print formatted results for better readability
                if result_count > 0:
                    print("\nFORMATTED RESULTS:")
                    for i, item in enumerate(result["data"]["result"]):
                        print(f"\nResult {i+1}:")
                        
                        # Print metric details
                        if "metric" in item:
                            print("  Metric:")
                            for key, value in item["metric"].items():
                                print(f"    {key}: {value}")
                        
                        # Print value
                        if "value" in item:
                            # Value is [timestamp, value_string]
                            timestamp_val = item["value"][0]
                            value = item["value"][1]
                            human_time = datetime.fromtimestamp(timestamp_val).strftime('%Y-%m-%d %H:%M:%S')
                            print(f"  Value: {value}")
                            print(f"  Timestamp: {human_time}")
                
                return result["data"]["result"]
            else:
                print(f"[{timestamp}] Query returned unexpected format: {result['status']}")
                print("Full response:")
                print(json.dumps(result, indent=2))
                return []
        else:
            print(f"[{timestamp}] Query failed with status code: {response.status_code}")
            print(f"[{timestamp}] Response: {response.text[:200]}")
            return []
    except Exception as e:
        print(f"Error querying Prometheus: {str(e)}")
        return []

def get_patient_metrics(prometheus_url):
    """Get and format patient metrics from Prometheus"""
    print("Gathering patient metrics from Prometheus...")
    
    # Get patient count
    print("\n===== PATIENT COUNT =====")
    patient_count_result = query_prometheus(prometheus_url, "count(patient_heart_rate)")
    
    if patient_count_result and len(patient_count_result) > 0:
        total_patients = int(float(patient_count_result[0]["value"][1]))
        print(f"\nDetected {total_patients} total patients in Prometheus")
    else:
        print("\nFailed to get patient count from Prometheus")
    
    # Get heart rates
    print("\n===== PATIENT HEART RATES =====")
    heart_rates = query_prometheus(prometheus_url, "patient_heart_rate")
    
    if heart_rates:
        print(f"\nFound heart rates for {len(heart_rates)} patients")
    else:
        print("\nNo heart rate data found")
    
    # Get anomaly scores
    print("\n===== PATIENT ANOMALY SCORES =====")
    anomaly_scores = query_prometheus(prometheus_url, "patient_anomaly_score")
    
    if anomaly_scores:
        print(f"\nFound anomaly scores for {len(anomaly_scores)} patients")
    else:
        print("\nNo anomaly score data found")

if __name__ == "__main__":
    # Default Prometheus URL
    prometheus_url = "http://localhost:9090"
    
    # Check if URL is provided as command line argument
    if len(sys.argv) > 1:
        prometheus_url = sys.argv[1]
    
    print(f"Using Prometheus URL: {prometheus_url}")
    
    # Run the queries
    get_patient_metrics(prometheus_url)