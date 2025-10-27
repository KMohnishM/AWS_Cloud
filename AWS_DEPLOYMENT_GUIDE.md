# AWS Deployment Guide - Healthcare Monitoring System

## Overview
This guide covers deploying the healthcare monitoring system to AWS with external monitoring services (Grafana, Prometheus, AlertManager).

## Environment Configuration for AWS

### 1. Create Production Environment File
Copy `.env.example` to `.env` and update for your AWS deployment:

```bash
# Copy the example file
cp .env.example .env
```

### 2. Update .env for AWS Deployment
Replace the monitoring URLs in `.env` with your AWS instance public IP:

```env
# AWS Production Configuration
GRAFANA_URL=http://13.234.199.39:3000
PROMETHEUS_URL=http://13.234.199.39:9090
ALERTMANAGER_URL=http://13.234.199.39:9093

# Security - Generate strong keys for production
SECRET_KEY=your-production-secret-key-here

# Database - Use RDS for production
DATABASE_URL=mysql+pymysql://username:password@rds-endpoint:3306/healthcare_db
```

### 3. AWS Security Group Configuration
Ensure your EC2 instance security group allows inbound traffic on:
- Port 3000 (Grafana)
- Port 9090 (Prometheus) 
- Port 9093 (AlertManager)
- Port 5000 (Web Dashboard)
- Port 8000 (Main Host API)

Example security group rules:
```
Type: Custom TCP
Port: 3000, 5000, 8000, 9090, 9093
Source: 0.0.0.0/0 (or restrict to your IP range)
```

### 4. Grafana Embedding Configuration
For proper iframe embedding in the monitoring page, ensure Grafana is configured with:

```ini
# In grafana.ini or via environment variables
[security]
allow_embedding = true
cookie_samesite = disabled

[auth.anonymous]
enabled = true
org_role = Viewer  # Optional: allow anonymous viewing
```

These settings are already configured in the docker-compose.yml Grafana service.

## Deployment Steps

### Option A: Direct Docker Compose on EC2
1. SSH into your AWS EC2 instance
2. Clone your repository
3. Copy and configure `.env` file
4. Run the application:
   ```bash
   docker-compose up -d --build
   ```

### Option B: AWS ECS (Fargate)
1. Build and push images to ECR
2. Create ECS task definitions with environment variables
3. Configure Application Load Balancer for external access
4. Deploy services to ECS cluster

## Production Considerations

### Security
- Use HTTPS in production (configure SSL/TLS)
- Replace default passwords (Grafana admin/admin)
- Restrict security group access to necessary IPs
- Use AWS Secrets Manager for sensitive configuration

### Monitoring URLs Best Practices
- Use Application Load Balancer with custom domain names instead of IP addresses
- Example: `https://monitoring.yourdomain.com` instead of `http://13.234.199.39:3000`
- Configure Route 53 for DNS management

### High Availability
- Use RDS Multi-AZ for database
- Deploy across multiple availability zones
- Configure auto-scaling for ECS services
- Use ElastiCache for session storage

## Testing Your Deployment

1. **Web Dashboard**: Access `http://your-aws-ip:5000`
2. **Monitoring Page**: Check that Grafana embeds correctly at `/monitoring`
3. **Direct Grafana**: Access `http://your-aws-ip:3000` 
4. **API Health**: Test `http://your-aws-ip:8000/health`

## Troubleshooting

### Grafana Not Embedding
- Check that `allow_embedding = true` in Grafana config
- Verify iframe security settings
- Check browser console for CORS errors

### Service Connection Issues
- Verify security group rules
- Check docker network connectivity
- Review environment variable values in containers

### Performance Issues
- Monitor CloudWatch metrics
- Scale services based on load
- Consider using AWS RDS instead of SQLite for production workloads