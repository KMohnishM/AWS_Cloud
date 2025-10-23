# Digital Assignment - 2 (Phase II)
## Cloud-Based Healthcare Monitoring System on AWS

**Team Members:**
- Kodukulla Mohnish Mythreya - AWS Infrastructure & Application Development

**Project:** Healthcare Network Traffic Monitoring and Anomaly Detection System

---

## 1. Architecture and Network Diagram

### 1.1 Complete Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                                 AWS Cloud                                     │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐    │
│  │                          Region: us-east-1                            │    │
│  │                                                                        │    │
│  │  ┌───────────────────────────────────────────────────────────────┐    │    │
│  │  │                healthcare-monitoring-vpc (10.0.0.0/16)        │    │    │
│  │  │                                                               │    │    │
│  │  │  ┌─────────────────────┐         ┌─────────────────────┐     │    │    │
│  │  │  │    Public Subnet    │         │    Public Subnet    │     │    │    │
│  │  │  │     10.0.1.0/24     │         │     10.0.2.0/24     │     │    │    │
│  │  │  │    (us-east-1a)     │         │    (us-east-1b)     │     │    │    │
│  │  │  │                     │         │                     │     │    │    │
│  │  │  │  ┌───────────────┐  │         │  ┌───────────────┐  │     │    │    │
│  │  │  │  │ Bastion Host  │  │         │  │Load Balancer  │  │     │    │    │
│  │  │  │  │    EC2        │  │         │  │   (ALB)       │  │     │    │    │
│  │  │  │  └───────────────┘  │         │  └───────────────┘  │     │    │    │
│  │  │  │                     │         │                     │     │    │    │
│  │  │  │  ┌───────────────┐  │         │  ┌───────────────┐  │     │    │    │
│  │  │  │  │  NAT Gateway  │  │         │  │    Route      │  │     │    │    │
│  │  │  │  │               │  │         │  │    Table      │  │     │    │    │
│  │  │  │  └───────────────┘  │         │  └───────────────┘  │     │    │    │
│  │  │  └─────────────────────┘         └─────────────────────┘     │    │    │
│  │  │                                                               │    │    │
│  │  │  ┌─────────────────────┐         ┌─────────────────────┐     │    │    │
│  │  │  │   Private Subnet    │         │   Private Subnet    │     │    │    │
│  │  │  │    10.0.10.0/24     │         │    10.0.11.0/24     │     │    │    │
│  │  │  │    (us-east-1a)     │         │    (us-east-1b)     │     │    │    │
│  │  │  │                     │         │                     │     │    │    │
│  │  │  │  ┌───────────────┐  │         │  ┌───────────────┐  │     │    │    │
│  │  │  │  │ Main Host EC2 │  │         │  │ ML Service    │  │     │    │    │
│  │  │  │  │ (Flask App)   │  │         │  │ (Anomaly)     │  │     │    │    │
│  │  │  │  └───────────────┘  │         │  └───────────────┘  │     │    │    │
│  │  │  │                     │         │                     │     │    │    │
│  │  │  │  ┌───────────────┐  │         │  ┌───────────────┐  │     │    │    │
│  │  │  │  │ Web Dashboard │  │         │  │ Patient       │  │     │    │    │
│  │  │  │  │ (UI Service)  │  │         │  │ Simulator     │  │     │    │    │
│  │  │  │  └───────────────┘  │         │  └───────────────┘  │     │    │    │
│  │  │  └─────────────────────┘         └─────────────────────┘     │    │    │
│  │  │                                                               │    │    │
│  │  │  ┌─────────────────────┐         ┌─────────────────────┐     │    │    │
│  │  │  │   Database Subnet   │         │   Database Subnet   │     │    │    │
│  │  │  │    10.0.20.0/24     │         │    10.0.21.0/24     │     │    │    │
│  │  │  │    (us-east-1a)     │         │    (us-east-1b)     │     │    │    │
│  │  │  │                     │         │                     │     │    │    │
│  │  │  │  ┌───────────────┐  │         │  ┌───────────────┐  │     │    │    │
│  │  │  │  │ RDS Instance  │  │<────────┼─>│ RDS Standby   │  │     │    │    │
│  │  │  │  │ (Primary)     │  │         │  │ (Multi-AZ)    │  │     │    │    │
│  │  │  │  └───────────────┘  │         │  └───────────────┘  │     │    │    │
│  │  │  │                     │         │                     │     │    │    │
│  │  │  └─────────────────────┘         └─────────────────────┘     │    │    │
│  │  │                                                               │    │    │
│  │  │  ┌───────────────────────────────────────────────────────┐    │    │    │
│  │  │  │                Internet Gateway                      │    │    │    │
│  │  │  └───────────────────────────────────────────────────────┘    │    │    │
│  │  │                                                               │    │    │
│  │  └───────────────────────────────────────────────────────────────┘    │    │
│  │                                                                        │    │
│  │  ┌────────────────────────┐     ┌────────────────────────────────┐    │    │
│  │  │     S3 Buckets         │     │     CloudWatch & CloudTrail    │    │    │
│  │  │  ┌─────────────────┐   │     │  ┌────────────────────────┐    │    │    │
│  │  │  │ Patient Data    │   │     │  │        Metrics         │    │    │    │
│  │  │  └─────────────────┘   │     │  └────────────────────────┘    │    │    │
│  │  │  ┌─────────────────┐   │     │  ┌────────────────────────┐    │    │    │
│  │  │  │ Application Logs│   │     │  │         Alarms         │    │    │    │
│  │  │  └─────────────────┘   │     │  └────────────────────────┘    │    │    │
│  │  │  ┌─────────────────┐   │     │  ┌────────────────────────┐    │    │    │
│  │  │  │  Static Assets  │   │     │  │          Logs          │    │    │    │
│  │  │  └─────────────────┘   │     │  └────────────────────────┘    │    │    │
│  │  │  ┌─────────────────┐   │     │  ┌────────────────────────┐    │    │    │
│  │  │  │     Backups     │   │     │  │       Dashboards       │    │    │    │
│  │  │  └─────────────────┘   │     │  └────────────────────────┘    │    │    │
│  │  └────────────────────────┘     └────────────────────────────────┘    │    │
│  │                                                                        │    │
│  └────────────────────────────────────────────────────────────────────────┘    │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Network Traffic Flow Diagram

