# 🔗 KisaanMitra - Live Links

## 📊 Knowledge Graph Dashboard (LIVE)

```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com
```

**Status:** ✅ Live on AWS S3  
**Features:**
- Interactive D3.js visualization
- 50 farmers, 10 villages
- Drag-and-drop nodes
- Real-time statistics
- Kolhapur insights

---

## 🎯 Streamlit Analytics Dashboard

### Deploy to AWS EC2

```bash
./deploy_dashboard_now.sh
```

**Deployment Time:** 5-7 minutes  
**Cost:** ~$10-15/month  
**Instance:** t3.small (2 vCPU, 2GB RAM)

### After Deployment

Your dashboard will be available at:
```
http://YOUR-EC2-PUBLIC-IP
```

**Features:**
- ✅ Real-time data from DynamoDB
- ✅ Auto-refresh every 30 seconds
- ✅ Live farmer profiles
- ✅ Conversation monitoring
- ✅ Dynamic charts and analytics

---

## 🚀 Quick Deploy Commands

### Deploy Streamlit Dashboard
```bash
./deploy_dashboard_now.sh
```

### Test Locally First
```bash
cd dashboard
streamlit run streamlit_app.py
```
Then open: http://localhost:8501

---

## 📱 Share These Links

### For Evaluators/Demo

**Knowledge Graph:**
```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com
```

**Streamlit Dashboard:**
```
http://YOUR-EC2-IP (after deployment)
```

### QR Codes

Generate QR codes for easy mobile access:
- https://www.qr-code-generator.com/

---

## 🔄 Current Status

| Component | Status | URL |
|-----------|--------|-----|
| Knowledge Graph | ✅ Live | http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com |
| Streamlit Dashboard | 🚀 Ready to Deploy | Run `./deploy_dashboard_now.sh` |
| WhatsApp Bot | ✅ Live | Lambda function active |
| DynamoDB | ✅ Live | 3 registered users |

---

## 📊 What Each Dashboard Shows

### Knowledge Graph
- Interactive network visualization
- Village-level farmer connections
- Crop distribution
- Success rates
- Pattern discoveries

### Streamlit Dashboard
- Real-time farmer count
- Live conversation feed
- Crop analytics
- Land distribution
- User management
- Export capabilities

---

## 🎯 Next Steps

1. **Deploy Streamlit Dashboard:**
   ```bash
   ./deploy_dashboard_now.sh
   ```

2. **Get Your EC2 IP:**
   - Script will display it after deployment
   - Or check AWS Console → EC2 → Instances

3. **Access Dashboard:**
   - Open: http://YOUR-EC2-IP
   - Auto-refresh is enabled by default

4. **Share Links:**
   - Knowledge Graph: Already live
   - Streamlit: Your EC2 IP

---

## 💡 Tips

- **Knowledge Graph:** Works on mobile, desktop, tablets
- **Streamlit:** Best on desktop, works on mobile
- **Auto-Refresh:** Dashboard updates every 30 seconds
- **Data:** All live from DynamoDB

---

**Last Updated:** March 8, 2026  
**Git Commit:** Latest push successful  
**Ready for Demo:** ✅ Yes