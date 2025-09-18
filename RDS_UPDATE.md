# RDS Integration Update

The project has been updated to connect to the Amazon RDS MySQL database with the following details:

- **Database Host**: database-1.cxkucyeociny.ap-south-1.rds.amazonaws.com
- **Database Port**: 3306
- **Database Name**: database-1
- **Database User**: admin

## Changes Made

1. Updated `.env` file with correct RDS credentials
2. Updated `docker-compose-with-rds.yml` to use environment variables
3. Created `database_init.sql` script to initialize the database schema
4. Created `initialize_rds.sh` script to connect to and initialize the RDS database
5. Updated `README-RDS.md` with specific connection information

## How to Use

1. Initialize the RDS database:
   ```bash
   chmod +x initialize_rds.sh
   ./initialize_rds.sh
   ```

2. Start the application with RDS integration:
   ```bash
   docker-compose -f docker-compose-with-rds.yml up -d
   ```

## Security Note

For production environments, consider:
1. Storing credentials in AWS Secrets Manager instead of environment variables
2. Setting up VPC peering for secure connections
3. Enabling SSL/TLS for database connections
4. Implementing IAM authentication for RDS

## Database Schema

The RDS database has been configured with the following tables:
- `users` - User authentication and profile information
- `user_sessions` - User session tracking
- `patients` - Patient profile information
- `patient_locations` - Track patient room/bed assignments
- `patient_vital_signs` - Store patient vital sign measurements
- `patient_medical_history` - Track medical history entries
- `emergency_contacts` - Store patient emergency contacts

Each table includes appropriate foreign key relationships and timestamps.

## Sample Data

The initialization script includes:
- Default admin user (username: admin, password: admin)
- Three sample patients
- Sample location data for the patients

Change the admin password immediately for production use.