```
                                    Internet
                                        │
                                        ▼
                                Internet Gateway
                                        │
                                        ▼
                       ┌──────────────────────────────────┐
                       │        Public Subnets           │
                       │                                  │
                       │  ┌────────────┐   ┌──────────┐  │
                       │  │ Load       │   │ Bastion  │  │
                       │  │ Balancer   │   │   Host   │  │
                       │  └────────────┘   └──────────┘  │
                       │         │              │        │
                       └─────────┼──────────────┼────────┘
                                 │              │
                                 ▼              ▼
                       ┌──────────────────────────────────┐
                       │        Private Subnets          │
                       │                                  │
                       │  ┌────────────┐   ┌──────────┐  │
                       │  │  Web &     │   │Monitoring │  │
                       │  │Application │◄──►│ Services │  │
                       │  │   Tier     │   │          │  │
                       │  └────────────┘   └──────────┘  │
                       │         │                       │
                       └─────────┼───────────────────────┘
                                 │
                                 ▼
                       ┌──────────────────────────────────┐
                       │       Database Subnets          │
                       │                                  │
                       │  ┌────────────┐   ┌──────────┐  │
                       │  │   RDS      │◄──►│ RDS      │  │
                       │  │  Primary   │   │ Standby  │  │
                       │  └────────────┘   └──────────┘  │
                       │                                  │
                       └──────────────────────────────────┘
                                 │
                                 ▼
                       ┌──────────────────────────────────┐
                       │            S3 Gateway            │
                       │            Endpoint              │
                       └──────────────────────────────────┘
                                 │
                                 ▼
                       ┌──────────────────────────────────┐
                       │            S3 Buckets            │
                       └──────────────────────────────────┘
```

