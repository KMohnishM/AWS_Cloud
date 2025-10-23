# Patient Data Integration

This document explains how patient data is integrated between the patient simulator and web dashboard components.

## Overview

The system has been updated to share patient data directly between the patient simulator and web dashboard. This eliminates the need for separate data initialization processes and ensures data consistency across components.

## Data Flow

1. The patient simulator reads patient data from Excel files located in `/app/data/patients_data.xlsx`
2. The web dashboard now reads from the same data source
3. Docker volumes ensure that both services access the same files

## Key Components

### 1. Docker Volume Configuration

Both services share the patient data through a mounted volume:

```yaml
volumes:
  - ./data/patient_samples:/app/data
```

### 2. Patient Data Synchronization

The web dashboard includes a `sync_patients.py` script that:
- Reads patient data directly from the Excel file
- Creates corresponding database records
- Preserves all attributes from the patient simulator in the `extra_data` field

### 3. Automatic Synchronization

The web dashboard's `app.py` automatically synchronizes with the patient simulator data on startup when no existing patient records are found.

## Manual Synchronization

You can manually synchronize patient data by running:

```bash
cd services/web_dashboard
python sync_patients.py
```

## Troubleshooting

If you encounter data synchronization issues:

1. Verify the patient data file exists at `data/patient_samples/patients_data.xlsx`
2. Check that Docker volumes are correctly mounted
3. Look for error messages in the web dashboard container logs

## Extending the Data Model

If you need to add new fields to patient records:

1. Update the Patient models in `services/web_dashboard/models/patient.py`
2. Use the `extra_data` JSON field for simulator-specific fields
3. Update the sync_patients.py script to include new fields

## Data Persistence

The database is stored in a Docker volume for persistence across container restarts. Patient simulator data is read fresh from the Excel file each time synchronization occurs.