import json
import urllib3
import os
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

http = urllib3.PoolManager()

# AWS Clients
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
s3 = boto3.client("s3", region_name="ap-south-1")

# Configuration
FINANCE_TABLE = os.environ.get("FINANCE_TABLE", "kisaanmitra-finance")
SCHEMES_TABLE = os.environ.get("SCHEMES_TABLE", "kisaanmitra-schemes")
BUDGET_BUCKET = os.environ.get("BUDGET_BUCKET", "kisaanmitra-budgets")

SYSTEM_PROMPT = """You are a Financial Planning Expert for Indian farmers. Your expertise:
- End-to-end budget planning (pre-planting to harvest)
- Government scheme matching and eligibility
- Input cost optimization (fertilizer, seeds, pesticides)
- Loan and subsidy planning
- Risk assessment (profit vs investment)
- Financial literacy in simple Hindi

Provide actionable financial advice. Keep responses practical and farmer-friendly in Hindi."""


def ask_bedrock_finance(user_message, context=None):
    """Query Bedrock with finance-specific system prompt"""
    
    messages = []
    
    if context:
        context_text = f"Financial Context:\n{json.dumps(context, indent=2, ensure_ascii=False)}\n\nFarmer Query: {user_message}"
        messages.append({
            "role": "user",
            "content": [{"text": context_text}]
        })
    else:
        messages.append({
            "role": "user",
            "content": [{"text": user_message}]
        })
    
    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",
        messages=messages,
        system=[{"text": SYSTEM_PROMPT}],
        inferenceConfig={"maxTokens": 600, "temperature": 0.7}
    )
    
    return response["output"]["message"]["content"][0]["text"]


def get_crop_budget_template(crop_name, land_size_acres):
    """Get detailed budget template for specific crop"""
    
    # Comprehensive budget templates (per acre)
    budgets = {
        "wheat": {
            "seeds": 1500,
            "fertilizer": 3500,
            "pesticides": 1200,
            "irrigation": 2000,
            "labor": 4000,
            "machinery": 2500,
            "misc": 1000,
            "total_cost": 15700,
            "expected_yield_quintal": 25,
            "expected_price_per_quintal": 2400,
            "expected_revenue": 60000,
            "expected_profit": 44300,
            "roi_percent": 282
        },
        "rice": {
            "seeds": 2000,
            "fertilizer": 4000,
            "pesticides": 1500,
            "irrigation": 3500,
            "labor": 5000,
            "machinery": 3000,
            "misc": 1200,
            "total_cost": 20200,
            "expected_yield_quintal": 30,
            "expected_price_per_quintal": 2200,
            "expected_revenue": 66000,
            "expected_profit": 45800,
            "roi_percent": 227
        },
        "cotton": {
            "seeds": 3000,
            "fertilizer": 5000,
            "pesticides": 3000,
            "irrigation": 2500,
            "labor": 6000,
            "machinery": 3500,
            "misc": 1500,
            "total_cost": 24500,
            "expected_yield_quintal": 15,
            "expected_price_per_quintal": 6500,
            "expected_revenue": 97500,
            "expected_profit": 73000,
            "roi_percent": 298
        },
        "sugarcane": {
            "seeds": 8000,
            "fertilizer": 6000,
            "pesticides": 2000,
            "irrigation": 4000,
            "labor": 8000,
            "machinery": 5000,
            "misc": 2000,
            "total_cost": 35000,
            "expected_yield_quintal": 400,
            "expected_price_per_quintal": 350,
            "expected_revenue": 140000,
            "expected_profit": 105000,
            "roi_percent": 300
        },
        "onion": {
            "seeds": 4000,
            "fertilizer": 4500,
            "pesticides": 2500,
            "irrigation": 3000,
            "labor": 7000,
            "machinery": 2000,
            "misc": 1500,
            "total_cost": 24500,
            "expected_yield_quintal": 100,
            "expected_price_per_quintal": 1500,
            "expected_revenue": 150000,
            "expected_profit": 125500,
            "roi_percent": 512
        },
        "potato": {
            "seeds": 5000,
            "fertilizer": 5000,
            "pesticides": 2000,
            "irrigation": 2500,
            "labor": 6000,
            "machinery": 3000,
            "misc": 1500,
            "total_cost": 25000,
            "expected_yield_quintal": 120,
            "expected_price_per_quintal": 1200,
            "expected_revenue": 144000,
            "expected_profit": 119000,
            "roi_percent": 476
        }
    }
    
    template = budgets.get(crop_name.lower(), budgets["wheat"])
    
    # Scale by land size
    scaled_budget = {}
    for key, value in template.items():
        if isinstance(value, (int, float)):
            scaled_budget[key] = int(value * land_size_acres)
        else:
            scaled_budget[key] = value
    
    scaled_budget["land_size_acres"] = land_size_acres
    scaled_budget["crop"] = crop_name
    
    return scaled_budget