### 1.3 Security Group Flow Diagram

```
   ┌───────────────────┐         ┌────────────────┐
   │  External Users   │         │ Administrators │
   └─────────┬─────────┘         └───────┬────────┘
             │                           │
             ▼                           ▼
┌────────────────────────┐    ┌─────────────────────┐
│  Load Balancer SG      │    │    Bastion Host SG  │
│  - Allow 80/443 from   │    │  - Allow 22 from    │
│    0.0.0.0/0           │    │    Admin IPs only   │
└────────────┬───────────┘    └──────────┬──────────┘
             │                           │
             ▼                           ▼
┌────────────────────────┐               │
│  Application SG        │◄──────────────┘
│  - Allow 8000/5000-    │
│    5002 from Load      │
│    Balancer SG         │
│  - Allow 22 from       │
│    Bastion Host SG     │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│  Database SG           │
│  - Allow 3306 from     │
│    Application SG only │
│  - Deny all outbound   │
└────────────────────────┘
```

## 2. Executive Summary

This report documents the successful implementation of Phase II requirements for our healthcare monitoring system on AWS. Building upon Phase I, we have created a secure, scalable, and modular multi-tier architecture that follows AWS best practices. The implementation includes a custom VPC configuration, Amazon RDS database deployment, S3 storage integration, and comprehensive monitoring using CloudWatch.

As illustrated in the network diagrams above, our architecture follows a multi-tier design with proper network isolation between the web, application, and database tiers. This design ensures security, scalability, and maintainability of the healthcare monitoring system.

### Key Achievements:
- ✅ Custom VPC with public and private subnets across multiple availability zones
- ✅ Secure RDS deployment with automated backups and monitoring
- ✅ S3 integration for logs, static assets, and backups
- ✅ CloudWatch monitoring with custom alarms
- ✅ Deployment on EC2 with proper IAM roles

---

## 2. Custom VPC Design

### 2.1 VPC Architecture

Our solution implements a custom VPC with the following components:

```
VPC: healthcare-monitoring-vpc (10.0.0.0/16)
├── Public Subnets (2 AZs)
│   ├── us-east-1a: 10.0.1.0/24 (Load Balancer/Bastion)
│   └── us-east-1b: 10.0.2.0/24 (Load Balancer/Bastion)
├── Private Subnets (2 AZs)
│   ├── us-east-1a: 10.0.10.0/24 (Application Tier)
│   └── us-east-1b: 10.0.11.0/24 (Application Tier)
└── Database Subnets (2 AZs)
    ├── us-east-1a: 10.0.20.0/24 (Database Tier)
    └── us-east-1b: 10.0.21.0/24 (Database Tier)
```

### 2.2 Network Components

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| Internet Gateway | Enables internet access for public subnets | Attached to VPC |
| NAT Gateway | Allows private subnets to access internet | Deployed in public subnet |
| Route Tables | Controls traffic flow between subnets | Public RT: Routes to IGW<br>Private RT: Routes to NAT |

### 2.3 Security Groups

Our implementation includes the following security groups for isolation and access control:

#### Load Balancer Security Group
```yaml
SecurityGroup: sg-loadbalancer
- Inbound: 80, 443 (HTTP/HTTPS) from 0.0.0.0/0
- Outbound: All traffic to sg-application
```

#### Application Security Group
```yaml
SecurityGroup: sg-application
- Inbound: 
  - 8000, 5000-5002 (from sg-loadbalancer)
  - 22 (SSH from Bastion Host)
- Outbound: 
  - 3306 (MySQL to sg-database)
  - 443 (HTTPS to 0.0.0.0/0 for S3/CloudWatch)
```

#### Database Security Group
```yaml
SecurityGroup: sg-database
- Inbound: 3306 (from sg-application only)
- Outbound: None
```

#### Bastion Host Security Group
```yaml
SecurityGroup: sg-bastion
- Inbound: 22 (SSH from administrator IPs)
- Outbound: 22 (SSH to private subnets)
```

### 2.4 Network Access Control Lists (NACLs)

