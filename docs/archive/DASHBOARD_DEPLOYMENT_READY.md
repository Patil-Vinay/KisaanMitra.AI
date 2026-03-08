# 🎉 Streamlit Dashboard - Ready to Deploy!

## 🚀 One-Command Deployment

```bash
./deploy_dashboard_now.sh
```

That's it! The script will:
1. ✅ Verify AWS credentials
2. ✅ Create all required AWS resources
3. ✅ Launch EC2 instance
4. ✅ Install and configure everything
5. ✅ Give you the public URL

**Time:** 5-7 minutes  
**Cost:** ~$10-15/month

---

## 📋 What You Need

### Before Running
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS credentials configured (`aws configure`)
- [ ] ~$15/month budget for EC2 instance

### AWS Credentials Setup
```bash
aws configure
```

Enter:
- **AWS Access Key ID:** Your access key
- **AWS Secret Access Key:** Your secret key
- **Default region:** `ap-south-1`
- **Default output format:** `json`

---

## 🎯 What Gets Deployed

### Infrastructure
- **EC2 Instance:** t3.small (2 vCPU, 2GB RAM)
- **Operating System:** Ubuntu 22.04 LTS
- **Region:** ap-south-1 (Mumbai)
- **Storage:** 20GB SSD
- **Security Group:** Ports 22, 80, 443, 8501 open
- **IAM Role:** DynamoDB access configured

### Software Stack
- **Python:** 3.11
- **Streamlit:** Latest version
- **Nginx:** Reverse proxy configured
- **Systemd:** Auto-start on reboot
- **SSL Ready:** Can add Let's Encrypt later

### Dashboard Features
- 📊 Real-time farmer analytics
- 👥 User management interface
- 💬 Conversation monitoring
- 🌐 Knowledge graph visualization
- 📈 Performance metrics
- 💰 Revenue analytics

---

## 🔗 Your Dashboard URLs

After deployment, you'll get:

```
Main Dashboard: http://YOUR-EC2-IP
Direct Streamlit: http://YOUR-EC2-IP:8501
SSH Access: ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP
```

---

## 📖 Deployment Options

### Option 1: Automated (Recommended)
```bash
./deploy_dashboard_now.sh
```
**Time:** 5-7 minutes  
**Difficulty:** Easy  
**Best for:** Quick deployment

### Option 2: Manual Control
```bash
cd dashboard
./deploy_streamlit_to_aws.sh
```
**Time:** 5-7 minutes  
**Difficulty:** Easy  
**Best for:** Custom configuration

### Option 3: Step-by-Step
See `STREAMLIT_AWS_DEPLOYMENT.md` for detailed manual steps.

**Time:** 15-20 minutes  
**Difficulty:** Medium  
**Best for:** Learning AWS

---

## 💰 Cost Breakdown

### Monthly Costs
- **EC2 t3.small:** ~$15/month (on-demand)
- **EBS Storage (20GB):** ~$2/month
- **Data Transfer:** ~$1/month
- **Total:** ~$18/month

### Save Money
1. **Reserved Instance (1-year):** Save 40% → $11/month
2. **Spot Instance:** Save 70% → $5/month (less reliable)
3. **Stop when not needed:** Only pay for storage (~$2/month)
4. **Use t3.micro:** $7.50/month (for low traffic)

---

## 🔧 Post-Deployment

### Check Status
```bash
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP
sudo systemctl status kisaanmitra-dashboard
```

### View Logs
```bash
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP
sudo journalctl -u kisaanmitra-dashboard -f
```

### Restart Service
```bash
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP
sudo systemctl restart kisaanmitra-dashboard
```

### Update Dashboard
```bash
# Upload new files
scp -i kisaanmitra-dashboard-key.pem -r dashboard ubuntu@YOUR-EC2-IP:/tmp/

# Apply updates
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP
sudo cp -r /tmp/dashboard/* /opt/kisaanmitra/dashboard/
sudo systemctl restart kisaanmitra-dashboard
```

---

## 🌐 Add Custom Domain (Optional)

### Step 1: Point Domain
In your domain registrar:
```
Type: A Record
Name: dashboard
Value: YOUR-EC2-IP
TTL: 300
```

### Step 2: Add SSL
```bash
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d dashboard.yourdomain.com
```

Now access at: `https://dashboard.yourdomain.com`

