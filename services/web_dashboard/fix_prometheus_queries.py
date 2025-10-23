"""
Prometheus Query Fix Utility

This script confirms that our Prometheus queries in app.py are using the correct metric names.
In the get_patient_metrics_from_prometheus function, it's looking for:
1. patient_heart_rate - but Prometheus has heart_rate_bpm 
2. patient_anomaly_score - but Prometheus has anomaly_score
"""
import requests
import json
from pprint import pprint

def get_available_metrics():
    """Get list of all metrics available in Prometheus."""
    print("Checking available metrics in Prometheus...")
    try:
        response = requests.get("http://localhost:9090/api/v1/label/__name__/values", timeout=5)
        if response.status_code != 200:
            print(f"❌ Error: Prometheus returned status code {response.status_code}")
            return []
        
        result = response.json()
        if result["status"] == "success" and "data" in result:
            metrics = result["data"]
            print(f"✅ Found {len(metrics)} metrics in Prometheus")
            return metrics
        else:
            print(f"❌ Error: Unexpected response format from Prometheus")
            return []
    except Exception as e:
        print(f"❌ Error querying Prometheus: {str(e)}")
        return []

def check_metric_exists(metric_name):
    """Check if a specific metric exists in Prometheus."""
    try:
        response = requests.get(f"http://localhost:9090/api/v1/query?query={metric_name}", timeout=5)
        if response.status_code != 200:
            print(f"❌ Error: Prometheus returned status code {response.status_code}")
            return False
        
        result = response.json()
        if result["status"] == "success" and result["data"]["resultType"] == "vector":
            result_count = len(result["data"]["result"])
            print(f"✅ Found {result_count} results for metric {metric_name}")
            return result_count > 0
        else:
            print(f"❌ Error: Unexpected response format from Prometheus")
            return False
    except Exception as e:
        print(f"❌ Error querying Prometheus: {str(e)}")
        return False

def test_queries():
    """Test various metric queries to see which ones work."""
    print("\n=== Testing metric queries ===")
    
    test_metrics = [
        # Original queries in app.py
        "count(patient_heart_rate)",
        "patient_heart_rate",
        "patient_anomaly_score",
        
        # Corrected queries based on what we observed
        "count(heart_rate_bpm)",
        "heart_rate_bpm",
        "anomaly_score"
    ]
    
    results = {}
    for metric in test_metrics:
        try:
            print(f"\nTesting query: {metric}")
            response = requests.get(f"http://localhost:9090/api/v1/query?query={metric}", timeout=5)
            
            if response.status_code != 200:
                print(f"❌ Query failed with status code {response.status_code}")
                results[metric] = False
                continue
            
            result = response.json()
            if result["status"] != "success":
                print(f"❌ Query returned non-success status: {result['status']}")
                results[metric] = False
                continue
            
            data_results = result["data"]["result"]
            result_count = len(data_results)
            
            if result_count > 0:
                print(f"✅ Query succeeded with {result_count} results")
                print(f"Sample result: {json.dumps(data_results[0], indent=2)[:200]}...")
                results[metric] = True
            else:
                print(f"❌ Query returned zero results")
                results[metric] = False
                
        except Exception as e:
            print(f"❌ Error executing query: {str(e)}")
            results[metric] = False
    
    return results

def generate_fix():
    """Generate the fix for app.py based on our findings."""
    print("\n=== Generating fix for app.py ===")
    
    # Test our queries first
    query_results = test_queries()
    
    # Determine which metrics work
    heart_rate_metric = "heart_rate_bpm" if query_results.get("heart_rate_bpm", False) else "patient_heart_rate"
    anomaly_metric = "anomaly_score" if query_results.get("anomaly_score", False) else "patient_anomaly_score"
    heart_rate_count = "count(heart_rate_bpm)" if query_results.get("count(heart_rate_bpm)", False) else "count(patient_heart_rate)"
    
    print(f"Based on testing, we should use:")
    print(f"- Heart rate metric: {heart_rate_metric}")
    print(f"- Anomaly metric: {anomaly_metric}")
    print(f"- Heart rate count: {heart_rate_count}")
    
    # Generate the fix
    print("\n=== CODE FIX FOR APP.PY ===")
    print("Find these lines in get_patient_metrics_from_prometheus():")
    print("```python")
    print("        # Get patient count - this is the most critical query")
    print("        patient_count_result = query_prometheus(\"count(patient_heart_rate)\")")
    print("```")
    print("\nReplace with:")
    print("```python")
    print("        # Get patient count - this is the most critical query")
    print(f"        patient_count_result = query_prometheus(\"{heart_rate_count}\")")
    print("```")
    
    print("\nFind these lines:")
    print("```python")
    print("        # Get anomaly scores for patients")
    print("        anomaly_scores = query_prometheus(\"patient_anomaly_score\")")
    print("```")
    print("\nReplace with:")
    print("```python")
    print("        # Get anomaly scores for patients")
    print(f"        anomaly_scores = query_prometheus(\"{anomaly_metric}\")")
    print("```")
    
    print("\nFind these lines:")
    print("```python")
    print("        # Get all heart rates in one query to avoid multiple requests")
    print("        all_heart_rates = query_prometheus(\"patient_heart_rate\")")
    print("```")
    print("\nReplace with:")
    print("```python")
    print("        # Get all heart rates in one query to avoid multiple requests")
    print(f"        all_heart_rates = query_prometheus(\"{heart_rate_metric}\")")
    print("```")

if __name__ == "__main__":
    print("=" * 50)
    print("PROMETHEUS QUERY FIX UTILITY")
    print("=" * 50)
    
    metrics = get_available_metrics()
    if metrics:
        print("\nAvailable metrics in Prometheus:")
        heart_rate_metrics = [m for m in metrics if "heart" in m.lower()]
        anomaly_metrics = [m for m in metrics if "anomaly" in m.lower()]
        
        print("\nHeart Rate related metrics:")
        for metric in heart_rate_metrics:
            print(f"- {metric}")
        
        print("\nAnomaly related metrics:")
        for metric in anomaly_metrics:
            print(f"- {metric}")
    
    generate_fix()