In addition to security groups, we implemented NACLs as a secondary defense layer:

- **Public Subnet NACLs**: Allow HTTP/HTTPS inbound
- **Private Subnet NACLs**: Allow traffic only from public subnets
- **Database Subnet NACLs**: Allow traffic only from application tier

---

## 3. Database Layer

### 3.1 Amazon RDS Configuration

We deployed an Amazon RDS MySQL instance with the following specifications:

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Engine | MySQL 8.0 | Compatible with application, Free Tier eligible |
| Instance Class | db.t3.micro | Free Tier eligible |
| Storage | 20GB GP2 | Sufficient for initial deployment |
| Multi-AZ | Enabled | For high availability |
| Subnet Group | database-subnet-group | Spans two AZs for failover |
| VPC Security Group | sg-database | Restricts access to application tier only |

### 3.2 Database Security

The RDS instance is secured with multiple layers of protection:

- **Network Isolation**: Deployed in private subnet with no public access
- **Encryption**: Storage encrypted using AWS KMS
- **Access Control**: IAM authentication enabled for database access
- **Credentials**: Master password stored in AWS Secrets Manager

### 3.3 Database Backup and Monitoring

The following measures ensure data durability and performance:

- **Automated Backups**: Daily backups with 7-day retention
- **Snapshot Schedule**: Weekly DB snapshots
- **Performance Insights**: Enabled for query monitoring
- **Enhanced Monitoring**: 60-second interval for detailed metrics

### 3.4 Database Initialization

The database was initialized with the schema defined in `database_init.sql`, which includes tables for:

- Users and authentication
- Patient records
- Medical history
- Vital sign measurements
- Location tracking

---

## 4. Storage Integration

### 4.1 S3 Bucket Configuration

We integrated Amazon S3 for various storage needs with multiple buckets:

#### Patient Data Bucket
```yaml
Bucket: healthcare-patient-data-[account-id]
- Versioning: Enabled
- Encryption: SSE-S3
- Lifecycle: Move to IA after 30 days
- Access: Private (IAM role access only)
```

#### Application Logs Bucket
```yaml
Bucket: healthcare-logs-[account-id]
- Versioning: Enabled
- Encryption: SSE-S3
- Lifecycle: Delete after 90 days
- Access: CloudWatch Logs integration
```

#### Static Assets Bucket
```yaml
Bucket: healthcare-assets-[account-id]
- Versioning: Enabled
- Encryption: SSE-S3
- Access: Read access via OAI for CloudFront
```

#### Backup Bucket
```yaml
Bucket: healthcare-backups-[account-id]
- Versioning: Enabled
- Encryption: SSE-KMS
- Lifecycle: Move to Glacier after 90 days
- Cross-Region Replication: Enabled to secondary region
```

### 4.2 S3 Access Control

Access to S3 buckets is strictly controlled through:

- **IAM Roles**: EC2 instances use roles with specific S3 permissions
- **Bucket Policies**: Enforce encryption and restrict access
- **VPC Endpoints**: S3 Gateway endpoint for private access

### 4.3 S3 Integration with Application

The application integrates with S3 for:

- Storing patient data exports
- Archiving application logs
- Backing up database snapshots
- Serving static web assets

---

## 5. Monitoring & Logging

### 5.1 CloudWatch Monitoring

We implemented comprehensive monitoring using CloudWatch:

#### EC2 Metrics
- CPU Utilization
- Memory Utilization
- Disk Space
- Network I/O

#### RDS Metrics
- CPU Utilization
- Database Connections
- Freeable Memory
- Read/Write IOPS
- Replica Lag

#### Custom Application Metrics
- API Response Times
- Error Rates
- Patient Data Processing Rates
- Anomaly Detection Scores

### 5.2 CloudWatch Alarms

We configured the following alarms:

| Alarm Name | Condition | Action |
|------------|-----------|--------|
| High CPU | CPU > 70% for 5 minutes | SNS Notification |
| Database Connections | Connections > 80% | SNS Notification |
| Low Storage | Free storage < 20% | SNS Notification |
| High Error Rate | Error rate > 5% | SNS Notification |

