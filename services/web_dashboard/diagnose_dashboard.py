import requests
import time
import sys
import json

def check_prometheus_patients():
    """Check Prometheus for patient data and display results"""
    prometheus_url = "http://localhost:9090"
    
    try:
        # Check if Prometheus is reachable
        print(f"Checking Prometheus at {prometheus_url}...")
        health_response = requests.get(f"{prometheus_url}/-/healthy", timeout=3)
        
        if health_response.status_code == 200:
            print("✅ Prometheus is healthy")
            
            # Query patient count
            print("\nQuerying for patient count...")
            count_response = requests.get(
                f"{prometheus_url}/api/v1/query",
                params={"query": "count(patient_heart_rate)"},
                timeout=5
            )
            
            if count_response.status_code == 200:
                count_data = count_response.json()
                
                if count_data["status"] == "success":
                    # Check if we have results
                    if len(count_data["data"]["result"]) > 0:
                        count_value = float(count_data["data"]["result"][0]["value"][1])
                        print(f"✅ Found {int(count_value)} patient(s) in Prometheus")
                    else:
                        print("❌ No patient count results returned from Prometheus")
                        print("Generating test data may be necessary")
                else:
                    print(f"❌ Prometheus query returned error status: {count_data['status']}")
            else:
                print(f"❌ Failed to query Prometheus: HTTP {count_response.status_code}")
            
            # Query heart rates
            print("\nQuerying for patient heart rates...")
            hr_response = requests.get(
                f"{prometheus_url}/api/v1/query",
                params={"query": "patient_heart_rate"},
                timeout=5
            )
            
            if hr_response.status_code == 200:
                hr_data = hr_response.json()
                
                if hr_data["status"] == "success":
                    heart_rates = hr_data["data"]["result"]
                    if heart_rates:
                        print(f"✅ Found heart rates for {len(heart_rates)} patient(s)")
                        # Display a sample
                        if len(heart_rates) > 0:
                            sample = heart_rates[0]
                            print(f"Sample patient: {sample['metric'].get('patient', 'unknown')}")
                            print(f"Sample heart rate: {float(sample['value'][1])}")
                    else:
                        print("❌ No heart rate data found in Prometheus")
                        print("Generating test data may be necessary")
                else:
                    print(f"❌ Prometheus query returned error status: {hr_data['status']}")
            else:
                print(f"❌ Failed to query heart rates: HTTP {hr_response.status_code}")
        else:
            print(f"❌ Prometheus health check failed: HTTP {health_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Could not connect to Prometheus")
        print("Please check if Prometheus is running")
    except requests.exceptions.Timeout:
        print("❌ Timeout - Prometheus request timed out")
    except Exception as e:
        print(f"❌ Error checking Prometheus: {e}")

def check_websocket_endpoint():
    """Check WebSocket endpoint health"""
    dashboard_url = "http://localhost:5000"
    
    try:
        print(f"Checking dashboard at {dashboard_url}...")
        
        # Check if dashboard is reachable
        dashboard_response = requests.get(dashboard_url, timeout=3)
        
        if dashboard_response.status_code == 200:
            print("✅ Dashboard web server is responding")
            
            # Check WebSocket debug endpoint
            print("Checking WebSocket debug endpoint...")
            ws_debug_response = requests.get(f"{dashboard_url}/api/debug/websocket", timeout=3)
            
            if ws_debug_response.status_code == 200:
                print("✅ WebSocket debug endpoint is accessible")
                
                # Parse response
                try:
                    debug_data = ws_debug_response.json()
                    
                    if debug_data["status"] == "success":
                        ws_info = debug_data.get("debug_info", {})
                        print(f"Server time: {ws_info.get('server_time')}")
                        print(f"WebSocket enabled: {ws_info.get('websocket_enabled', False)}")
                        print(f"Connected clients: {ws_info.get('connected_clients', 0)}")
                        
                        # Check Prometheus connection from dashboard
                        prom_status = ws_info.get("prometheus", {}).get("status", "unknown")
                        prom_latency = ws_info.get("prometheus", {}).get("latency")
                        
                        print(f"Prometheus status from dashboard: {prom_status}")
                        if prom_latency:
                            print(f"Prometheus latency: {prom_latency * 1000:.2f}ms")
                    else:
                        print("❌ WebSocket debug returned error status")
                except ValueError:
                    print("❌ Invalid JSON response from WebSocket debug endpoint")
            else:
                print(f"❌ WebSocket debug endpoint returned: HTTP {ws_debug_response.status_code}")
                
            # Check ping endpoint
            print("\nChecking API ping endpoint...")
            ping_response = requests.get(f"{dashboard_url}/api/ping", timeout=3)
            
            if ping_response.status_code == 200:
                print("✅ API ping endpoint is responding")
                try:
                    ping_data = ping_response.json()
                    print(f"API timestamp: {ping_data.get('timestamp')}")
                except ValueError:
                    print("❌ Invalid JSON response from ping endpoint")
            else:
                print(f"❌ API ping endpoint returned: HTTP {ping_response.status_code}")
                
        else:
            print(f"❌ Dashboard is not responding: HTTP {dashboard_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Could not connect to dashboard")
        print("Please check if the dashboard server is running")
    except requests.exceptions.Timeout:
        print("❌ Timeout - Dashboard request timed out")
    except Exception as e:
        print(f"❌ Error checking dashboard: {e}")

if __name__ == "__main__":
    print("🏥 Hospital Dashboard Diagnostic Tool 🏥")
    print("="*50)
    
    # Check Prometheus
    print("\n📊 CHECKING PROMETHEUS DATA SOURCE")
    print("-"*50)
    check_prometheus_patients()
    
    # Check WebSocket
    print("\n🔌 CHECKING WEBSOCKET CONNECTIVITY")
    print("-"*50)
    check_websocket_endpoint()
    
    print("\n✨ Diagnostics complete!")
    print("If both Prometheus and WebSocket are working but the dashboard still shows")
    print("only 5 patients, please restart the dashboard server with the fixes applied.")