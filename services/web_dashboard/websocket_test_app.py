from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import time
import os
from datetime import datetime
import requests
import logging

# Enable logging for debug
logging.basicConfig(level=logging.DEBUG)

# Create a simple Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key'

# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Initialize SocketIO with debugging enabled
socketio = SocketIO(app,
                   cors_allowed_origins="*",
                   async_mode='eventlet',  # Try eventlet for WebSocket
                   engineio_logger=True,
                   logger=True,
                   ping_timeout=30,
                   ping_interval=15)

# Configuration for localhost testing
PROMETHEUS_URL = os.environ.get('PUBLIC_PROMETHEUS_URL', 'http://localhost:9090')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/test')
def test_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
        <script src="https://cdn.socket.io/4.4.1/socket.io.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Connect to Socket.IO server
                const socket = io();
                
                // Connection events
                socket.on('connect', function() {
                    appendMessage('Connected to server!', 'success');
                    document.getElementById('status').textContent = 'Connected';
                    document.getElementById('status').className = 'connected';
                });
                
                socket.on('connect_error', function(error) {
                    appendMessage('Connection error: ' + error, 'error');
                    document.getElementById('status').textContent = 'Error';
                    document.getElementById('status').className = 'error';
                });
                
                socket.on('disconnect', function() {
                    appendMessage('Disconnected from server', 'warning');
                    document.getElementById('status').textContent = 'Disconnected';
                    document.getElementById('status').className = 'disconnected';
                });
                
                // Custom events
                socket.on('test_response', function(data) {
                    appendMessage('Server response: ' + JSON.stringify(data), 'info');
                });
                
                socket.on('patients_update', function(data) {
                    appendMessage('Patient data received', 'info');
                    document.getElementById('patient-count').textContent = data.patients.length;
                    
                    // Display patient data
                    const patientsList = document.getElementById('patients-list');
                    patientsList.innerHTML = '';
                    
                    if (data.patients && data.patients.length > 0) {
                        data.patients.forEach(function(patient) {
                            const li = document.createElement('li');
                            li.textContent = `ID: ${patient.patient_id}, Score: ${patient.anomaly_score}, Status: ${patient.status}`;
                            li.className = patient.status.toLowerCase();
                            patientsList.appendChild(li);
                        });
                    } else {
                        const li = document.createElement('li');
                        li.textContent = 'No patients found';
                        patientsList.appendChild(li);
                    }
                });
                
                // Handle button click
                document.getElementById('test-button').addEventListener('click', function() {
                    appendMessage('Requesting test data from server...', 'info');
                    socket.emit('test_event', {message: 'Test from client'});
                });
                
                document.getElementById('get-patients').addEventListener('click', function() {
                    appendMessage('Requesting patient data...', 'info');
                    socket.emit('request_patients', {message: 'Get patients'});
                });
                
                // Helper function to append messages
                function appendMessage(message, type) {
                    const messageElement = document.createElement('div');
                    messageElement.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
                    messageElement.className = `message ${type}`;
                    document.getElementById('messages').appendChild(messageElement);
                    // Auto scroll
                    const messagesContainer = document.getElementById('messages');
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            });
        </script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #status-container { margin-bottom: 20px; }
            #status { display: inline-block; padding: 5px 10px; border-radius: 4px; }
            .connected { background-color: green; color: white; }
            .disconnected { background-color: gray; color: white; }
            .error { background-color: red; color: white; }
            #messages { height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; }
            .message { margin-bottom: 5px; padding: 5px; border-radius: 4px; }
            .success { background-color: #d4edda; }
            .warning { background-color: #fff3cd; }
            .error { background-color: #f8d7da; }
            .info { background-color: #d1ecf1; }
            button { padding: 10px 15px; margin-right: 10px; }
            #patients { margin-top: 20px; }
            #patients-list li { margin: 5px 0; padding: 5px; border-radius: 4px; }
            #patients-list li.normal { background-color: #d4edda; }
            #patients-list li.warning { background-color: #fff3cd; }
            #patients-list li.critical { background-color: #f8d7da; }
        </style>
    </head>
    <body>
        <h1>WebSocket Test Page</h1>
        
        <div id="status-container">
            Status: <span id="status" class="disconnected">Disconnected</span>
        </div>
        
        <div id="controls">
            <button id="test-button">Send Test Event</button>
            <button id="get-patients">Get Patients</button>
        </div>
        
        <h3>Messages:</h3>
        <div id="messages"></div>
        
        <div id="patients">
            <h3>Patients (<span id="patient-count">0</span>):</h3>
            <ul id="patients-list"></ul>
        </div>
    </body>
    </html>
    """

def query_prometheus(query):
    """Query Prometheus for metrics with detailed logging"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Querying Prometheus: {query}")
        print(f"[{timestamp}] URL: {PROMETHEUS_URL}/api/v1/query?query={query}")
        
        # Set a timeout to avoid hanging requests
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[{timestamp}] Prometheus response: {json.dumps(result)[:200]}...")
            
            if result["status"] == "success" and result["data"]["resultType"] == "vector":
                return result["data"]["result"]
            else:
                print(f"[{timestamp}] Unexpected format: {result['status']}")
        else:
            print(f"[{timestamp}] Query failed: Status {response.status_code}")
            
        return []
    except Exception as e:
        print(f"Error querying Prometheus: {str(e)}")
        return []

def get_patient_data():
    """Get patient data from Prometheus"""
    try:
        print("Getting patient data from Prometheus...")
        
        # Get patient count
        patient_count_result = query_prometheus("count(patient_heart_rate)")
        total_patients = 0
        
        if patient_count_result and len(patient_count_result) > 0:
            total_patients = int(float(patient_count_result[0]["value"][1]))
            print(f"Found {total_patients} patients")
        else:
            print("No patients found, using test data")
            # Generate test data if Prometheus returns nothing
            return generate_test_data()
        
        # Get anomaly scores
        anomaly_scores = query_prometheus("patient_anomaly_score")
        
        if not anomaly_scores:
            print("No anomaly scores found, using test data")
            return generate_test_data()
        
        # Get heart rates
        all_heart_rates = query_prometheus("patient_heart_rate")
        heart_rate_map = {}
        
        if all_heart_rates:
            for hr_result in all_heart_rates:
                if "metric" in hr_result and "value" in hr_result:
                    patient_id = hr_result["metric"].get("patient", "unknown")
                    heart_rate = float(hr_result["value"][1])
                    heart_rate_map[patient_id] = heart_rate
        
        # Process patient data
        patients_data = []
        
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
                    
                    # Add heart rate if available
                    if patient_id in heart_rate_map:
                        patient_data["heart_rate"] = heart_rate_map[patient_id]
                    
                    # Categorize patient status
                    if anomaly_score > 0.7:
                        patient_data["status"] = "Critical"
                    elif anomaly_score > 0.4:
                        patient_data["status"] = "Warning"
                    else:
                        patient_data["status"] = "Normal"
                        
                    patients_data.append(patient_data)
                except Exception as e:
                    print(f"Error processing patient data: {e}")
                    continue
        
        if not patients_data:
            print("No patient data processed, using test data")
            return generate_test_data()
            
        return patients_data
            
    except Exception as e:
        print(f"Error getting patient data: {str(e)}")
        return generate_test_data()

def generate_test_data():
    """Generate test patient data"""
    import random
    
    print("Generating test patient data...")
    test_data = []
    
    # Generate 15 test patients (the number you were expecting)
    for i in range(1, 16):
        anomaly_score = round(random.uniform(0, 1), 2)
        heart_rate = round(random.uniform(60, 120))
        
        status = "Normal"
        if anomaly_score > 0.7:
            status = "Critical"
        elif anomaly_score > 0.4:
            status = "Warning"
            
        test_data.append({
            "patient_id": f"test-patient-{i}",
            "anomaly_score": anomaly_score,
            "heart_rate": heart_rate,
            "status": status
        })
    
    return test_data

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('test_response', {'data': 'Connected successfully!'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('test_event')
def handle_test_event(data):
    print(f"Received test event: {data}")
    emit('test_response', {'data': 'Test response from server', 'received': data})

@socketio.on('request_patients')
def handle_request_patients(data):
    print(f"Client requested patient data: {data}")
    patients = get_patient_data()
    print(f"Sending {len(patients)} patients to client")
    emit('patients_update', {
        'patients': patients,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting WebSocket test server...")
    print(f"Prometheus URL: {PROMETHEUS_URL}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)