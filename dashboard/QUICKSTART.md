# Quick Start Guide 🚀

## Run Dashboard

### Option 1: Using Script (Easiest)
```bash
cd dashboard
./run_dashboard.sh
```

### Option 2: Manual
```bash
cd dashboard
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Option 3: With Custom Port
```bash
streamlit run streamlit_app.py --server.port 8502
```

## Access Dashboard

Open browser and go to: **http://localhost:8501**

## Troubleshooting

### Port Already in Use
```bash
# Kill existing streamlit process
pkill -f streamlit

# Or use different port
streamlit run streamlit_app.py --server.port 8502
```

### Module Not Found
```bash
pip install streamlit boto3 pandas plotly
```

### AWS Credentials Error
```bash
# Configure AWS
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=ap-south-1
```

### Can't Load Knowledge Graph Data
The dashboard looks for `../demo/knowledge_graph_dummy_data.json`

Make sure you're running from the `dashboard/` directory.

## Features

- 📊 **Overview**: Real-time metrics and charts
- 👥 **Users**: All registered farmers
- 💬 **Conversations**: Recent WhatsApp chats  
- 🌐 **Knowledge Graph**: Village-level insights
- 📈 **Analytics**: Performance and revenue data

## Stop Dashboard

Press `Ctrl+C` in the terminal

---
**Need Help?** Check the full README.md
