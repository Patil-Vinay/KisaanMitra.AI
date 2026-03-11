#!/bin/bash

# Complete Demo - All 3 Agents with WhatsApp-style responses

clear

echo "KisaanMitra.AI - Live Demo"
echo "WhatsApp-based Multi-Agent AI for Farmers"
echo ""
sleep 2

# CROP AGENT DEMO
echo ""
echo "1. CROP AGENT - Disease Detection"
echo ""
sleep 1

./demo_crop_agent.sh

sleep 2

# MARKET AGENT DEMO
echo ""
echo "2. MARKET AGENT - Price Intelligence"
echo ""
sleep 1

./demo_market_agent.sh

sleep 2

# FINANCE AGENT DEMO
echo ""
echo "3. FINANCE AGENT - Budget Planning"
echo ""
sleep 1

./demo_finance_agent.sh

# Final Summary
echo ""
echo "Demo complete"
echo ""
echo "All 3 Agents Demonstrated:"
echo ""
echo "   Crop Agent"
echo "      • Disease detection from a leaf photo"
echo "      • Treatment recommendations"
echo "      • Hindi language support"
echo ""
echo "   Market Agent"
echo "      • Real-time mandi prices"
echo "      • Price trend analysis"
echo "      • Crop recommendations"
echo ""
echo "   Finance Agent"
echo "      • Complete budget planning"
echo "      • Loan eligibility calculator"
echo "      • Government scheme matching"
echo "      • Cost and profit estimate per acre"
echo ""
echo ""