def calculate_loan_eligibility(budget, farmer_income, credit_score=None, loan_purpose="crop", land_size=1):
    """
    Calculate smart loan eligibility based on user context
    
    Args:
        budget: Budget dict with total_cost
        farmer_income: Monthly income
        credit_score: Credit score (optional)
        loan_purpose: crop/equipment/land_improvement
        land_size: Land size in acres
    """
    
    total_cost = budget.get("total_cost", 0)
    
    # Loan type and limits based on purpose
    if loan_purpose == "crop":
        # Crop loans - typically 100% of cultivation cost
        max_loan_base = int(total_cost * 1.0)  # Full cost coverage
        loan_type = "Kisan Credit Card (KCC) - Crop Loan"
        tenure_months = 12  # One crop cycle
        interest_rate_base = 7.0
    elif loan_purpose == "equipment":
        # Equipment loans - up to 85% of cost
        max_loan_base = int(total_cost * 0.85)
        loan_type = "Farm Equipment Loan"
        tenure_months = 60  # 5 years
        interest_rate_base = 9.5
    else:
        # General agricultural loan
        max_loan_base = int(total_cost * 0.75)
        loan_type = "Agricultural Term Loan"
        tenure_months = 36  # 3 years
        interest_rate_base = 8.5
    
    # Adjust based on land size (collateral value)
    if land_size >= 5:
        max_loan = int(max_loan_base * 1.2)  # 20% more for larger landholdings
    elif land_size >= 2:
        max_loan = max_loan_base
    else:
        max_loan = int(max_loan_base * 0.9)  # Slightly lower for small farmers
    
    # Cap at ₹3 lakh for KCC without collateral
    if loan_purpose == "crop" and max_loan > 300000:
        max_loan = 300000
        requires_collateral = True
    else:
        requires_collateral = False
    
    # Interest rate adjustments
    if credit_score and credit_score > 750:
        interest_rate = interest_rate_base - 1.0  # 1% discount for good credit
    elif credit_score and credit_score > 650:
        interest_rate = interest_rate_base
    else:
        interest_rate = interest_rate_base + 1.5  # Higher rate for lower/no credit score
    
    # Interest subvention for crop loans (Government subsidy)
    if loan_purpose == "crop":
        interest_rate_effective = max(4.0, interest_rate - 3.0)  # 3% subvention
        has_subvention = True
    else:
        interest_rate_effective = interest_rate
        has_subvention = False
    
    # EMI calculation
    monthly_rate = interest_rate_effective / 12 / 100
    if monthly_rate > 0:
        emi = int(max_loan * monthly_rate * (1 + monthly_rate)**tenure_months / ((1 + monthly_rate)**tenure_months - 1))
    else:
        emi = int(max_loan / tenure_months)
    
    # Debt-to-income ratio (should be < 40%)
    monthly_income = farmer_income if farmer_income > 10000 else farmer_income * 30  # Assume monthly if > 10k, else daily
    dti_ratio = (emi / monthly_income * 100) if monthly_income > 0 else 100
    
    # Repayment capacity assessment
    if dti_ratio < 30:
        repayment_capacity = "excellent"
        approval_likelihood = "95%"
    elif dti_ratio < 40:
        repayment_capacity = "good"
        approval_likelihood = "80%"
    elif dti_ratio < 50:
        repayment_capacity = "moderate"
        approval_likelihood = "60%"
    else:
        repayment_capacity = "poor"
        approval_likelihood = "30%"
    
    # Smart recommendations
    recommendations = []
    
    if dti_ratio > 40:
        recommendations.append("⚠️ EMI is high relative to income. Consider:")
        recommendations.append("  • Reducing loan amount by 20-30%")
        recommendations.append("  • Using own funds for part of the cost")
        recommendations.append("  • Applying for government subsidies first")
    
    if loan_purpose == "crop" and not has_subvention:
        recommendations.append("💡 Apply through Kisan Credit Card for 3% interest subsidy")
    
    if land_size < 2:
        recommendations.append("💡 Check eligibility for small farmer subsidies (up to 50% on equipment)")
    
    if credit_score is None or credit_score < 650:
        recommendations.append("💡 Build credit score by:")
        recommendations.append("  • Timely repayment of existing loans")
        recommendations.append("  • Getting a small KCC and using it responsibly")
    
    # Alternative financing options
    alternatives = []
    if dti_ratio > 50:
        alternatives.append("Consider group farming/FPO for shared costs")
        alternatives.append("Explore government subsidies (can reduce cost by 40-60%)")
        alternatives.append("Start with smaller land area this season")
    
    return {
        "loan_type": loan_type,
        "max_loan_amount": max_loan,
        "interest_rate": interest_rate,
        "interest_rate_effective": interest_rate_effective,
        "has_subvention": has_subvention,
        "tenure_months": tenure_months,
        "monthly_emi": emi,
        "total_repayment": emi * tenure_months,
        "total_interest": (emi * tenure_months) - max_loan,
        "dti_ratio": round(dti_ratio, 2),
        "repayment_capacity": repayment_capacity,
        "approval_likelihood": approval_likelihood,
        "requires_collateral": requires_collateral,
        "recommendations": recommendations,
        "alternatives": alternatives,
        "documents_needed": [
            "Aadhaar card",
            "PAN card",
            "Land ownership documents" if requires_collateral else "Land records/lease",
            "Bank statements (6 months)",
            "Passport size photos"
        ]
    }


