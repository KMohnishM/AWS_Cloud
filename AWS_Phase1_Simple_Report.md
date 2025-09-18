# Digital Assignment - Phase I (DA-1)
## Healthcare Monitoring System on AWS - Simplified Implementation

**Team Members:**
- [Your Name] - AWS Infrastructure & Deployment
- [Partner Name] - Application Development

**Project:** Healthcare Network Traffic Monitoring and Anomaly Detection System

---

## 1. Executive Summary

This report documents a simplified AWS deployment for our healthcare monitoring system using AWS Free Tier services. The focus is on practical implementation with essential services: IAM, VPC, EC2, and S3.

### Key Objectives:
- Deploy healthcare monitoring system on AWS Free Tier
- Implement basic security with IAM and VPC
- Use EC2 for application hosting
- Store data securely in S3

---

## 2. AWS Account Setup

### 2.1 Account Configuration
- **Account Type:** AWS Free Tier Account
- **Region:** us-east-1 (N. Virginia)
- **Billing Alert:** Set at $5 threshold
- **Root User:** MFA enabled

### 2.2 Free Tier Services We'll Use
- **EC2:** 750 hours/month (t3.micro)
- **S3:** 5GB storage
- **CloudWatch:** Basic monitoring
- **IAM:** Free for all users

---

## 3. Identity and Access Management (IAM)

### 3.1 IAM Users (Simple Setup)

#### Admin User
```json
{
  "UserName": "healthcare-admin",
  "Group": "Administrators",
  "Permissions": "AdministratorAccess"
}
```

#### Developer User
```json
{
  "UserName": "healthcare-developer",
  "Group": "Developers", 
  "Permissions": [
    "EC2FullAccess",
    "S3FullAccess",
    "CloudWatchFullAccess"
  ]
}
```

### 3.2 IAM Role for EC2
```json
{
  "RoleName": "Healthcare-EC2-Role",
  "TrustedEntities": "ec2.amazonaws.com",
  "Policies": [
    "CloudWatchAgentServerPolicy",
    "S3ReadWriteAccess"
  ]
}
```

### 3.3 MFA Setup
- **Root User:** Enable MFA (Google Authenticator)
- **Admin User:** Enable MFA
- **Console Access:** MFA required for admin access

---

## 4. Virtual Private Cloud (VPC) - Simple Design

### 4.1 VPC Configuration
```
VPC: healthcare-vpc (10.0.0.0/16)
├── Public Subnet: 10.0.1.0/24 (us-east-1a)
└── Private Subnet: 10.0.10.0/24 (us-east-1a)
```

### 4.2 Security Groups

#### Application Security Group
```yaml
SecurityGroup: sg-healthcare-app
- Inbound Rules:
  - SSH (22): Your IP only
  - HTTP (80): 0.0.0.0/0
  - HTTPS (443): 0.0.0.0/0
  - Custom (8000): 0.0.0.0/0 (Flask app)
  - Custom (3000): 0.0.0.0/0 (Grafana)
  - Custom (9090): 0.0.0.0/0 (Prometheus)
- Outbound Rules:
  - All traffic: 0.0.0.0/0
```

---

## 5. AWS Services Implementation

### 5.1 Amazon EC2 Instance

#### Single Application Server
```yaml
Instance: healthcare-server
- Type: t3.micro (Free Tier)
- OS: Amazon Linux 2
- Storage: 8GB GP2 EBS
- IAM Role: Healthcare-EC2-Role
- Security Group: sg-healthcare-app
- Key Pair: healthcare-key
```

#### User Data Script (Docker Installation)
```bash
#!/bin/bash
# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone application
cd /home/ec2-user
git clone https://github.com/KMohnishM/CN_Project.git
cd CN_Project

# Start application
docker-compose up -d
```

### 5.2 Amazon S3 Buckets

#### Patient Data Bucket
```yaml
Bucket: healthcare-patient-data-[your-account-id]
- Versioning: Enabled
- Encryption: SSE-S3 (default)
- Access: Private
- Lifecycle: None (Free Tier)
```

#### Logs Bucket
```yaml
Bucket: healthcare-logs-[your-account-id]
- Versioning: Disabled
- Encryption: SSE-S3 (default)
- Access: Private
- Lifecycle: Delete after 30 days
```

