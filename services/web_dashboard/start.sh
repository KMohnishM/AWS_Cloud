#!/bin/bash

# Hospital Monitoring Dashboard Startup Script

echo "🏥 Starting Hospital Monitoring Dashboard..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the web_dashboard directory."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Make sure database instance directory exists
mkdir -p /app/instance

# Initialize patient data
echo "🏥 Initializing patient data..."
python3 initialize_patient_data.py

# Start the application
echo "🚀 Starting the application..."
echo "📱 Dashboard will be available at: http://localhost:5000"
echo "🔑 Default login: username=admin, password=admin"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py