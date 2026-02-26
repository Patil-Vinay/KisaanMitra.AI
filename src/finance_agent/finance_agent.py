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


def calculate_loan_eligibility(budget, farmer_income, credit_score=None):
    """Calculate loan eligibility and recommendations"""
    
    total_cost = budget.get("total_cost", 0)
    
    # Loan eligibility (typically 80% of total cost)
    max_loan = int(total_cost * 0.8)
    
    # Interest rates based on credit score
    if credit_score and credit_score > 750:
        interest_rate = 7.0  # Priority sector lending
    elif credit_score and credit_score > 650:
        interest_rate = 9.0
    else:
        interest_rate = 11.0  # Standard rate
    
    # EMI calculation (6 months repayment typical for crop loans)
    months = 6
    monthly_rate = interest_rate / 12 / 100
    emi = int(max_loan * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1))
    
    # Debt-to-income ratio
    dti_ratio = (emi * months) / (farmer_income * 6) if farmer_income > 0 else 0
    
    return {
        "max_loan_amount": max_loan,
        "interest_rate": interest_rate,
        "monthly_emi": emi,
        "total_repayment": emi * months,
        "total_interest": (emi * months) - max_loan,
        "dti_ratio": round(dti_ratio * 100, 2),
        "recommendation": "approved" if dti_ratio < 0.4 else "needs_review"
    }


def match_government_schemes(crop, land_size, state="Maharashtra", income=None):
    """Match farmer with eligible government schemes"""
    
    schemes = []
    
    # PM-KISAN (all farmers)
    schemes.append({
        "name": "PM-KISAN",
        "benefit": "₹6,000/year (₹2,000 per installment)",
        "eligibility": "All landholding farmers",
        "status": "eligible",
        "how_to_apply": "Visit pmkisan.gov.in or nearest CSC",
        "documents": ["Aadhaar", "Land records", "Bank account"]
    })
    
    # Crop Insurance (PMFBY)
    schemes.append({
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "benefit": f"Crop insurance with 2% premium for {crop}",
        "eligibility": "All farmers growing notified crops",
        "status": "eligible",
        "how_to_apply": "Through bank or insurance company",
        "documents": ["Land records", "Sowing certificate", "Bank account"]
    })
    
    # Kisan Credit Card
    schemes.append({
        "name": "Kisan Credit Card (KCC)",
        "benefit": "Credit up to ₹3 lakh at 7% interest",
        "eligibility": "Farmers with land ownership",
        "status": "eligible",
        "how_to_apply": "Visit nearest bank branch",
        "documents": ["Land records", "Aadhaar", "PAN card"]
    })
    
    # Small/Marginal farmer schemes
    if land_size <= 2:
        schemes.append({
            "name": "National Mission for Sustainable Agriculture",
            "benefit": "50% subsidy on farm equipment",
            "eligibility": "Small and marginal farmers",
            "status": "eligible",
            "how_to_apply": "District agriculture office",
            "documents": ["Land records", "Aadhaar", "Income certificate"]
        })
    
    # Drip irrigation subsidy
    if crop in ["cotton", "sugarcane", "vegetables"]:
        schemes.append({
            "name": "Micro Irrigation Scheme",
            "benefit": "60% subsidy on drip/sprinkler systems",
            "eligibility": "All farmers",
            "status": "eligible",
            "how_to_apply": "Agriculture department",
            "documents": ["Land records", "Quotation from vendor"]
        })
    
    # Organic farming
    schemes.append({
        "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "benefit": "₹50,000/hectare for organic farming",
        "eligibility": "Farmers adopting organic methods",
        "status": "conditional",
        "how_to_apply": "Form farmer groups, apply through agriculture dept",
        "documents": ["Land records", "Group formation certificate"]
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
