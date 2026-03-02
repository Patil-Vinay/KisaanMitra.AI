# KisaanMitra Dashboard Hosting Guide

## Quick Start (Local)

```bash
cd dashboard
streamlit run streamlit_app.py
```

Access at: http://localhost:8501

---

## Option 1: Streamlit Community Cloud (Recommended - FREE)

### Pros
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Easy deployment
- ✅ Auto-updates from GitHub

### Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit dashboard"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `dashboard/streamlit_app.py`
   - Click "Deploy"

3. **Configure AWS Credentials**
   - In Streamlit Cloud dashboard, go to "Settings" → "Secrets"
   - Add your AWS credentials:
   ```toml
   AWS_ACCESS_KEY_ID = "your_access_key"
   AWS_SECRET_ACCESS_KEY = "your_secret_key"
   AWS_DEFAULT_REGION = "ap-south-1"
   ```

4. **Done!**
   - Your dashboard will be live at: `https://your-app-name.streamlit.app`

---

## Option 2: AWS EC2 (Full Control)

### Pros
- ✅ Full control
- ✅ Custom domain
- ✅ No resource limits
- ✅ Private hosting

### Cost
- ~$10-20/month (t3.small instance)

### Steps

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.small (2 vCPU, 2GB RAM)
   - Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
   - Storage: 20GB

2. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Upload Files**
   ```bash
   # From your local machine
   scp -i your-key.pem -r dashboard ubuntu@your-ec2-ip:/home/ubuntu/
   scp -i your-key.pem requirements.txt ubuntu@your-ec2-ip:/home/ubuntu/
   ```

4. **Run Deployment Script**
   ```bash
   # On EC2 instance
   cd /home/ubuntu
   chmod +x dashboard/deploy_to_ec2.sh
   sudo bash dashboard/deploy_to_ec2.sh
   ```

5. **Configure AWS Credentials**
   - Option A: Use IAM Role (Recommended)
     - Attach IAM role to EC2 with DynamoDB permissions
   - Option B: Use credentials file
     - Edit `~/.aws/credentials` with your keys

6. **Access Dashboard**
   - http://your-ec2-public-ip

7. **Optional: Add Custom Domain**
   - Point your domain to EC2 IP
   - Install SSL with Let's Encrypt:
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

---

## Option 3: AWS ECS Fargate (Serverless)

### Pros
- ✅ Serverless (no server management)
- ✅ Auto-scaling
- ✅ High availability

### Cost
- ~$15-30/month

### Steps

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY dashboard/requirements.txt .
   RUN pip install -r requirements.txt
   COPY dashboard/ .
   EXPOSE 8501
   CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and Push to ECR**
   ```bash
   aws ecr create-repository --repository-name kisaanmitra-dashboard
   docker build -t kisaanmitra-dashboard .
   docker tag kisaanmitra-dashboard:latest 482548785371.dkr.ecr.ap-south-1.amazonaws.com/kisaanmitra-dashboard:latest
   aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 482548785371.dkr.ecr.ap-south-1.amazonaws.com
   docker push 482548785371.dkr.ecr.ap-south-1.amazonaws.com/kisaanmitra-dashboard:latest
   ```

3. **Create ECS Service**
   - Use AWS Console or CLI to create ECS cluster, task definition, and service
   - Configure Application Load Balancer
   - Set environment variables for AWS credentials

---

## Option 4: Heroku (Easy Alternative)

### Pros
- ✅ Easy deployment
- ✅ Free tier available
- ✅ Git-based deployment

### Steps

1. **Create Heroku Files**
   
   `Procfile`:
   ```
   web: streamlit run dashboard/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy**
   ```bash
   heroku login
   heroku create kisaanmitra-dashboard
   heroku config:set AWS_ACCESS_KEY_ID=your_key
   heroku config:set AWS_SECRET_ACCESS_KEY=your_secret
   heroku config:set AWS_DEFAULT_REGION=ap-south-1
   git push heroku main
   ```

---

## Recommended Setup

For hackathon/demo: **Streamlit Community Cloud** (free, fast)
For production: **AWS EC2 with IAM role** (secure, scalable)

---

## Monitoring & Maintenance

### Check Service Status (EC2)
```bash
sudo systemctl status kisaanmitra-dashboard
```

### View Logs (EC2)
```bash
sudo journalctl -u kisaanmitra-dashboard -f
```

### Restart Service (EC2)
```bash
sudo systemctl restart kisaanmitra-dashboard
```

### Update Code (EC2)
```bash
cd /opt/kisaanmitra
git pull
sudo systemctl restart kisaanmitra-dashboard
```

---

## Security Best Practices

1. **Use IAM Roles** (EC2) instead of access keys
2. **Enable HTTPS** with SSL certificate
3. **Restrict Security Groups** to specific IPs if possible
4. **Use Secrets Manager** for sensitive data
5. **Enable CloudWatch** for monitoring
6. **Regular Updates** - keep packages updated

---

## Troubleshooting

### Dashboard not loading
- Check service status: `sudo systemctl status kisaanmitra-dashboard`
- Check logs: `sudo journalctl -u kisaanmitra-dashboard -f`
- Verify port 8501 is open: `sudo netstat -tlnp | grep 8501`

### AWS connection errors
- Verify IAM permissions for DynamoDB
- Check AWS credentials configuration
- Verify region is set to `ap-south-1`

### Performance issues
- Increase EC2 instance size (t3.medium or larger)
- Enable Streamlit caching
- Optimize DynamoDB queries

---

## Support

For issues or questions:
- Check logs first
- Review AWS CloudWatch metrics
- Test locally before deploying
