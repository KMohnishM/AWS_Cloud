# PowerShell script to initialize RDS database using Docker
# This script connects to the RDS database and initializes it with the schema

# Load environment variables from .env file
function Load-EnvFile {
    if (Test-Path -Path ".env") {
        Get-Content .env | ForEach-Object {
            if (-not [string]::IsNullOrWhiteSpace($_) -and -not $_.StartsWith('#')) {
                $key, $value = $_.Split('=', 2)
                [Environment]::SetEnvironmentVariable($key, $value)
            }
        }
    }
    else {
        Write-Error "Error: .env file not found"
        exit 1
    }
}

# Load environment variables
Load-EnvFile

$RDS_HOSTNAME = [Environment]::GetEnvironmentVariable("RDS_HOSTNAME")
$RDS_USERNAME = [Environment]::GetEnvironmentVariable("RDS_USERNAME")
$RDS_PASSWORD = [Environment]::GetEnvironmentVariable("RDS_PASSWORD")
$RDS_DB_NAME = [Environment]::GetEnvironmentVariable("RDS_DB_NAME")

Write-Host "Initializing RDS database at $RDS_HOSTNAME..."

# Check if Docker is installed
try {
    docker --version | Out-Null
}
catch {
    Write-Error "Error: Docker is not installed or not running"
    Write-Host "Please install Docker to run this script: https://docs.docker.com/get-docker/"
    exit 1
}

# Test connection to RDS
Write-Host "Testing connection to RDS..."
Write-Host "Attempting to connect to $RDS_HOSTNAME with user $RDS_USERNAME..."

# First, test basic network connectivity
Write-Host "Testing basic network connectivity to RDS endpoint..."
try {
    $testConnection = Test-NetConnection -ComputerName $RDS_HOSTNAME -Port 3306 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($testConnection.TcpTestSucceeded) {
        Write-Host "Network connectivity test successful. Port 3306 is reachable."
    } else {
        Write-Host "Network connectivity test failed. Cannot reach port 3306 on $RDS_HOSTNAME."
        Write-Host "This suggests a network or security group issue."
    }
} catch {
    Write-Host "Could not perform network test: $_"
}

# Now try the full MySQL connection
Write-Host "Testing database connection with credentials..."
docker run --rm mysql:5.7 mysql -h $RDS_HOSTNAME -u $RDS_USERNAME -p"$RDS_PASSWORD" -e "SELECT 'Connection successful!' as Message;"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Error: Failed to connect to RDS database"
    Write-Host "Please check:"
    Write-Host "1. Your RDS security group allows connections from your IP address to port 3306"
    Write-Host "2. The RDS instance is publicly accessible"
    Write-Host "3. The RDS instance is in the 'Available' state"
    Write-Host "4. Your network/VPN is not blocking outbound connections to port 3306"
    Write-Host ""
    Write-Host "For detailed troubleshooting steps, see RDS-Troubleshooting.md"
    exit 1
}

# Initialize the database with the schema
Write-Host "Initializing database schema..."

# Create a temporary file with the SQL content
$tempSqlFile = "temp_init.sql"
Get-Content -Path "database_init.sql" | Set-Content -Path $tempSqlFile -Encoding UTF8

# Use Docker to run the SQL file
Get-Content $tempSqlFile | docker run -i --rm mysql:5.7 mysql -h $RDS_HOSTNAME -u $RDS_USERNAME -p"$RDS_PASSWORD" $RDS_DB_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Error "Error: Failed to initialize database schema"
    Remove-Item -Path $tempSqlFile -Force
    exit 1
}

# Clean up
Remove-Item -Path $tempSqlFile -Force

Write-Host "Database initialization complete!"
Write-Host "RDS database is now ready for use with the Hospital Monitoring System."