def match_government_schemes(crop, land_size, state="Maharashtra", income=None):
    """Match farmer with eligible government schemes - REAL SCHEMES ONLY"""
    
    schemes = []
    
    # 1. PM-KISAN (Universal - All farmers)
    schemes.append({
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "benefit": "₹6,000/year in 3 equal installments of ₹2,000",
        "eligibility": "All landholding farmers (no land size limit)",
        "status": "eligible",
        "how_to_apply": "Visit pmkisan.gov.in or nearest Common Service Centre (CSC)",
        "documents": ["Aadhaar card", "Land ownership documents", "Bank account with Aadhaar linking"],
        "official_website": "https://pmkisan.gov.in"
    })
    
    # 2. PMFBY - Crop Insurance (All farmers growing notified crops)
    premium_rate = "2%" if crop.lower() in ["rice", "wheat", "cotton", "sugarcane"] else "1.5%"
    schemes.append({
        "name": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
        "benefit": f"Comprehensive crop insurance with only {premium_rate} farmer premium",
        "eligibility": "All farmers growing notified crops in notified areas",
        "status": "eligible" if crop.lower() in ["rice", "wheat", "cotton", "sugarcane", "maize", "bajra", "tur"] else "check_eligibility",
        "how_to_apply": "Through your bank, insurance company, or CSC within crop cutting period",
        "documents": ["Land records", "Sowing certificate from Patwari", "Bank account", "Aadhaar"],
        "official_website": "https://pmfby.gov.in"
    })
    
    # 3. Kisan Credit Card (KCC) - For farmers with land
    schemes.append({
        "name": "Kisan Credit Card (KCC)",
        "benefit": "Credit up to ₹3 lakh at 7% interest (4% effective with 3% subvention)",
        "eligibility": "Farmers with land ownership or lease agreement",
        "status": "eligible",
        "how_to_apply": "Visit nearest bank branch (any nationalized/cooperative bank)",
        "documents": ["Land records/lease deed", "Aadhaar", "PAN card", "Passport size photos"],
        "official_website": "https://www.nabard.org/content1.aspx?id=523"
    })
    
    # 4. PM-KUSUM (Solar Pump) - For irrigation
    if crop.lower() in ["rice", "sugarcane", "cotton", "vegetables"]:
        subsidy_percent = "60%" if land_size <= 2 else "40%"
        schemes.append({
            "name": "PM-KUSUM (Solar Pump Scheme)",
            "benefit": f"{subsidy_percent} subsidy on solar pump installation + 30% bank loan",
            "eligibility": "Farmers with irrigation needs",
            "status": "eligible",
            "how_to_apply": "Apply through state nodal agency or DISCOM",
            "documents": ["Land documents", "Electricity connection details", "Bank account", "Aadhaar"],
            "official_website": "https://pmkusum.mnre.gov.in"
        })
    
    # 5. Soil Health Card Scheme (Universal)
    schemes.append({
        "name": "Soil Health Card Scheme",
        "benefit": "Free soil testing and nutrient recommendations every 2 years",
        "eligibility": "All farmers",
        "status": "eligible",
        "how_to_apply": "Contact District Agriculture Office or Krishi Vigyan Kendra",
        "documents": ["Land details", "Aadhaar"],
        "official_website": "https://soilhealth.dac.gov.in"
    })
    
    # 6. e-NAM (National Agriculture Market) - For selling produce
    schemes.append({
        "name": "e-NAM (National Agriculture Market)",
        "benefit": "Online trading platform for better price discovery and transparent auctions",
        "eligibility": "All farmers",
        "status": "eligible",
        "how_to_apply": "Register at nearest e-NAM mandi or online at enam.gov.in",
        "documents": ["Aadhaar", "Bank account", "Mobile number"],
        "official_website": "https://enam.gov.in"
    })
    
    # 7. Small/Marginal Farmer Schemes
    if land_size <= 2:
        schemes.append({
            "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
            "benefit": "40-50% subsidy on farm equipment (tractors, harvesters, etc.)",
            "eligibility": "Small and marginal farmers (up to 2 hectares)",
            "status": "eligible",
            "how_to_apply": "Apply through District Agriculture Office",
            "documents": ["Land records", "Aadhaar", "Income certificate", "Caste certificate (if applicable)"],
            "official_website": "Contact District Agriculture Office"
        })
    
    # 8. Micro Irrigation - For water-intensive crops
    if crop.lower() in ["cotton", "sugarcane", "vegetables", "fruits"]:
        schemes.append({
            "name": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY) - Micro Irrigation",
            "benefit": "55% subsidy on drip/sprinkler irrigation (up to 5 hectares)",
            "eligibility": "All farmers with water source",
            "status": "eligible",
            "how_to_apply": "Apply through District Agriculture Office with vendor quotation",
            "documents": ["Land records", "Water source proof", "Vendor quotation", "Aadhaar"],
            "official_website": "https://pmksy.gov.in"
        })
    
    # 9. Interest Subvention Scheme (Linked with KCC)
    schemes.append({
        "name": "Interest Subvention Scheme",
        "benefit": "3% interest subvention on crop loans (effective 4% interest)",
        "eligibility": "Farmers with Kisan Credit Card",
        "status": "eligible" if land_size > 0 else "conditional",
        "how_to_apply": "Automatic benefit with KCC - no separate application",
        "documents": ["KCC card"],
        "official_website": "Through your bank"
    })
    
    return schemes


