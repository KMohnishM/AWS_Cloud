@echo off
echo ===============================================
echo Hospital Dashboard - Fixed Prometheus Queries
echo ===============================================
echo.

echo Setting up environment variables...
set PUBLIC_PROMETHEUS_URL=http://localhost:9090
set PUBLIC_GRAFANA_URL=http://localhost:3001
set PUBLIC_ALERTMANAGER_URL=http://localhost:9093
set PUBLIC_MAIN_HOST_URL=http://localhost:8000
set PUBLIC_ML_SERVICE_URL=http://localhost:6000

echo.
echo Starting dashboard application with fixed Prometheus queries...
echo.
echo IMPORTANT: 
echo - The dashboard now correctly queries Prometheus for metrics
echo - All 15 patients will be displayed consistently
echo - The Prometheus query fix has been applied
echo.

cd "c:\Users\kmohn\New folder\AWS_Cloud\services\web_dashboard"
python app.py

pause