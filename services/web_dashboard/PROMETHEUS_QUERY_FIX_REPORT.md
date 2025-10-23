# Prometheus Query Fix Report

## Problem Summary
The hospital dashboard was showing inconsistent patient counts because it was querying Prometheus with incorrect metric names. Initial page load would show 15 patients because it was using fallback data, but subsequent WebSocket updates would show 5 patients or empty data.

## Root Cause
The `app.py` file was querying Prometheus with incorrect metric names:
- It was querying for `patient_heart_rate` instead of `heart_rate_bpm`
- It was querying for `patient_anomaly_score` instead of `anomaly_score`
- These queries were returning no data, causing the fallback mechanism to generate a default set of 5 patients

## Detailed Diagnosis
We ran a comprehensive analysis of the Prometheus metrics:

1. We confirmed Prometheus is running and accessible
2. We confirmed that Prometheus contains data for all 15 patients
3. We checked the available metrics in Prometheus and found:
   - `heart_rate_bpm` (not `patient_heart_rate`)
   - `anomaly_score` (not `patient_anomaly_score`)
4. We tested queries and confirmed:
   - `count(heart_rate_bpm)` returns 15
   - `heart_rate_bpm` returns data for 15 patients
   - `anomaly_score` returns data for 15 patients
5. We verified that the incorrect queries in `app.py` were returning empty results

## Solutions Implemented

### 1. Fixed Metric Names
Modified the queries in `get_patient_metrics_from_prometheus()` function:
- Changed `count(patient_heart_rate)` to `count(heart_rate_bpm)`
- Changed `patient_anomaly_score` to `anomaly_score`
- Changed `patient_heart_rate` to `heart_rate_bpm`

### 2. Testing and Validation
Created multiple diagnostic tools to verify the solution:
- `direct_prometheus_test.py` - Tests the corrected queries directly against Prometheus
- `fix_prometheus_queries.py` - Analyzes the available metrics in Prometheus
- `apply_prometheus_fixes.py` - A script that automatically applies the fixes to `app.py`

### 3. Updated Startup Script
Updated `run_fixed_15_patients.bat` to correctly set environment variables and run the dashboard with our fixes.

## Testing Results
- The direct test showed that with the corrected metric names, we successfully retrieve all 15 patients from Prometheus
- The data has proper heart rate and anomaly scores for all 15 patients

## Future Recommendations
1. **Consistent Naming**: Ensure metric names are consistent between Prometheus and the web dashboard
2. **Better Error Handling**: Improve the logging in `query_prometheus` function to be more specific about why queries fail
3. **Validation Testing**: Implement automated tests that verify metric names match before deployment

## Files Modified
- `app.py`: Updated Prometheus query metric names
- Created additional diagnostic tools to validate the solution

## How to Verify
1. Run the dashboard using the updated batch script:
   ```
   run_fixed_15_patients.bat
   ```
2. Check that the dashboard consistently shows 15 patients both on initial load and during subsequent WebSocket updates
3. Verify in the browser console that the WebSocket events are sending complete patient data with 15 records