#!/bin/bash

# Run KisaanMitra Knowledge Graph Dashboard
# This script sets up and runs the Streamlit dashboard

echo "🌾 Starting KisaanMitra Knowledge Graph Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set AWS credentials (if not already set)
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "⚠️  AWS credentials not found in environment"
    echo "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    echo "Or configure AWS CLI: aws configure"
fi

# Run Streamlit app
echo ""
echo "✅ Starting dashboard..."
echo "📊 Dashboard will open in your browser at http://localhost:8501"
echo ""

streamlit run streamlit_app.py
