#!/bin/bash

# KisaanMitra Streamlit Dashboard - EC2 Deployment Script
# This script sets up Streamlit on an EC2 instance

echo "🚀 KisaanMitra Streamlit Dashboard - EC2 Setup"
echo "================================================"

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
echo "🐍 Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Install required system packages
sudo apt-get install -y git nginx

# Create app directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/kisaanmitra
sudo chown -R ubuntu:ubuntu /opt/kisaanmitra
cd /opt/kisaanmitra

# Clone or copy your code here
# git clone <your-repo-url> .

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r dashboard/requirements.txt

# Configure AWS credentials (if not using IAM role)
echo "🔐 Configuring AWS credentials..."
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
EOF

cat > ~/.aws/config << EOF
[default]
region = ap-south-1
EOF

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/kisaanmitra-dashboard.service > /dev/null << EOF
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

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx reverse proxy
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/kisaanmitra > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/kisaanmitra /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Start the service
echo "🚀 Starting KisaanMitra dashboard..."
sudo systemctl daemon-reload
sudo systemctl enable kisaanmitra-dashboard
sudo systemctl start kisaanmitra-dashboard

# Check status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service status:"
sudo systemctl status kisaanmitra-dashboard --no-pager

echo ""
echo "🌐 Dashboard should be accessible at:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "📝 Useful commands:"
echo "   sudo systemctl status kisaanmitra-dashboard  # Check status"
echo "   sudo systemctl restart kisaanmitra-dashboard # Restart service"
echo "   sudo journalctl -u kisaanmitra-dashboard -f  # View logs"
