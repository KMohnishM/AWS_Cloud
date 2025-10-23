import os
import requests
import time
from datetime import datetime

def main():
    print("=" * 50)
    print("Dashboard Console Log Source Test")
    print("=" * 50)
    
    print("\nThis test will help verify if the console.log source information modifications are working correctly.")
    print("Please follow these steps:")
    print("1. Restart your web application if it's already running")
    print("2. Open your web browser and navigate to the dashboard")
    print("3. Open the browser's developer console (F12 or right-click > Inspect > Console)")
    print("4. Look for 'Received dashboard stats update' messages")
    print("\nYou should now see [Source: ...] information in the console logs, which will tell you")
    print("whether the data is coming from WebSocket Real-time updates or REST API Fetch fallbacks.")
    
    print("\nChecking if your web server is running...")
    
    # Try to ping the server
    try:
        response = requests.get("http://localhost:5000/api/ping", timeout=3)
        if response.status_code == 200:
            print("✅ Web server is running! You can now check the browser console.")
        else:
            print(f"⚠️ Web server returned status code {response.status_code}. It might not be running properly.")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the web server. Is it running?")
        print("   Start the web server with: python app.py")
    except Exception as e:
        print(f"❌ Error checking web server: {str(e)}")
    
    print("\nTo test both data sources:")
    print("1. For WebSocket updates: Just load the dashboard normally")
    print("2. For REST API updates: Try disabling WebSockets or refreshing manually")
    
    print("\nHappy testing!")

if __name__ == "__main__":
    main()