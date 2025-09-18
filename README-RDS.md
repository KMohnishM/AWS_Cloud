# Hospital Monitoring System with Amazon RDS Integration

## Overview

This project is a comprehensive hospital monitoring system that collects, analyzes, and visualizes patient vital signs in real-time. The system uses Prometheus for metrics collection, Grafana for visualization, and now integrates with Amazon RDS for secure and scalable data storage.

## Architecture

![Architecture Diagram](./Images/architecture.jpg)

The system consists of the following components:

1. **Main Host**: Flask application that serves as the central hub for collecting and processing patient data
2. **ML Service**: Anomaly detection service using Isolation Forest algorithm
3. **Patient Service**: Generates and sends simulated patient data
4. **Prometheus**: Time-series database for metrics collection
5. **Alert Manager**: Handles alert notifications based on rules
6. **Grafana**: Visualization dashboard for patient vital signs
7. **Web Dashboard**: User interface for monitoring patients and managing the system
8. **Amazon RDS**: Relational database for persistent storage of user authentication and patient details

## Amazon RDS Integration

The system now uses Amazon RDS (MySQL) for storing:

1. User authentication data (login credentials, sessions)
2. Comprehensive patient information
3. Medical history and vital sign records
4. Location tracking within the hospital

### Setting Up Amazon RDS

1. Create an Amazon RDS MySQL instance in your AWS account:
   - Go to AWS Console > RDS > Create database
   - Select MySQL
   - Choose an appropriate instance size (db.t3.micro is sufficient for testing)
   - Configure storage (20GB minimum recommended)
   - Set up admin credentials
   - Make sure to enable public accessibility for development (disable in production)
   - Create a security group that allows connections from your application's IP

2. Configure the `.env` file with your RDS credentials:
   ```
   RDS_USERNAME=admin
   RDS_PASSWORD=Zvg3NRkRiLkX6qlub6Mc
   RDS_HOSTNAME=database-1.cxkucyeociny.ap-south-1.rds.amazonaws.com
   RDS_PORT=3306
   RDS_DB_NAME=database-1
   ```

3. Create the database on your RDS instance:
   ```sql
   USE database-1;
   
   -- Run the database_init.sql script to create all required tables
   -- You can do this by connecting to your RDS instance with a MySQL client:
   -- mysql -h database-1.cxkucyeociny.ap-south-1.rds.amazonaws.com -u admin -p database-1 < database_init.sql
   ```

4. The application will automatically create the necessary tables on first run.

## Running the Application with RDS

To run the application with Amazon RDS integration:

### 1. Configure Your AWS RDS Instance

Before initializing the database, make sure your RDS instance is properly configured:

1. **Enable Public Accessibility**:
   - In the AWS RDS Console, make sure your database has "Public accessibility" set to "Yes"

2. **Configure Security Group**:
   - Add an inbound rule to your RDS security group:
     - Type: MySQL/Aurora (port 3306)
     - Source: Your IP address (or 0.0.0.0/0 for any IP - not recommended for production)

3. **Verify Instance Status**:
   - Check that your RDS instance status is "Available"

### 2. Initialize the RDS Database

You have two options to initialize the database:

#### Option 1: Using Docker with the bash script (Linux/Mac/WSL):
```bash
# Make the script executable
chmod +x initialize_rds.sh

# Run the initialization script
./initialize_rds.sh
```

#### Option 2: Using PowerShell script (Windows):
```powershell
# Run the PowerShell initialization script
.\Initialize-RDS.ps1
```

These scripts will:
1. Test connectivity to your RDS instance
2. Connect to your RDS instance
3. Create the necessary database tables
4. Set up initial data including admin user

If you encounter connection issues, see the `RDS-Troubleshooting.md` file for detailed guidance.

### 3. Start the Application with RDS

```bash
# Start the application with RDS integration
docker-compose -f docker-compose-with-rds.yml up -d

# Access the web dashboard at http://localhost:5000
# Access Grafana at http://localhost:3001 (admin/admin)
```

## Features

- **User Authentication**: Secure login system with role-based access control
- **Patient Management**: Add, view, edit, and delete patient records
- **Real-time Monitoring**: Live dashboard of patient vital signs
- **Anomaly Detection**: ML-based detection of abnormal vital signs
- **Alerting**: Immediate notifications for critical patient conditions
- **Reporting**: Generate reports on patient status and system performance
- **Persistent Storage**: All data securely stored in Amazon RDS

## Security Considerations

For production deployment:

1. Use a secure, randomly generated SECRET_KEY
2. Store credentials in AWS Secrets Manager, not in environment variables
3. Enable SSL/TLS for RDS connections
4. Use IAM authentication for database access
5. Implement a VPC for your RDS instance and only allow connections from your application
6. Enable encryption at rest for your RDS instance
7. Regularly back up your database

## License

This project is licensed under the MIT License - see the LICENSE file for details.