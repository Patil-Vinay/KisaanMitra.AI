# 🚀 Streamlit Dashboard - AWS EC2 Deployment Guide

## Quick Deploy (Automated)

### Prerequisites
- AWS CLI configured (`aws configure`)
- AWS account with EC2 permissions
- ~$10-15/month budget for t3.small instance

### One-Command Deployment

```bash
cd dashboard
./deploy_streamlit_to_aws.sh
```

This script will automatically:
1. ✅ Create SSH key pair
2. ✅ Create security group with proper rules
3. ✅ Create IAM role for DynamoDB access
4. ✅ Launch EC2 instance (Ubuntu 22.04, t3.small)
5. ✅ Install Python, Streamlit, and dependencies
6. ✅ Configure Nginx reverse proxy
7. ✅ Upload your dashboard files
8. ✅ Start the service
9. ✅ Provide you with the public URL

**Estimated Time:** 5-7 minutes

---

## What You'll Get

### Access URLs
```
Main Dashboard: http://YOUR-EC2-IP
Direct Streamlit: http://YOUR-EC2-IP:8501
```

### Features Deployed
- 📊 Real-time farmer analytics
- 👥 User management interface
- 💬 Conversation monitoring
- 🌐 Knowledge graph visualization
- 📈 Performance metrics
- 💰 Revenue analytics

### Instance Details
- **Type:** t3.small (2 vCPU, 2GB RAM)
- **OS:** Ubuntu 22.04 LTS
- **Region:** ap-south-1 (Mumbai)
- **Storage:** 20GB SSD
- **Cost:** ~$10-15/month

---

## Manual Deployment (Step-by-Step)

If you prefer manual control:

### Step 1: Launch EC2 Instance

```bash
# Via AWS Console
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose Ubuntu 22.04 LTS
4. Select t3.small
5. Create/select key pair
6. Configure security group:
   - Port 22 (SSH)
   - Port 80 (HTTP)
   - Port 443 (HTTPS)
   - Port 8501 (Streamlit)
7. Launch instance
```

### Step 2: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@YOUR-EC2-IP
```

### Step 3: Run Setup Script

```bash
# Upload the setup script
scp -i your-key.pem dashboard/deploy_to_ec2.sh ubuntu@YOUR-EC2-IP:/home/ubuntu/

# Connect and run
ssh -i your-key.pem ubuntu@YOUR-EC2-IP
chmod +x deploy_to_ec2.sh
sudo bash deploy_to_ec2.sh
```

### Step 4: Upload Dashboard Files

```bash
# From your local machine
scp -i your-key.pem -r dashboard ubuntu@YOUR-EC2-IP:/tmp/