---

## 🛑 Stop/Terminate Instance

### Stop (Keep for later)
```bash
aws ec2 stop-instances --instance-ids YOUR-INSTANCE-ID --region ap-south-1
```
**Cost while stopped:** ~$2/month (storage only)

### Terminate (Delete everything)
```bash
aws ec2 terminate-instances --instance-ids YOUR-INSTANCE-ID --region ap-south-1
```
**Cost after termination:** $0

---

## 🐛 Troubleshooting

### "AWS CLI not configured"
```bash
aws configure
# Enter your credentials
```

### "Permission denied"
```bash
chmod 400 kisaanmitra-dashboard-key.pem
```

### "Connection refused"
Wait 2-3 minutes for instance to fully start, then try again.

### "Dashboard not loading"
```bash
# Check service status
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP
sudo systemctl status kisaanmitra-dashboard
sudo journalctl -u kisaanmitra-dashboard -n 50
```

### "AWS credentials error"
Verify IAM role is attached:
```bash
aws ec2 describe-instances --instance-ids YOUR-INSTANCE-ID \
    --query 'Reservations[0].Instances[0].IamInstanceProfile'
```

---

## 📊 Monitoring

### CloudWatch Metrics
- CPU Utilization
- Network In/Out
- Disk Read/Write
- Status Checks

### Set Up Alarms
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name kisaanmitra-high-cpu \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=YOUR-INSTANCE-ID \
    --evaluation-periods 2
```

---

## ✅ Success Checklist

After deployment, verify:

- [ ] Can access dashboard at http://YOUR-EC2-IP
- [ ] Dashboard shows farmer data from DynamoDB
- [ ] Knowledge graph loads correctly
- [ ] Conversation history displays
- [ ] Analytics charts render properly
- [ ] Service auto-starts on reboot
- [ ] Nginx reverse proxy working
- [ ] No errors in logs

---

## 🎓 Learn More

### Documentation
- `STREAMLIT_AWS_DEPLOYMENT.md` - Complete deployment guide
- `dashboard/README.md` - Dashboard features and usage
- `dashboard/HOSTING_GUIDE.md` - Alternative hosting options

### AWS Resources
- [EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [CloudWatch Monitoring](https://docs.aws.amazon.com/cloudwatch/)

---

## 🚀 Ready to Deploy?

### Quick Start
```bash
# 1. Configure AWS (if not done)
aws configure

# 2. Deploy dashboard
./deploy_dashboard_now.sh

# 3. Wait 5-7 minutes

# 4. Access your dashboard!
```

### What Happens Next
1. Script creates all AWS resources
2. Launches EC2 instance
3. Installs software and dependencies
4. Uploads your dashboard files
5. Starts the service
6. Gives you the public URL

### Expected Output
```
🚀 KisaanMitra Streamlit Dashboard - AWS EC2 Deployment
==========================================================

✅ AWS CLI configured
✅ Key pair created
✅ Security group created
✅ IAM role created
✅ Instance launched: i-xxxxx
✅ Instance is running!
✅ Public IP: 13.232.xxx.xxx
✅ SSH connection established
✅ Application files uploaded
✅ Service started

==========================================
🎉 Deployment Complete!
==========================================

Instance Details:
  Instance ID: i-xxxxx
  Public IP: 13.232.xxx.xxx
  Region: ap-south-1
  Instance Type: t3.small

Access URLs:
  Dashboard: http://13.232.xxx.xxx
  Direct Streamlit: http://13.232.xxx.xxx:8501

SSH Access:
  ssh -i kisaanmitra-dashboard-key.pem ubuntu@13.232.xxx.xxx
```

---

## 🎉 You're Ready!

Everything is set up and ready to deploy. Just run:

```bash
./deploy_dashboard_now.sh
```

And your Streamlit dashboard will be live on AWS in 5-7 minutes!

---

## 📞 Need Help?

- Check `STREAMLIT_AWS_DEPLOYMENT.md` for detailed troubleshooting
- Review AWS CloudWatch logs
- Test locally first: `streamlit run dashboard/streamlit_app.py`

---

**Status:** ✅ Ready to Deploy  
**Estimated Time:** 5-7 minutes  
**Estimated Cost:** ~$10-15/month  
**Difficulty:** Easy (automated)  

**Let's go! 🚀**