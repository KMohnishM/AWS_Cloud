# Hospital Dashboard Quick Reference

## Running the Fixed Dashboard

To run the dashboard with the fix for consistently showing 15 patients, use the batch file:

```
run_fixed_15_patients.bat
```

This script:
1. Sets all required environment variables
2. Starts the Flask application with all our fixes applied
3. Ensures the dashboard will show 15 patients consistently

## Validating the Fix

To check if the patient data function is working correctly without starting the full application:

```
python validate_patient_count.py
```

This will:
1. Import the patient data function from app.py
2. Call it directly to check if it returns 15 patients
3. Display the distribution of patient statuses
4. Show a sample of the patient data

## Documentation

For a complete explanation of the issue and the fixes implemented, see:

```
PATIENT_COUNT_FIX_REPORT.md
```

## Original Files

The original application files remain unchanged. The fixes have been applied to the main `app.py` file.

## Troubleshooting

If the dashboard still shows inconsistent patient counts:

1. Check that Prometheus is running: `http://localhost:9090`
2. Verify browser console for any WebSocket errors
3. Ensure no other processes are modifying the patient data
4. Restart all services using Docker if necessary: `docker-compose down && docker-compose up`