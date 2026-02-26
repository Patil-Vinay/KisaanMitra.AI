#!/bin/bash

# Install LangGraph and dependencies for Lambda deployment

set -e

echo "📦 Installing LangGraph dependencies for Lambda..."

# Create package directory if it doesn't exist
mkdir -p package

# Install dependencies
pip install \
    langgraph==0.2.45 \
    langchain-core==0.3.15 \
    langchain-aws==0.2.6 \
    -t package/ \
    --upgrade

echo "✅ LangGraph dependencies installed in package/"
echo ""
echo "📊 Package size:"
du -sh package/
echo ""
echo "Next steps:"
echo "1. Run: bash deploy_whatsapp.sh"
echo "2. This will include LangGraph in the deployment"
