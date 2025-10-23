@echo off
echo Starting WebSocket test application...

REM Set environment variables for localhost testing
set PUBLIC_PROMETHEUS_URL=http://localhost:9090
set PUBLIC_GRAFANA_URL=http://localhost:3001
set PUBLIC_ALERTMANAGER_URL=http://localhost:9093
set PUBLIC_MAIN_HOST_URL=http://localhost:8000
set PUBLIC_ML_SERVICE_URL=http://localhost:6000

echo Using Prometheus at: %PUBLIC_PROMETHEUS_URL%

REM Install required packages
pip install flask flask-socketio eventlet requests

REM Run the application
python websocket_test_app.py

pause