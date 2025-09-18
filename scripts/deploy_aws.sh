#!/bin/bash
# Deploy the application to AWS EC2

# Variables
INSTANCE_TYPE="t2.medium"
KEY_NAME="your-key-name"
SECURITY_GROUP="your-security-group"
AMI_ID="ami-0c55b159cbfafe1f0"  # Ubuntu 20.04 LTS
REGION="us-east-1"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Create EC2 instance
echo "Creating EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP \
    --region $REGION \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=healthcare-monitoring}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance $INSTANCE_ID is being created. Waiting for it to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --region $REGION \
    --output text)

echo "Instance is running at $PUBLIC_IP"

# SSH into the instance and set up the environment
echo "Setting up the environment on the instance..."
echo "Please make sure your SSH key is set up correctly."
echo "Connect to the instance with: ssh -i ~/.ssh/$KEY_NAME.pem ubuntu@$PUBLIC_IP"
echo "Then run the following commands:"
echo "  git clone https://github.com/KMohnishM/CN_Project.git"
echo "  cd CN_Project"
echo "  chmod +x scripts/setup.sh"
echo "  ./scripts/setup.sh"
echo "  docker-compose up -d"
echo ""
echo "Once deployed, you can access:"
echo "  Prometheus: http://$PUBLIC_IP:9090"
echo "  Grafana: http://$PUBLIC_IP:3001"
echo "  AlertManager: http://$PUBLIC_IP:9093"