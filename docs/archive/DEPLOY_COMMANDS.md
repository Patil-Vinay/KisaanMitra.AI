# 🚀 Quick Deploy Commands

## Deploy Streamlit Dashboard to AWS

### One Command Deploy
```bash
./deploy_dashboard_now.sh
```

### Manual Deploy
```bash
cd dashboard
./deploy_streamlit_to_aws.sh
```

---

## Your Live Links

### Knowledge Graph (Already Live)
```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com
```

### Streamlit Dashboard (After Deployment)
```
http://YOUR-EC2-IP
```

---

## Quick Commands

### Check AWS Configuration
```bash
aws sts get-caller-identity
```

### Configure AWS (if needed)
```bash
aws configure
# Region: ap-south-1
```

### Test Dashboard Locally
```bash
cd dashboard
streamlit run streamlit_app.py
```

### SSH to EC2 (after deployment)
```bash
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP
```

### Check Service Status
```bash
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP \
  'sudo systemctl status kisaanmitra-dashboard'
```

### View Logs
```bash
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP \
  'sudo journalctl -u kisaanmitra-dashboard -f'
```

### Restart Service
```bash
ssh -i kisaanmitra-dashboard-key.pem ubuntu@YOUR-EC2-IP \
  'sudo systemctl restart kisaanmitra-dashboard'
```

### Stop Instance (save money)
```bash
aws ec2 stop-instances --instance-ids YOUR-INSTANCE-ID --region ap-south-1
```

### Start Instance
```bash
aws ec2 start-instances --instance-ids YOUR-INSTANCE-ID --region ap-south-1
```

### Terminate Instance (delete)
```bash
aws ec2 terminate-instances --instance-ids YOUR-INSTANCE-ID --region ap-south-1
```

---

## Deployment Time & Cost

- **Time:** 5-7 minutes
- **Cost:** ~$10-15/month
- **Instance:** t3.small (2 vCPU, 2GB RAM)
- **Region:** ap-south-1 (Mumbai)

---

## Files Created

- `deploy_dashboard_now.sh` - Quick deploy script
- `dashboard/deploy_streamlit_to_aws.sh` - Full deployment automation
- `STREAMLIT_AWS_DEPLOYMENT.md` - Complete guide
- `DASHBOARD_DEPLOYMENT_READY.md` - Quick start guide

---

## Ready to Deploy? 🚀

```bash
./deploy_dashboard_now.sh
```