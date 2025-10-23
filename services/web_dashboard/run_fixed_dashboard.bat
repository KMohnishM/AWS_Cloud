@echo off
echo Running fixed dashboard with all patients displayed...

REM Set environment variables for localhost testing
set PUBLIC_PROMETHEUS_URL=http://localhost:9090
set PUBLIC_GRAFANA_URL=http://localhost:3001
set PUBLIC_ALERTMANAGER_URL=http://localhost:9093
set PUBLIC_MAIN_HOST_URL=http://localhost:8000
set PUBLIC_ML_SERVICE_URL=http://localhost:6000

echo Using Prometheus at: %PUBLIC_PROMETHEUS_URL%

REM Activate any virtual environment if needed
REM call venv\Scripts\activate

REM Install requirements if needed
pip install -r requirements.txt

REM Run the application
python app.py

pause