### 5.3 CloudWatch Monitoring

#### Basic Monitoring
```yaml
Metrics:
- CPU Utilization
- Memory Utilization
- Disk Usage
- Network In/Out
```

#### Simple Alarms
```yaml
Alarms:
- HighCPU: CPU > 80% for 5 minutes
- LowDiskSpace: Disk < 20% available
```

---

## 6. Shared Responsibility Model

### 6.1 AWS Responsibilities
- **Physical Security:** Data centers
- **Hardware Security:** Compute, storage
- **Network Security:** VPC infrastructure
- **Virtualization Security:** Hypervisor

### 6.2 Our Responsibilities
- **Application Security:** Code, data validation
- **Data Security:** Encryption, access control
- **Network Security:** Security group rules
- **Identity Management:** IAM users, MFA

### 6.3 Implementation Checklist
- [x] Enable MFA for root and admin users
- [x] Create IAM users with least privilege
- [x] Configure security groups properly
- [x] Enable S3 encryption
- [x] Set up CloudWatch monitoring

---

## 7. Simple Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Cloud                          │
├─────────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Internet Gateway                  │   │
│  └─────────────────────────────────────────────────┘   │
│                              │                       │
│                              ▼                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Public Subnet                     │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │         EC2 Instance                   │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ │   │   │
│  │  │  │  Flask  │ │Prometheus│ │ Grafana │ │   │   │
│  │  │  │   App   │ │(Metrics)│ │(Dashboard│ │   │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
│                              │                       │
│                              ▼                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │                    S3                         │   │
│  │  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │ Patient Data│  │    Logs     │            │   │
│  │  └─────────────┘  └─────────────┘            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Step-by-Step Implementation Guide

### 8.1 AWS Console Setup (30 minutes)

#### Step 1: Create IAM Users
1. Go to IAM Console
2. Create Admin User: `healthcare-admin`
3. Create Developer User: `healthcare-developer`
4. Enable MFA for both users
5. Create EC2 Role: `Healthcare-EC2-Role`

#### Step 2: Create VPC
1. Go to VPC Console
2. Create VPC: `healthcare-vpc` (10.0.0.0/16)
3. Create Public Subnet: `10.0.1.0/24`
4. Create Internet Gateway
5. Attach Internet Gateway to VPC
6. Update route table for public access

#### Step 3: Create Security Group
1. Create Security Group: `sg-healthcare-app`
2. Add inbound rules:
   - SSH (22): Your IP
   - HTTP (80): 0.0.0.0/0
   - Custom (8000): 0.0.0.0/0
   - Custom (3000): 0.0.0.0/0
   - Custom (9090): 0.0.0.0/0

#### Step 4: Create S3 Buckets
1. Create bucket: `healthcare-patient-data-[account-id]`
2. Create bucket: `healthcare-logs-[account-id]`
3. Enable versioning on patient data bucket

#### Step 5: Launch EC2 Instance
1. Launch t3.micro instance
2. Select Amazon Linux 2 AMI
3. Attach IAM Role: `Healthcare-EC2-Role`
4. Attach Security Group: `sg-healthcare-app`
5. Use User Data script (above)
6. Create/select key pair

### 8.2 Application Deployment (15 minutes)

#### Step 6: Deploy Application
1. SSH to EC2 instance
2. Verify Docker is running: `docker --version`
3. Navigate to application: `cd CN_Project`
4. Start services: `docker-compose up -d`
5. Verify services are running: `docker ps`

#### Step 7: Configure Monitoring
1. Access Prometheus: `http://[EC2-IP]:9090`
2. Access Grafana: `http://[EC2-IP]:3000`
3. Set up basic CloudWatch alarms

---

## 9. Cost Analysis (Free Tier)

### 9.1 Monthly Costs (Free Tier)
- **EC2 t3.micro:** 750 hours/month - **$0**
- **S3 Storage:** 5GB - **$0**
- **CloudWatch:** Basic monitoring - **$0**
- **IAM:** All users and roles - **$0**
- **VPC:** All components - **$0**

### 9.2 Total Monthly Cost: **$0**

### 9.3 Post-Free Tier Estimate
- **EC2:** ~$8/month (t3.micro)
- **S3:** ~$0.25/month (5GB)
- **Total:** ~$8.25/month

---

## 10. Security Implementation

### 10.1 Basic Security Measures
- **MFA:** Enabled for admin users
- **IAM:** Least privilege access
- **Security Groups:** Restrictive inbound rules
- **S3:** Private buckets with encryption
- **SSH:** Key-based authentication only

### 10.2 Data Protection
- **Encryption at Rest:** S3 SSE-S3
- **Encryption in Transit:** HTTPS/TLS
- **Access Control:** IAM policies
- **Backup:** S3 versioning

---

## 11. Monitoring & Alerting

### 11.1 CloudWatch Monitoring
- **EC2 Metrics:** CPU, Memory, Disk, Network
- **Custom Metrics:** Application health
- **Logs:** Application logs to CloudWatch

### 11.2 Basic Alarms
- **High CPU Usage:** > 80% for 5 minutes
- **Low Disk Space:** < 20% available
- **Instance Status:** Health check failures

---

## 12. Testing & Validation

### 12.1 Functionality Tests
- [ ] Application accessible via HTTP
- [ ] Prometheus metrics endpoint working
- [ ] Grafana dashboard accessible
- [ ] Patient data being generated
- [ ] Alerts triggering properly

### 12.2 Security Tests
- [ ] MFA working for admin access
- [ ] S3 buckets not publicly accessible
- [ ] Security groups blocking unauthorized access
- [ ] IAM policies working correctly

---

## 13. Troubleshooting Guide

### 13.1 Common Issues

#### Application Not Starting
```bash
# Check Docker status
sudo systemctl status docker

# Check container logs
docker logs [container-name]

# Restart services
docker-compose down
docker-compose up -d
```

#### Security Group Issues
- Verify inbound rules include your IP
- Check that required ports are open
- Ensure outbound rules allow all traffic

#### S3 Access Issues
- Verify IAM role has S3 permissions
- Check bucket policies
- Ensure encryption settings are correct

---

## 14. Next Steps (Phase II)

### 14.1 Planned Enhancements
- **Load Balancer:** Add ALB for high availability
- **Auto Scaling:** Implement auto-scaling groups
- **Database:** Add RDS for persistent data
- **Backup:** Automated backup strategy

### 14.2 Advanced Features
- **Container Orchestration:** Migrate to ECS
- **Serverless:** Use Lambda for processing
- **CDN:** Add CloudFront for performance
- **Monitoring:** Advanced APM tools

---

## 15. Conclusion

This simplified AWS deployment provides a solid foundation for the healthcare monitoring system using only Free Tier services. The implementation is practical, cost-effective, and follows AWS best practices while remaining achievable for Phase 1.

### Key Achievements:
- ✅ AWS Free Tier deployment
- ✅ Basic security implementation
- ✅ Monitoring and alerting setup
- ✅ Cost-effective solution ($0/month)
- ✅ Scalable architecture foundation

### Benefits:
- **Cost:** Zero monthly cost during Free Tier
- **Security:** Basic but effective security measures
- **Scalability:** Easy to expand in Phase II
- **Maintenance:** Simple to manage and monitor

---

## 16. Appendices

### Appendix A: AWS CLI Commands
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create IAM Role
aws iam create-role --role-name Healthcare-EC2-Role

# Create S3 Bucket
aws s3 mb s3://healthcare-patient-data-[account-id]

# Launch EC2 Instance
aws ec2 run-instances --image-id ami-0c02fb55956c7d316 --count 1 --instance-type t3.micro
```

### Appendix B: Useful Commands
```bash
# Check instance status
aws ec2 describe-instances --instance-ids i-1234567890abcdef0

# View S3 bucket contents
aws s3 ls s3://healthcare-patient-data-[account-id]

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization
```

### Appendix C: Security Checklist
- [ ] Root user MFA enabled
- [ ] Admin user MFA enabled
- [ ] IAM users created with least privilege
- [ ] Security groups configured properly
- [ ] S3 buckets private and encrypted
- [ ] CloudWatch monitoring enabled
- [ ] Key pair created for EC2 access

---

**Document Version:** 1.0  
**Last Updated:** [Current Date]  
**Next Review:** [Date + 3 months]  
**Implementation Time:** ~2 hours  
**Monthly Cost:** $0 (Free Tier) 