import socket
import requests
import time
import sys

def check_port_open(host, port, timeout=2):
    """Check if a port is open on the host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error checking port {port} on {host}: {e}")
        return False

def check_http_service(url, timeout=3):
    """Check if an HTTP service is responding"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        latency = time.time() - start_time
        
        return {
            "status_code": response.status_code,
            "status": "ok" if response.status_code < 400 else "error",
            "latency_ms": round(latency * 1000, 2),
            "content_length": len(response.content)
        }
    except requests.exceptions.Timeout:
        return {"status": "timeout", "error": "Request timed out"}
    except requests.exceptions.ConnectionError as e:
        return {"status": "connection_error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_services(host="localhost"):
    """Check all services in the hospital monitoring stack"""
    services = {
        "prometheus": 9090,
        "grafana": 3001,  # Note: Different port when mapped to host
        "alertmanager": 9093,
        "web_dashboard": 5000,
        "main_host": 8000,
        "ml_service": 6000,
    }
    
    print(f"Checking services on host: {host}\n")
    
    for service_name, port in services.items():
        print(f"Checking {service_name} (port {port})...")
        
        # Check if port is open
        port_open = check_port_open(host, port)
        print(f"  Port {port} is {'OPEN' if port_open else 'CLOSED'}")
        
        # If port is open, try HTTP request
        if port_open:
            url = f"http://{host}:{port}"
            print(f"  Testing HTTP connection to {url}")
            result = check_http_service(url)
            
            if result["status"] == "ok":
                print(f"  ✅ HTTP service is responding (status {result['status_code']}, latency {result['latency_ms']}ms)")
            else:
                print(f"  ❌ HTTP service error: {result.get('error', 'Unknown error')}")
                
            # Check service specific endpoints
            if service_name == "prometheus":
                # Check Prometheus health endpoint
                health_result = check_http_service(f"{url}/-/healthy")
                if health_result["status"] == "ok":
                    print(f"  ✅ Prometheus health check passed (latency {health_result['latency_ms']}ms)")
                else:
                    print(f"  ❌ Prometheus health check failed: {health_result.get('error', 'Unknown error')}")
                    
                # Try a simple query
                query_url = f"{url}/api/v1/query?query=up"
                query_result = check_http_service(query_url)
                if query_result["status"] == "ok":
                    print(f"  ✅ Prometheus query API is responding (latency {query_result['latency_ms']}ms)")
                else:
                    print(f"  ❌ Prometheus query API error: {query_result.get('error', 'Unknown error')}")
            
            elif service_name == "web_dashboard":
                # Check dashboard ping endpoint
                ping_result = check_http_service(f"{url}/api/ping")
                if ping_result["status"] == "ok":
                    print(f"  ✅ Dashboard ping endpoint is responding (latency {ping_result['latency_ms']}ms)")
                else:
                    print(f"  ❌ Dashboard ping endpoint error: {ping_result.get('error', 'Unknown error')}")
        
        print()  # Empty line between services

if __name__ == "__main__":
    host = "localhost"
    
    # Check if host is provided as argument
    if len(sys.argv) > 1:
        host = sys.argv[1]
    
    check_services(host)