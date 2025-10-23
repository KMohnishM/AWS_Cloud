@echo off
echo Hospital Dashboard Service - Fix and Restart
echo ==========================================
echo.
echo Step 1: Running diagnostics...
python diagnose_dashboard.py
echo.

echo Step 2: Stopping any existing dashboard processes...
taskkill /F /IM python.exe /T 2>nul
echo.

echo Step 3: Configuring environment...
set PUBLIC_PROMETHEUS_URL=http://localhost:9090
set PUBLIC_GRAFANA_URL=http://localhost:3001
set PUBLIC_ALERTMANAGER_URL=http://localhost:9093
set PUBLIC_MAIN_HOST_URL=http://localhost:8000
set PUBLIC_ML_SERVICE_URL=http://localhost:6000
echo Environment variables set.
echo.

echo Step 4: Installing required packages...
pip install -r requirements.txt
echo.

echo Step 5: Starting dashboard...
echo The dashboard will start in a new window.
echo.
echo WebSocket testing page will be available at: http://localhost:5000/test
echo Main dashboard will be available at: http://localhost:5000/dashboard
echo.
echo Press any key to continue...
pause >nul

start cmd /k python websocket_test_app.py

echo Done! Dashboard started in a new window.
echo.
echo You can now test the WebSocket connection at: http://localhost:5000/test
echo.