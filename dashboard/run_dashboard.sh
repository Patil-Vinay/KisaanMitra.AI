#!/bin/bash

echo "🚀 Starting KisaanMitra.AI Dashboard..."
echo ""
echo "Dashboard will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run streamlit
streamlit run streamlit_app.py --server.port 8501 --server.address localhost
