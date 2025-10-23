@echo off
echo 🏥 Starting Hospital Monitoring Dashboard...

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: app.py not found. Please run this script from the web_dashboard directory.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing requirements...
pip install -r requirements.txt

REM Make sure instance directory exists
if not exist "instance" (
    mkdir instance
)

REM Initialize patient data
echo 🏥 Initializing patient data...
python initialize_patient_data.py

REM Start the application
echo 🚀 Starting the application...
echo 📱 Dashboard will be available at: http://localhost:5000
echo 🔑 Default login: username=admin, password=admin
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
