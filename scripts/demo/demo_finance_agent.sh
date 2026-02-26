#!/bin/bash

# Demo Finance Agent - Shows WhatsApp-style responses

echo "💰 FINANCE AGENT DEMO"
echo "====================="
echo ""

# Query 1: Budget Plan
echo "👨‍🌾 Farmer: 2 एकड़ गेहूं के लिए बजट बताओ"
echo ""
sleep 1

python3 << 'EOF'
import sys
sys.path.insert(0, 'src/finance_agent')
from finance_agent import generate_financial_plan, format_financial_plan

plan = generate_financial_plan("wheat", 2, 50000, has_loan=True)
response = format_financial_plan(plan)

print("🤖 Finance Agent:")
print(response)
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Query 2: Loan Check
echo "👨‍🌾 Farmer: मुझे कितना लोन मिल सकता है?"
echo ""
sleep 1

python3 << 'EOF'
import sys
sys.path.insert(0, 'src/finance_agent')
from finance_agent import calculate_loan_eligibility

budget = {"total_cost": 30000}
loan = calculate_loan_eligibility(budget, 50000, credit_score=720)

print("🤖 Finance Agent:")
print("*🏦 Loan Eligibility*\n")
print(f"Max Loan: ₹{loan['max_loan_amount']:,}")
print(f"Interest Rate: {loan['interest_rate']}%")
print(f"Monthly EMI: ₹{loan['monthly_emi']:,}")
print(f"Total Repayment: ₹{loan['total_repayment']:,}")
print(f"Total Interest: ₹{loan['total_interest']:,}")
print(f"\nStatus: {loan['recommendation'].upper()}")
print("\n💡 Apply at your nearest bank with land documents")
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Query 3: Government Schemes
echo "👨‍🌾 Farmer: कौन सी सरकारी योजनाएं हैं?"
echo ""
sleep 1

python3 << 'EOF'
import sys
sys.path.insert(0, 'src/finance_agent')
from finance_agent import match_government_schemes

schemes = match_government_schemes("wheat", 2)

print("🤖 Finance Agent:")
print("*🎁 Government Schemes*\n")
for i, scheme in enumerate(schemes[:5], 1):
    print(f"{i}. *{scheme['name']}*")
    print(f"   {scheme['benefit']}")
    print(f"   Status: {scheme['status']}")
    print()
print("💡 Visit your nearest agriculture office to apply")
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Query 4: Cost Optimization
echo "👨‍🌾 Farmer: खर्च कैसे कम करूं?"
echo ""
sleep 1

python3 << 'EOF'
import sys
sys.path.insert(0, 'src/finance_agent')
from finance_agent import get_crop_budget_template, optimize_input_costs

budget = get_crop_budget_template("wheat", 2)
optimizations = optimize_input_costs(budget)

print("🤖 Finance Agent:")
print("*💡 Cost Optimization Tips*\n")
for opt in optimizations['optimizations']:
    print(f"• {opt['category'].title()}")
    print(f"  Strategy: {opt['strategy']}")
    print(f"  Savings: ₹{opt['potential_savings']:,}")
    print(f"  {opt['tip']}")
    print()
print(f"*Total Potential Savings: ₹{optimizations['total_potential_savings']:,}*")
print(f"New Cost: ₹{optimizations['optimized_cost']:,}")
print(f"Improved ROI: {optimizations['new_roi']}%")
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
