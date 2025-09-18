#!/bin/bash
# This script connects to the RDS database and initializes it with the schema using Docker

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found"
    exit 1
fi

echo "Initializing RDS database at ${RDS_HOSTNAME}..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    echo "Please install Docker to run this script: https://docs.docker.com/get-docker/"
    exit 1
fi

# Test connection to RDS using Docker with MySQL client
echo "Testing connection to RDS..."
echo "Attempting to connect to ${RDS_HOSTNAME} with user ${RDS_USERNAME}..."

# First, test basic network connectivity
echo "Testing basic network connectivity to RDS endpoint..."
if command -v nc &> /dev/null; then
    if nc -z -w5 ${RDS_HOSTNAME} 3306; then
        echo "Network connectivity test successful. Port 3306 is reachable."
    else
        echo "Network connectivity test failed. Cannot reach port 3306 on ${RDS_HOSTNAME}."
        echo "This suggests a network or security group issue."
    fi
elif command -v telnet &> /dev/null; then
    echo "Checking connection with telnet..."
    if timeout 5 telnet ${RDS_HOSTNAME} 3306 </dev/null 2>&1 | grep -q "Connected"; then
        echo "Network connectivity test successful. Port 3306 is reachable."
    else
        echo "Network connectivity test failed. Cannot reach port 3306 on ${RDS_HOSTNAME}."
        echo "This suggests a network or security group issue."
    fi
else
    echo "Neither nc nor telnet is available for basic connectivity testing."
fi

# Now try the full MySQL connection
echo "Testing database connection with credentials..."
docker run --rm mysql:5.7 mysql -h ${RDS_HOSTNAME} -u ${RDS_USERNAME} -p${RDS_PASSWORD} -e "SELECT 'Connection successful!' as Message;"

if [ $? -ne 0 ]; then
    echo "Error: Failed to connect to RDS database"
    echo "Please check:"
    echo "1. Your RDS security group allows connections from your IP address to port 3306"
    echo "2. The RDS instance is publicly accessible"
    echo "3. The RDS instance is in the 'Available' state"
    echo "4. Your network/VPN is not blocking outbound connections to port 3306"
    echo ""
    echo "For detailed troubleshooting steps, see RDS-Troubleshooting.md"
    exit 1
fi

# Create a temporary copy of the init script to fix line endings if needed
sed 's/\r$//' database_init.sql > database_init_unix.sql

# Initialize the database with the schema
echo "Initializing database schema..."
cat database_init_unix.sql | docker run -i --rm mysql:5.7 mysql -h ${RDS_HOSTNAME} -u ${RDS_USERNAME} -p${RDS_PASSWORD} ${RDS_DB_NAME}

if [ $? -ne 0 ]; then
    echo "Error: Failed to initialize database schema"
    rm -f database_init_unix.sql
    exit 1
fi

# Clean up
rm -f database_init_unix.sql

echo "Database initialization complete!"
echo "RDS database is now ready for use with the Hospital Monitoring System."