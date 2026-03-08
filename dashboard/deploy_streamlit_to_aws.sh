#!/bin/bash

# KisaanMitra Streamlit Dashboard - Automated AWS EC2 Deployment
# This script automates the entire deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🚀 KisaanMitra Streamlit Dashboard - AWS EC2 Deployment"
echo "========================================================"
echo ""

# Configuration
REGION="ap-south-1"
INSTANCE_TYPE="t3.small"
AMI_ID="ami-0f58b397bc5c1f2e8"  # Ubuntu 22.04 LTS in ap-south-1
KEY_NAME="kisaanmitra-dashboard-key"
SECURITY_GROUP_NAME="kisaanmitra-dashboard-sg"
INSTANCE_NAME="kisaanmitra-dashboard"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

print_success "AWS CLI configured"

# Step 1: Create Key Pair (if doesn't exist)
print_status "Checking for SSH key pair..."
if aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION &> /dev/null; then
    print_success "Key pair '$KEY_NAME' already exists"
else
    print_status "Creating new key pair..."
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --region $REGION \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    
    chmod 400 ${KEY_NAME}.pem
    print_success "Key pair created and saved to ${KEY_NAME}.pem"
    print_warning "IMPORTANT: Save this file securely! You won't be able to download it again."
fi

# Step 2: Create Security Group (if doesn't exist)
print_status "Checking for security group..."
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null)

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
    print_status "Creating security group..."
    
    # Get default VPC
    VPC_ID=$(aws ec2 describe-vpcs \
        --filters "Name=isDefault,Values=true" \
        --region $REGION \
        --query 'Vpcs[0].VpcId' \
        --output text)
    
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for KisaanMitra Streamlit Dashboard" \
        --vpc-id $VPC_ID \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    # Add inbound rules
    print_status "Configuring security group rules..."
    
    # SSH (port 22)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # HTTP (port 80)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # HTTPS (port 443)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # Streamlit (port 8501) - for direct access
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 8501 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    print_success "Security group created: $SG_ID"
else
    print_success "Security group already exists: $SG_ID"
fi

# Step 3: Create IAM Role for EC2 (optional but recommended)
print_status "Checking for IAM role..."
ROLE_NAME="KisaanMitraDashboardRole"

if aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
    print_success "IAM role already exists"
else
    print_status "Creating IAM role for EC2..."
    
    # Create trust policy
    cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
    
    # Create role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file://trust-policy.json
    
    # Attach DynamoDB policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
    
    # Create instance profile
    aws iam create-instance-profile \
        --instance-profile-name $ROLE_NAME
    
    # Add role to instance profile
    aws iam add-role-to-instance-profile \
        --instance-profile-name $ROLE_NAME \
        --role-name $ROLE_NAME
    
    # Wait for role to be ready
    sleep 10
    
    rm trust-policy.json
    print_success "IAM role created"
fi

# Step 4: Create User Data Script
print_status "Creating user data script..."
cat > user-data.sh << 'EOF'
#!/bin/bash
set -e

# Log everything
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "Starting KisaanMitra Dashboard setup..."

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y python3.11 python3.11-venv python3-pip git nginx

# Create app directory
mkdir -p /opt/kisaanmitra
cd /opt/kisaanmitra

# Clone repository (replace with your repo URL)
# For now, we'll create the structure manually
mkdir -p dashboard

# Create requirements.txt
cat > dashboard/requirements.txt << 'REQUIREMENTS'
streamlit==1.28.0
boto3==1.28.0
pandas==2.0.0
plotly==5.17.0
python-dateutil==2.8.2
REQUIREMENTS

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r dashboard/requirements.txt

# Create systemd service
cat > /etc/systemd/system/kisaanmitra-dashboard.service << 'SERVICE'
[Unit]
Description=KisaanMitra Streamlit Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/kisaanmitra
Environment="PATH=/opt/kisaanmitra/venv/bin"
ExecStart=/opt/kisaanmitra/venv/bin/streamlit run dashboard/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Configure Nginx
cat > /etc/nginx/sites-available/kisaanmitra << 'NGINX'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/kisaanmitra /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Set permissions
chown -R ubuntu:ubuntu /opt/kisaanmitra

echo "Setup complete! Waiting for application files..."
EOF

# Step 5: Launch EC2 Instance
print_status "Launching EC2 instance..."

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --iam-instance-profile Name=$ROLE_NAME \
    --user-data file://user-data.sh \
    --region $REGION \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

print_success "Instance launched: $INSTANCE_ID"

# Wait for instance to be running
print_status "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

print_success "Instance is running!"
print_success "Public IP: $PUBLIC_IP"

# Wait for instance to be ready for SSH
print_status "Waiting for instance to be ready (this may take 2-3 minutes)..."
sleep 60

# Step 6: Upload application files
print_status "Uploading application files..."

# Wait for SSH to be ready
MAX_RETRIES=10
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no -o ConnectTimeout=5 ubuntu@$PUBLIC_IP "echo 'SSH ready'" &> /dev/null; then
        print_success "SSH connection established"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    print_status "Waiting for SSH... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 10
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Could not establish SSH connection"
    exit 1
fi

# Upload dashboard files
print_status "Uploading dashboard application..."
scp -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no -r ../dashboard ubuntu@$PUBLIC_IP:/tmp/

# Move files and start service
ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP << 'REMOTE_COMMANDS'
sudo cp -r /tmp/dashboard/* /opt/kisaanmitra/dashboard/
sudo chown -R ubuntu:ubuntu /opt/kisaanmitra
cd /opt/kisaanmitra
source venv/bin/activate
pip install -r dashboard/requirements.txt
sudo systemctl daemon-reload
sudo systemctl enable kisaanmitra-dashboard
sudo systemctl start kisaanmitra-dashboard
REMOTE_COMMANDS

# Clean up
rm user-data.sh

# Step 7: Display results
echo ""
echo "=========================================="
print_success "🎉 Deployment Complete!"
echo "=========================================="
echo ""
print_status "Instance Details:"
echo "  Instance ID: $INSTANCE_ID"
echo "  Public IP: $PUBLIC_IP"
echo "  Region: $REGION"
echo "  Instance Type: $INSTANCE_TYPE"
echo ""
print_status "Access URLs:"
echo "  Dashboard: http://$PUBLIC_IP"
echo "  Direct Streamlit: http://$PUBLIC_IP:8501"
echo ""
print_status "SSH Access:"
echo "  ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo ""
print_status "Useful Commands:"
echo "  Check status: ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'sudo systemctl status kisaanmitra-dashboard'"
echo "  View logs: ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'sudo journalctl -u kisaanmitra-dashboard -f'"
echo "  Restart: ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'sudo systemctl restart kisaanmitra-dashboard'"
echo ""
print_warning "Note: It may take 1-2 minutes for the dashboard to be fully ready."
echo ""
print_status "Testing connection in 30 seconds..."
sleep 30

# Test the connection
if curl -s -o /dev/null -w "%{http_code}" http://$PUBLIC_IP | grep -q "200\|302"; then
    print_success "Dashboard is accessible!"
else
    print_warning "Dashboard may still be starting up. Please wait a minute and try accessing:"
    echo "  http://$PUBLIC_IP"
fi

echo ""
print_success "Deployment script completed!"
echo ""
print_status "💰 Estimated Cost: ~$10-15/month for t3.small instance"
echo ""
print_status "To terminate the instance later:"
echo "  aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION"
