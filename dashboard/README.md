# KisaanMitra.AI Streamlit Dashboard 🌾

Real-time analytics and monitoring dashboard for KisaanMitra.AI

## Features

- 📊 **Overview Dashboard**: Key metrics, charts, and statistics
- 👥 **User Management**: View all registered farmers
- 💬 **Conversations**: Monitor real-time conversations
- 🌐 **Knowledge Graph**: Explore village-level farmer network
- 📈 **Analytics**: Advanced performance and revenue analytics

## Setup

### 1. Install Dependencies

```bash
cd dashboard
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Make sure your AWS credentials are configured:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=ap-south-1
```

### 3. Run Dashboard

```bash
streamlit run streamlit_app.py
```

The dashboard will open at: http://localhost:8501

## Dashboard Pages

### 📊 Overview
- Total farmers, villages, crops
- Crop distribution pie chart
- User growth trend
- Top villages by farmers

### 👥 Users
- List of all registered farmers
- Download CSV export
- Real-time data from DynamoDB

### 💬 Conversations
- Recent WhatsApp conversations
- User messages and bot responses
- Agent routing information

### 🌐 Knowledge Graph
- Village-level statistics
- Farmer distribution by village
- Crop insights per village
- Link to live graph dashboard

### 📈 Analytics
- System performance metrics
- Response time trends
- Revenue analytics by crop
- Crop yield comparisons

## Data Sources

- **DynamoDB Tables**:
  - `kisaanmitra-farmer-profiles` - User profiles
  - `kisaanmitra-conversations` - Chat history
  - `kisaanmitra-onboarding` - Onboarding state

- **Knowledge Graph**:
  - `demo/knowledge_graph_dummy_data.json` - Demo data

## Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Select `dashboard/streamlit_app.py` as main file
5. Add AWS credentials in Secrets:

```toml
[aws]
AWS_ACCESS_KEY_ID = "your_key"
AWS_SECRET_ACCESS_KEY = "your_secret"
AWS_DEFAULT_REGION = "ap-south-1"
```

### Deploy to EC2

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt

# Run with nohup
nohup streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
```

Access at: http://your-ec2-ip:8501

## Screenshots

### Overview Dashboard
![Overview](https://via.placeholder.com/800x400/2E7D32/FFFFFF?text=Overview+Dashboard)

### Knowledge Graph
![Knowledge Graph](https://via.placeholder.com/800x400/667eea/FFFFFF?text=Knowledge+Graph)

### Analytics
![Analytics](https://via.placeholder.com/800x400/43e97b/FFFFFF?text=Analytics)

## Customization

### Add New Metrics

Edit `streamlit_app.py` and add your metrics:

```python
st.metric("Your Metric", "Value", "Change")
```

### Add New Charts

Use Plotly for interactive charts:

```python
import plotly.express as px

fig = px.bar(data, x='column1', y='column2')
st.plotly_chart(fig)
```

### Change Theme

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2E7D32"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## Troubleshooting

### AWS Credentials Error
```
Make sure AWS credentials are configured correctly
```
**Solution**: Run `aws configure` or set environment variables

### Module Not Found
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution**: Run `pip install -r requirements.txt`

### Connection Timeout
```
Error loading user data: Connection timeout
```
**Solution**: Check AWS region and network connectivity

## Support

For issues or questions:
- GitHub Issues: [Create Issue](https://github.com/your-repo/issues)
- Email: support@kisaanmitra.ai

---
**Built with ❤️ for Indian Farmers**
