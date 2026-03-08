# 🚀 Dashboard Quick Start

## Start Dashboard Locally

```bash
cd dashboard
streamlit run streamlit_app.py
```

Then open: http://localhost:8501

## ✨ New Features

### Auto-Refresh (Every 30 seconds)
- ✅ Enabled by default
- Toggle in sidebar
- Shows live update time

### Dynamic Data
- ✅ Real-time from DynamoDB
- ✅ Live farmer profiles
- ✅ Current conversations
- ✅ Actual statistics

### Manual Refresh
- Click "🔄 Refresh Now" in sidebar
- Instant data reload

## 📊 What You'll See

### Overview Page
- Total farmers (live count)
- Villages covered
- Total conversations
- Active users
- Crop distribution charts
- Land distribution

### Farmers Page
- All registered farmers
- Filter by village/district
- Export to CSV
- Live updates

### Conversations Page
- Last 20 conversations
- User messages + Bot responses
- Real-time activity
- Hourly statistics

### Knowledge Graph Page
- Demo data visualization
- Link to live dashboard

## 🔄 Updates

- **Auto:** Every 30 seconds
- **Manual:** Click refresh button
- **Cache:** 30-60 second TTL

## 📱 Access

- **Local:** http://localhost:8501
- **AWS:** Deploy with `./deploy_dashboard_now.sh`

---

**All data is now live from DynamoDB!** 🎉