def optimize_input_costs(budget):
    """Suggest cost optimization strategies"""
    
    optimizations = []
    
    # Fertilizer optimization
    if budget.get("fertilizer", 0) > 3000:
        savings = int(budget["fertilizer"] * 0.15)
        optimizations.append({
            "category": "fertilizer",
            "strategy": "Use soil testing + balanced NPK",
            "potential_savings": savings,
            "tip": "मिट्टी परीक्षण से 15% खाद बचाएं"
        })
    
    # Pesticide optimization
    if budget.get("pesticides", 0) > 2000:
        savings = int(budget["pesticides"] * 0.20)
        optimizations.append({
            "category": "pesticides",
            "strategy": "Integrated Pest Management (IPM)",
            "potential_savings": savings,
            "tip": "जैविक कीटनाशक से 20% बचत"
        })
    
    # Labor optimization
    if budget.get("labor", 0) > 5000:
        savings = int(budget["labor"] * 0.25)
        optimizations.append({
            "category": "labor",
            "strategy": "Mechanization + group hiring",
            "potential_savings": savings,
            "tip": "मशीनीकरण से 25% श्रम लागत कम करें"
        })
    
    # Irrigation optimization
    if budget.get("irrigation", 0) > 3000:
        savings = int(budget["irrigation"] * 0.30)
        optimizations.append({
            "category": "irrigation",
            "strategy": "Drip irrigation system",
            "potential_savings": savings,
            "tip": "ड्रिप सिंचाई से 30% पानी और बिजली बचाएं"
        })
    
    total_savings = sum([opt["potential_savings"] for opt in optimizations])
    
    return {
        "optimizations": optimizations,
        "total_potential_savings": total_savings,
        "optimized_cost": budget.get("total_cost", 0) - total_savings,
        "new_roi": round(((budget.get("expected_revenue", 0) - (budget.get("total_cost", 0) - total_savings)) / (budget.get("total_cost", 0) - total_savings)) * 100, 2) if budget.get("total_cost", 0) > total_savings else 0
    }