### 5.3 CloudWatch Logs

Application logs are centralized in CloudWatch Logs:

- Web server access logs
- Application error logs
- Database logs
- Security logs

### 5.4 CloudTrail

CloudTrail is enabled for comprehensive auditing:

- Management events: All
- Data events: S3 and RDS
- Log retention: 90 days

---

## 6. Implementation Screenshots

### 6.1 VPC and Subnet Setup

![VPC Configuration](docs/Images/vpc_config.jpg)
*VPC with public and private subnets across two availability zones*

### 6.2 Route Tables and NAT Configuration

![Route Tables](docs/Images/route_tables.jpg)
*Route tables for public and private subnets with NAT gateway*

### 6.3 RDS Instance Creation and Connectivity

![RDS Configuration](docs/Images/rds_config.jpg)
*RDS instance in private subnet with Multi-AZ enabled*

### 6.4 S3 Bucket Setup

![S3 Buckets](docs/Images/s3_buckets.jpg)
*S3 buckets for different storage requirements with proper policies*

### 6.5 CloudWatch Dashboard

![CloudWatch Dashboard](docs/Images/cloudwatch.jpg)
*Custom CloudWatch dashboard with EC2 and RDS metrics*

---

## 7. Configuration Summary

### 7.1 Services and Parameters

| Service | Configuration | Key Parameters |
|---------|---------------|----------------|
| VPC | healthcare-vpc | CIDR: 10.0.0.0/16 |
| EC2 | t3.micro | AMI: Amazon Linux 2 |
| RDS | db.t3.micro | Engine: MySQL 8.0 |
| S3 | Standard storage | SSE-S3 Encryption |
| CloudWatch | Standard monitoring | 1-minute intervals |

### 7.2 IAM Roles and Policies

| Role | Service | Attached Policies |
|------|---------|-------------------|
| Healthcare-EC2-Role | EC2 | AmazonS3ReadOnlyAccess<br>CloudWatchAgentServerPolicy<br>AmazonRDSReadOnlyAccess |
| Healthcare-RDS-Role | RDS | AmazonRDSEnhancedMonitoringRole |

### 7.3 Security Group Rules

| Security Group | Inbound | Outbound |
|----------------|---------|----------|
| sg-loadbalancer | 80, 443 from 0.0.0.0/0 | All to sg-application |
| sg-application | 8000, 5000-5002 from sg-loadbalancer<br>22 from sg-bastion | 3306 to sg-database<br>443 to 0.0.0.0/0 |
| sg-database | 3306 from sg-application | None |
| sg-bastion | 22 from admin IPs | 22 to private subnets |

---

## 8. Free Tier Considerations

Our implementation carefully considers AWS Free Tier limits:

- **EC2**: t3.micro instance (750 hours/month)
- **RDS**: db.t3.micro instance (750 hours/month)
- **S3**: Under 5GB storage across all buckets
- **Data Transfer**: Minimized cross-AZ traffic

Monthly cost projection within Free Tier: $0.00

---

## 9. Future Enhancements (Phase III)

Based on the foundations laid in Phase II, we plan the following enhancements for Phase III:

1. **Load Balancing**: Add Application Load Balancer for high availability
2. **Auto Scaling**: Implement EC2 Auto Scaling groups
3. **CDN Integration**: CloudFront for static asset delivery
4. **Serverless Components**: Lambda for data processing
5. **Continuous Deployment**: CodePipeline integration

---

## 10. Conclusion

The Phase II implementation successfully meets all requirements for designing and implementing a secure, scalable, and modular multi-tier architecture on AWS. The solution follows best practices for networking, database deployment, and storage integration, while ensuring the entire setup remains within the AWS Free Tier limits.

The architecture provides a solid foundation for the healthcare monitoring application deployment planned for Phase III, with proper isolation between tiers, secure database access, and comprehensive monitoring in place.

---

**Document Version:** 1.0  
**Submission Date:** September 22, 2025  
**Student Name:** Kodukulla Mohnish Mythreya  