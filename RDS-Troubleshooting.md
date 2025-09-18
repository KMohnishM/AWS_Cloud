# RDS Connectivity Troubleshooting Guide

## Error: Can't connect to MySQL server (Error code 111)

This error indicates that your computer cannot establish a network connection to the RDS instance. Here are the most common causes and solutions:

### 1. Security Group Configuration

Your RDS instance's security group needs to explicitly allow incoming connections from your IP address:

1. Go to the AWS Management Console
2. Navigate to RDS > Databases > Select your database (database-1)
3. Click on the "Connectivity & security" tab
4. Click on the VPC security group (e.g., "default")
5. In the security group page:
   - Select the "Inbound rules" tab
   - Click "Edit inbound rules"
   - Add a rule:
     - Type: MySQL/Aurora (port 3306)
     - Source: Your IP address or 0.0.0.0/0 for any IP (not recommended for production)
   - Save rules

### 2. Public Accessibility Setting

Make sure your RDS instance is set to be publicly accessible:

1. Go to the AWS Management Console
2. Navigate to RDS > Databases > Select your database (database-1)
3. Click "Modify"
4. Under "Connectivity", ensure "Public access" is set to "Yes"
5. Click "Continue" and "Apply immediately"
6. Click "Modify DB Instance"

Note: It may take a few minutes for changes to take effect.

### 3. Database Instance Status

Verify that the RDS instance is in the "Available" state:

1. Go to the AWS Management Console
2. Navigate to RDS > Databases
3. Check that the status of your database (database-1) shows as "Available"

### 4. Network/Firewall Issues

If you're accessing from a corporate network or using a VPN:

1. Ensure that outbound connections to port 3306 are allowed
2. Try connecting from a different network (e.g., mobile hotspot)
3. Temporarily disable any VPN software that may be routing traffic

### 5. AWS Region and Endpoint

Confirm you're using the correct endpoint for your RDS instance's region:

1. Go to the AWS Management Console
2. Navigate to RDS > Databases > Select your database (database-1)
3. On the "Connectivity & security" tab, check the "Endpoint" field
4. Ensure this matches the endpoint in your .env file

## Testing Connectivity

You can test basic network connectivity using telnet or ncat:

```powershell
# Using PowerShell Test-NetConnection (Windows)
Test-NetConnection -ComputerName database-1.cxkucyeociny.ap-south-1.rds.amazonaws.com -Port 3306
```

A successful connection will show "TcpTestSucceeded : True".

## Checking Your Current Public IP

To find your current public IP address (useful for setting up security group rules):

1. Visit [whatismyip.com](https://www.whatismyip.com/) or [ipify.org](https://api.ipify.org/)
2. Use this IP address in your security group rule