def assess_financial_risk(budget, loan_info, market_volatility="medium"):
    """Comprehensive risk assessment"""
    
    total_cost = budget.get("total_cost", 0)
    expected_revenue = budget.get("expected_revenue", 0)
    expected_profit = budget.get("expected_profit", 0)
    
    # Risk factors
    risks = []
    risk_score = 0
    
    # Market risk
    if market_volatility == "high":
        risks.append({
            "type": "market_risk",
            "level": "high",
            "impact": "Price fluctuation may reduce profit by 20-30%",
            "mitigation": "Consider contract farming or futures"
        })
        risk_score += 30
    elif market_volatility == "medium":
        risks.append({
            "type": "market_risk",
            "level": "medium",
            "impact": "Price may vary by 10-15%",
            "mitigation": "Monitor mandi prices regularly"
        })
        risk_score += 15
    
    # Weather risk
    risks.append({
        "type": "weather_risk",
        "level": "medium",
        "impact": "Drought/flood may reduce yield by 20%",
        "mitigation": "Take crop insurance (PMFBY)"
    })
    risk_score += 20
    
    # Debt risk
    if loan_info and loan_info.get("dti_ratio", 0) > 30:
        risks.append({
            "type": "debt_risk",
            "level": "high",
            "impact": "High debt burden may cause repayment issues",
            "mitigation": "Reduce loan amount or extend tenure"
        })
        risk_score += 25
    
    # Input cost risk
    if total_cost > expected_revenue * 0.4:
        risks.append({
            "type": "cost_risk",
            "level": "medium",
            "impact": "High input costs reduce profit margin",
            "mitigation": "Optimize inputs, use subsidies"
        })
        risk_score += 15
    
    # Overall assessment
    if risk_score < 30:
        risk_level = "low"
        recommendation = "Safe to proceed with planned investment"
    elif risk_score < 60:
        risk_level = "medium"
        recommendation = "Proceed with caution, implement risk mitigation"
    else:
        risk_level = "high"
        recommendation = "High risk - consider reducing investment or alternative crops"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risks": risks,
        "recommendation": recommendation,
        "insurance_recommended": True,
        "diversification_suggested": risk_score > 50
    }


def generate_financial_plan(crop, land_size, farmer_income, has_loan=False):
    """Generate comprehensive financial plan"""
    
    # Get budget
    budget = get_crop_budget_template(crop, land_size)
    
    # Calculate loan if needed
    loan_info = None
    if has_loan or farmer_income < budget["total_cost"]:
        loan_info = calculate_loan_eligibility(budget, farmer_income)
    
    # Match schemes
    schemes = match_government_schemes(crop, land_size, income=farmer_income)
    
    # Optimize costs
    optimizations = optimize_input_costs(budget)
    
    # Risk assessment
    risk = assess_financial_risk(budget, loan_info)
    
    # Calculate scheme benefits
    scheme_benefits = 6000  # PM-KISAN
    if land_size <= 2:
        scheme_benefits += int(budget.get("machinery", 0) * 0.5)  # 50% subsidy
    
    return {
        "budget": budget,
        "loan": loan_info,
        "schemes": schemes,
        "optimizations": optimizations,
        "risk_assessment": risk,
        "scheme_benefits": scheme_benefits,
        "net_investment": budget["total_cost"] - scheme_benefits - (loan_info["max_loan_amount"] if loan_info else 0),
        "final_profit": budget["expected_profit"] + scheme_benefits - (loan_info["total_interest"] if loan_info else 0)
    }