# On EC2 instance
ssh -i your-key.pem ubuntu@YOUR-EC2-IP
sudo cp -r /tmp/dashboard/* /opt/kisaanmitra/dashboard/
sudo systemctl restart kisaanmitra-dashboard
```

---

## Post-Deployment

### Check Service Status

```bash
ssh -i your-key.pem ubuntu@YOUR-EC2-IP
sudo systemctl status kisaanmitra-dashboard
```

### View Logs

```bash
# Real-time logs
sudo journalctl -u kisaanmitra-dashboard -f

# Last 100 lines
sudo journalctl -u kisaanmitra-dashboard -n 100
```

### Restart Service

```bash
sudo systemctl restart kisaanmitra-dashboard
```

### Update Dashboard Code

```bash
# Upload new files
scp -i your-key.pem -r dashboard ubuntu@YOUR-EC2-IP:/tmp/

# On EC2
sudo cp -r /tmp/dashboard/* /opt/kisaanmitra/dashboard/
sudo systemctl restart kisaanmitra-dashboard
```

---

## Configure AWS Credentials

### Option 1: IAM Role (Recommended)

The automated script creates an IAM role with DynamoDB access. No manual configuration needed!

### Option 2: Manual Credentials

If not using IAM role:

```bash
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# Configure AWS CLI
aws configure
# Enter your access key, secret key, and region (ap-south-1)
```

---

## Add Custom Domain (Optional)

### Step 1: Point Domain to EC2

In your domain registrar (GoDaddy, Namecheap, etc.):
```
Type: A Record
Name: dashboard (or @)
Value: YOUR-EC2-IP
TTL: 300
```

### Step 2: Install SSL Certificate

```bash
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

Now access at: `https://yourdomain.com`

---

## Monitoring & Maintenance

### CloudWatch Monitoring

```bash
# Enable detailed monitoring
aws ec2 monitor-instances --instance-ids YOUR-INSTANCE-ID --region ap-south-1
```

### Set Up Alarms

```bash
# CPU utilization alarm
aws cloudwatch put-metric-alarm \
    --alarm-name kisaanmitra-high-cpu \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=YOUR-INSTANCE-ID \
    --evaluation-periods 2
```

### Backup Strategy

```bash
# Create AMI backup
aws ec2 create-image \
    --instance-id YOUR-INSTANCE-ID \
    --name "kisaanmitra-dashboard-backup-$(date +%Y%m%d)" \
    --region ap-south-1
```

---

## Troubleshooting

### Dashboard Not Loading

```bash
# Check if service is running
sudo systemctl status kisaanmitra-dashboard

# Check Nginx
sudo systemctl status nginx

# Check logs
sudo journalctl -u kisaanmitra-dashboard -n 50

# Restart everything
sudo systemctl restart kisaanmitra-dashboard
sudo systemctl restart nginx
```

### AWS Connection Errors

```bash
# Verify IAM role is attached
aws ec2 describe-instances --instance-ids YOUR-INSTANCE-ID \
    --query 'Reservations[0].Instances[0].IamInstanceProfile'

# Test DynamoDB access
aws dynamodb list-tables --region ap-south-1
```

### Port Not Accessible

```bash
# Check security group
aws ec2 describe-security-groups \
    --group-ids YOUR-SG-ID \
    --region ap-south-1

# Verify Nginx is listening
sudo netstat -tlnp | grep 80
sudo netstat -tlnp | grep 8501
```

### High Memory Usage

```bash
# Check memory
free -h

# Upgrade instance type
aws ec2 stop-instances --instance-ids YOUR-INSTANCE-ID
aws ec2 modify-instance-attribute \
    --instance-id YOUR-INSTANCE-ID \
    --instance-type t3.medium
aws ec2 start-instances --instance-ids YOUR-INSTANCE-ID
```

---

## Cost Optimization

### Current Cost: ~$10-15/month

**Breakdown:**
- EC2 t3.small: ~$15/month (on-demand)
- Data transfer: ~$1/month
- EBS storage (20GB): ~$2/month

### Save Money:

1. **Use Reserved Instance** (1-year commitment)
   - Save ~40%: $9/month instead of $15/month

2. **Use Spot Instance** (for non-critical)
   - Save ~70%: $4.50/month instead of $15/month

3. **Stop When Not Needed**
   ```bash
   # Stop instance (only pay for storage)
   aws ec2 stop-instances --instance-ids YOUR-INSTANCE-ID
   
   # Start when needed
   aws ec2 start-instances --instance-ids YOUR-INSTANCE-ID
   ```

4. **Use Smaller Instance** (if traffic is low)
   - t3.micro: ~$7.50/month (1 vCPU, 1GB RAM)

---

## Scaling Up

### Increase Instance Size

```bash
# Stop instance
aws ec2 stop-instances --instance-ids YOUR-INSTANCE-ID --region ap-south-1
aws ec2 wait instance-stopped --instance-ids YOUR-INSTANCE-ID --region ap-south-1

# Change instance type
aws ec2 modify-instance-attribute \
    --instance-id YOUR-INSTANCE-ID \
    --instance-type t3.medium \
    --region ap-south-1

# Start instance
aws ec2 start-instances --instance-ids YOUR-INSTANCE-ID --region ap-south-1
```

### Add Load Balancer (for high traffic)

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
    --name kisaanmitra-alb \
    --subnets subnet-xxx subnet-yyy \
    --security-groups sg-xxx \
    --region ap-south-1
```

---

## Terminate Instance

When you're done:

```bash
# Terminate instance
aws ec2 terminate-instances --instance-ids YOUR-INSTANCE-ID --region ap-south-1

# Delete security group
aws ec2 delete-security-group --group-id YOUR-SG-ID --region ap-south-1

# Delete key pair
aws ec2 delete-key-pair --key-name kisaanmitra-dashboard-key --region ap-south-1
```

---

## Quick Reference

### Service Management
```bash
sudo systemctl start kisaanmitra-dashboard    # Start
sudo systemctl stop kisaanmitra-dashboard     # Stop
sudo systemctl restart kisaanmitra-dashboard  # Restart
sudo systemctl status kisaanmitra-dashboard   # Status
```

### Logs
```bash
sudo journalctl -u kisaanmitra-dashboard -f   # Follow logs
sudo journalctl -u kisaanmitra-dashboard -n 100  # Last 100 lines
```

### Files
```bash
/opt/kisaanmitra/dashboard/          # Application files
/etc/systemd/system/kisaanmitra-dashboard.service  # Service file
/etc/nginx/sites-available/kisaanmitra  # Nginx config
/var/log/nginx/                      # Nginx logs
```

---

## Support

### Common Issues

1. **"Connection refused"** → Check security group allows port 80/8501
2. **"Service failed to start"** → Check logs with `journalctl`
3. **"AWS credentials not found"** → Verify IAM role is attached
4. **"High CPU usage"** → Upgrade to t3.medium

### Get Help

- Check logs: `sudo journalctl -u kisaanmitra-dashboard -f`
- Test locally: `streamlit run dashboard/streamlit_app.py`
- AWS Support: https://console.aws.amazon.com/support/

---

## Success Checklist

- [ ] EC2 instance launched and running
- [ ] Security group configured (ports 22, 80, 443, 8501)
- [ ] IAM role attached for DynamoDB access
- [ ] Dashboard accessible at http://YOUR-EC2-IP
- [ ] Service starts automatically on reboot
- [ ] Nginx reverse proxy working
- [ ] Logs are clean (no errors)
- [ ] Can view farmer data from DynamoDB
- [ ] Knowledge graph loads correctly

---

## 🎉 You're Live!

Your Streamlit dashboard is now running on AWS EC2!

**Share your dashboard:**
```
🌾 KisaanMitra Analytics Dashboard

📊 Live at: http://YOUR-EC2-IP

Features:
✅ Real-time farmer analytics
✅ Conversation monitoring
✅ Knowledge graph visualization
✅ Performance metrics
```

**Next Steps:**
1. Add custom domain (optional)
2. Set up SSL certificate
3. Configure CloudWatch alarms
4. Create backup AMI
5. Share with your team!

---

**Deployment Time:** 5-7 minutes  
**Monthly Cost:** ~$10-15  
**Uptime:** 24/7  
**Status:** Production Ready 🚀