# 🔄 Dashboard Updated - Dynamic Data Loading

## ✅ What's New

The Streamlit dashboard has been updated with **real-time dynamic data loading** from DynamoDB!

### Key Features

1. **Auto-Refresh (30 seconds)**
   - Dashboard automatically refreshes every 30 seconds
   - Toggle on/off in sidebar
   - Shows live update time

2. **Dynamic Data Loading**
   - All data fetched directly from DynamoDB
   - No static/dummy data
   - Real-time farmer profiles
   - Live conversation history
   - Automatic cache refresh

3. **Smart Caching**
   - Farmer data: 30-second cache
   - Conversation data: 30-second cache
   - Knowledge graph: 60-second cache
   - AWS clients: 60-second cache

4. **Manual Refresh**
   - "Refresh Now" button in sidebar
   - Clears all caches
   - Instant data reload

## 🚀 Running the Dashboard

### Local
```bash
cd dashboard
streamlit run streamlit_app.py
```

### With Auto-Refresh
The dashboard will automatically refresh every 30 seconds when the toggle is ON (default).

## 📊 Pages

### 1. Overview
- **Live Metrics:**
  - Total farmers (from DynamoDB)
  - Villages count
  - Total conversations
  - Active users
- **Dynamic Charts:**
  - Crop distribution (real data)
  - Land distribution by crop
- **Auto-updates:** Every 30 seconds

### 2. Farmers
- **Real-time farmer list** from DynamoDB
- **Filters:**
  - By village
  - By district
- **Features:**
  - Live count
  - Total land calculation
  - Average land per farmer
  - CSV export with timestamp
- **Updates:** Instant on refresh

### 3. Conversations
- **Live conversation feed** from DynamoDB
- **Metrics:**
  - Total messages
  - Unique users
  - Messages per user
  - Last hour activity
- **Display:**
  - Last 20 conversations
  - User message + Bot response
  - Agent type
  - Timestamp
- **Updates:** Real-time

### 4. Knowledge Graph
- **Demo data** from JSON file
- **Metrics:**
  - Farmer count
  - Districts
  - Villages
  - Total land
- **Link:** Live dashboard URL

## 🔧 Technical Details

### Caching Strategy
```python
@st.cache_data(ttl=30)  # 30 seconds
def load_all_farmers():
    # Fetches from DynamoDB
    # Auto-refreshes every 30s

@st.cache_data(ttl=30)  # 30 seconds
def load_conversations():
    # Fetches from DynamoDB
    # Auto-refreshes every 30s

@st.cache_resource(ttl=60)  # 60 seconds
def get_aws_clients():
    # Connection pooling
    # Reuses connections
```

### Auto-Refresh Implementation
```python
# JavaScript-based auto-refresh
setTimeout(function(){
    window.location.reload();
}, 30000);  // 30 seconds
```

### Data Loading
- **Pagination Support:** Handles large datasets
- **Error Handling:** Graceful fallbacks
- **Performance:** Optimized queries
- **Real-time:** No stale data

## 📈 Performance

### Before (Static Data)
- ❌ Manual refresh required
- ❌ Dummy data only
- ❌ No real-time updates
- ❌ Stale information

### After (Dynamic Data)
- ✅ Auto-refresh every 30s
- ✅ Real DynamoDB data
- ✅ Live updates
- ✅ Always current
- ✅ Smart caching
- ✅ Fast load times

## 🎯 Use Cases

### 1. Live Monitoring
- Watch new farmers register in real-time
- See conversations as they happen
- Track system activity

### 2. Demo/Presentation
- Show live data to stakeholders
- Real-time updates during demo
- No manual refresh needed

### 3. Analytics
- Current farmer statistics
- Active user tracking
- Conversation patterns

## 🔄 Refresh Behavior

### Auto-Refresh (Default: ON)
- **Interval:** 30 seconds
- **Scope:** Entire page
- **Cache:** Cleared automatically
- **Toggle:** Sidebar checkbox

### Manual Refresh
- **Button:** "Refresh Now" in sidebar
- **Action:** Clears all caches
- **Effect:** Immediate data reload

### Cache Refresh
- **Farmers:** Every 30 seconds
- **Conversations:** Every 30 seconds
- **Knowledge Graph:** Every 60 seconds
- **AWS Clients:** Every 60 seconds

## 📱 Mobile Responsive
- Works on all devices
- Touch-friendly interface
- Responsive charts
- Mobile-optimized layout

## 🐛 Troubleshooting

### Dashboard Not Updating
1. Check auto-refresh toggle (should be ON)
2. Click "Refresh Now" button
3. Check AWS credentials
4. Verify DynamoDB access

### No Data Showing
1. Verify farmers are registered
2. Check DynamoDB tables exist
3. Confirm AWS region (ap-south-1)
4. Test AWS CLI access

### Slow Loading
1. Check internet connection
2. Verify AWS region latency
3. Reduce cache TTL if needed
4. Check DynamoDB throughput

## 🔐 Security

- **AWS Credentials:** IAM role or credentials file
- **Region:** ap-south-1 (Mumbai)
- **Tables:** Read-only access sufficient
- **No Data Modification:** Dashboard is read-only

## 📊 Data Sources

### DynamoDB Tables
1. **kisaanmitra-farmer-profiles**
   - User profiles
   - Registration data
   - Crop information

2. **kisaanmitra-conversations**
   - Chat history
   - User messages
   - Bot responses

3. **kisaanmitra-onboarding**
   - Onboarding status
   - User progress

### JSON Files
- **knowledge_graph_dummy_data.json**
  - Demo farmers
  - Village data
  - Relationships

## 🚀 Deployment

### Local
```bash
streamlit run dashboard/streamlit_app.py
```

### AWS EC2
```bash
./deploy_dashboard_now.sh
```

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy from `dashboard/streamlit_app.py`
4. Add AWS credentials in Secrets

## ✅ Testing

### Test Auto-Refresh
1. Open dashboard
2. Note current time in sidebar
3. Wait 30 seconds
4. Page should auto-refresh
5. Time should update

### Test Dynamic Data
1. Add new farmer via WhatsApp
2. Wait 30 seconds
3. Check dashboard
4. New farmer should appear

### Test Manual Refresh
1. Click "Refresh Now"
2. Data should reload immediately
3. Cache cleared
4. Latest data shown

## 📝 Changelog

### v2.0 (Dynamic Update)
- ✅ Added auto-refresh (30s)
- ✅ Dynamic DynamoDB data loading
- ✅ Smart caching with TTL
- ✅ Manual refresh button
- ✅ Live update indicator
- ✅ Pagination support
- ✅ Error handling
- ✅ Performance optimization

### v1.0 (Original)
- Static data
- Manual refresh only
- No caching
- Dummy data

## 🎉 Benefits

1. **Real-time Insights**
   - Always current data
   - No stale information
   - Live monitoring

2. **Better UX**
   - Auto-refresh
   - No manual intervention
   - Smooth updates

3. **Accurate Analytics**
   - Real farmer count
   - Actual conversations
   - True statistics

4. **Demo Ready**
   - Live data during presentations
   - Impressive real-time updates
   - Professional appearance

---

**Status:** ✅ Live and Running  
**Auto-Refresh:** ON (30s)  
**Data Source:** DynamoDB (ap-south-1)  
**Cache:** Smart TTL-based  
**Performance:** Optimized  

**Ready to use!** 🚀