def save_financial_plan(user_id, plan):
    """Save financial plan to DynamoDB"""
    
    try:
        table = dynamodb.Table(FINANCE_TABLE)
        table.put_item(
            Item={
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "plan": json.loads(json.dumps(plan), parse_float=Decimal),
                "ttl": int((datetime.now() + timedelta(days=180)).timestamp())
            }
        )
        
        # Also save to S3 as PDF (future: generate PDF)
        s3.put_object(
            Bucket=BUDGET_BUCKET,
            Key=f"{user_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_plan.json",
            Body=json.dumps(plan, indent=2, ensure_ascii=False),
            ContentType="application/json"
        )
        
        return True
    except Exception as e:
        print(f"Error saving plan: {e}")
        return False


def format_financial_plan(plan):
    """Format financial plan for WhatsApp"""
    
    budget = plan["budget"]
    loan = plan.get("loan")
    optimizations = plan["optimizations"]
    risk = plan["risk_assessment"]
    
    message = f"*💰 {budget['crop'].title()} - Financial Plan*\n"
    message += f"*Land*: {budget['land_size_acres']} acres\n\n"
    
    message += "*📊 Budget Breakdown*\n"
    message += f"Seeds: ₹{budget['seeds']:,}\n"
    message += f"Fertilizer: ₹{budget['fertilizer']:,}\n"
    message += f"Pesticides: ₹{budget['pesticides']:,}\n"
    message += f"Labor: ₹{budget['labor']:,}\n"
    message += f"*Total Cost*: ₹{budget['total_cost']:,}\n\n"
    
    message += "*💵 Expected Returns*\n"
    message += f"Yield: {budget['expected_yield_quintal']} quintal\n"
    message += f"Revenue: ₹{budget['expected_revenue']:,}\n"
    message += f"*Profit*: ₹{budget['expected_profit']:,}\n"
    message += f"ROI: {budget['roi_percent']}%\n\n"
    
    if loan:
        message += "*🏦 Loan Details*\n"
        message += f"Amount: ₹{loan['max_loan_amount']:,}\n"
        message += f"Interest: {loan['interest_rate']}%\n"
        message += f"EMI: ₹{loan['monthly_emi']:,}/month\n\n"
    
    message += "*💡 Cost Savings*\n"
    message += f"Potential: ₹{optimizations['total_potential_savings']:,}\n"
    message += f"New Cost: ₹{optimizations['optimized_cost']:,}\n\n"
    
    message += f"*⚠️ Risk Level*: {risk['risk_level'].upper()}\n"
    message += f"{risk['recommendation']}\n\n"
    
    message += f"*🎁 Govt Benefits*: ₹{plan['scheme_benefits']:,}\n"
    message += f"*✅ Final Profit*: ₹{plan['final_profit']:,}"
    
    return message


def lambda_handler(event, context):
    """Lambda handler for finance agent"""
    
    print("Finance Agent Event:", event)
    
    try:
        body = json.loads(event.get("body", "{}"))
        
        query_type = body.get("type", "general")
        user_id = body.get("user_id", "unknown")
        
        if query_type == "budget_plan":
            crop = body.get("crop", "wheat")
            land_size = float(body.get("land_size", 1))
            income = int(body.get("income", 50000))
            has_loan = body.get("has_loan", False)
            
            plan = generate_financial_plan(crop, land_size, income, has_loan)
            save_financial_plan(user_id, plan)
            
            response = format_financial_plan(plan)
        
        elif query_type == "schemes":
            crop = body.get("crop", "wheat")
            land_size = float(body.get("land_size", 1))
            schemes = match_government_schemes(crop, land_size)
            
            response = "*🎁 Government Schemes*\n\n"
            for i, scheme in enumerate(schemes[:5], 1):
                response += f"{i}. *{scheme['name']}*\n"
                response += f"   {scheme['benefit']}\n"
                response += f"   Status: {scheme['status']}\n\n"
        
        elif query_type == "loan_check":
            budget_amount = int(body.get("budget", 20000))
            income = int(body.get("income", 50000))
            
            budget = {"total_cost": budget_amount}
            loan = calculate_loan_eligibility(budget, income)
            
            response = f"*🏦 Loan Eligibility*\n\n"
            response += f"Max Loan: ₹{loan['max_loan_amount']:,}\n"
            response += f"Interest: {loan['interest_rate']}%\n"
            response += f"EMI: ₹{loan['monthly_emi']:,}\n"
            response += f"Status: {loan['recommendation']}"
        
        else:
            # General query with AI
            user_message = body.get("message", "")
            response = ask_bedrock_finance(user_message)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "response": response
            })
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }
