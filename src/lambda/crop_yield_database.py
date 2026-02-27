"""
Crop Yield Database - Realistic yield ranges and ROI limits for Indian crops
Based on government agricultural data and state-specific averages
"""

# Realistic yield ranges per acre (in quintals unless specified)
CROP_YIELD_RANGES = {
    # Pulses (Dal)
    "tur": {"min": 4, "max": 8, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 15000, "max": 25000}},
    "tur dal": {"min": 4, "max": 8, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 15000, "max": 25000}},
    "arhar": {"min": 4, "max": 8, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 15000, "max": 25000}},
    "moong": {"min": 3, "max": 6, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 12000, "max": 20000}},
    "moong dal": {"min": 3, "max": 6, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 12000, "max": 20000}},
    "urad": {"min": 3, "max": 6, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 12000, "max": 20000}},
    "urad dal": {"min": 3, "max": 6, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 12000, "max": 20000}},
    "chana": {"min": 8, "max": 15, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 15000, "max": 25000}},
    "gram": {"min": 8, "max": 15, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 15000, "max": 25000}},
    "masoor": {"min": 5, "max": 10, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 12000, "max": 20000}},
    "lentil": {"min": 5, "max": 10, "unit": "quintal", "category": "pulse", "cost_per_acre": {"min": 12000, "max": 20000}},
    
    # Cereals
    "rice": {"min": 20, "max": 35, "unit": "quintal", "category": "cereal", "cost_per_acre": {"min": 20000, "max": 35000}},
    "paddy": {"min": 20, "max": 35, "unit": "quintal", "category": "cereal", "cost_per_acre": {"min": 20000, "max": 35000}},
    "wheat": {"min": 25, "max": 45, "unit": "quintal", "category": "cereal", "cost_per_acre": {"min": 18000, "max": 30000}},
    "maize": {"min": 20, "max": 40, "unit": "quintal", "category": "cereal", "cost_per_acre": {"min": 15000, "max": 25000}},
    "corn": {"min": 20, "max": 40, "unit": "quintal", "category": "cereal", "cost_per_acre": {"min": 15000, "max": 25000}},
    "bajra": {"min": 10, "max": 20, "unit": "quintal", "category": "cereal", "cost_per_acre": {"min": 10000, "max": 18000}},
    "pearl millet": {"min": 10, "max": 20, "unit": "quintal", "category": "cereal", "cost_per_acre": {"min": 10000, "max": 18000}},
    "jowar": {"min": 10, "max": 20, "unit": "quintal", "category": "cereal", "cost_per_acre": {"min": 10000, "max": 18000}},
    "sorghum": {"min": 10, "max": 20, "unit": "quintal", "category": "cereal", "cost_per_acre": {"min": 10000, "max": 18000}},
    
    # Oilseeds
    "soybean": {"min": 10, "max": 20, "unit": "quintal", "category": "oilseed", "cost_per_acre": {"min": 15000, "max": 25000}},
    "groundnut": {"min": 12, "max": 25, "unit": "quintal", "category": "oilseed", "cost_per_acre": {"min": 18000, "max": 30000}},
    "peanut": {"min": 12, "max": 25, "unit": "quintal", "category": "oilseed", "cost_per_acre": {"min": 18000, "max": 30000}},
    "sunflower": {"min": 8, "max": 15, "unit": "quintal", "category": "oilseed", "cost_per_acre": {"min": 12000, "max": 22000}},
    "mustard": {"min": 8, "max": 15, "unit": "quintal", "category": "oilseed", "cost_per_acre": {"min": 10000, "max": 18000}},
    "sesame": {"min": 3, "max": 6, "unit": "quintal", "category": "oilseed", "cost_per_acre": {"min": 8000, "max": 15000}},
    
    # Cash Crops
    "cotton": {"min": 10, "max": 20, "unit": "quintal", "category": "cash_crop", "cost_per_acre": {"min": 25000, "max": 40000}},
    "sugarcane": {"min": 60, "max": 110, "unit": "ton", "category": "cash_crop", "cost_per_acre": {"min": 50000, "max": 80000}},  # Sugarcane in TONS not quintals
    "tobacco": {"min": 10, "max": 18, "unit": "quintal", "category": "cash_crop", "cost_per_acre": {"min": 30000, "max": 50000}},
    
    # Vegetables (high value, higher yields, higher costs)
    "tomato": {"min": 100, "max": 250, "unit": "quintal", "category": "vegetable", "cost_per_acre": {"min": 40000, "max": 70000}},
    "potato": {"min": 80, "max": 200, "unit": "quintal", "category": "vegetable", "cost_per_acre": {"min": 35000, "max": 60000}},
    "onion": {"min": 80, "max": 180, "unit": "quintal", "category": "vegetable", "cost_per_acre": {"min": 40000, "max": 70000}},
    "cabbage": {"min": 100, "max": 250, "unit": "quintal", "category": "vegetable", "cost_per_acre": {"min": 35000, "max": 60000}},
    "cauliflower": {"min": 80, "max": 200, "unit": "quintal", "category": "vegetable", "cost_per_acre": {"min": 35000, "max": 60000}},
    "brinjal": {"min": 100, "max": 250, "unit": "quintal", "category": "vegetable", "cost_per_acre": {"min": 30000, "max": 55000}},
    "eggplant": {"min": 100, "max": 250, "unit": "quintal", "category": "vegetable", "cost_per_acre": {"min": 30000, "max": 55000}},
    "okra": {"min": 40, "max": 80, "unit": "quintal", "category": "vegetable", "cost_per_acre": {"min": 25000, "max": 45000}},
    "bhindi": {"min": 40, "max": 80, "unit": "quintal", "category": "vegetable", "cost_per_acre": {"min": 25000, "max": 45000}},
    
    # Fruits
    "banana": {"min": 200, "max": 400, "unit": "quintal", "category": "fruit", "cost_per_acre": {"min": 50000, "max": 90000}},
    "papaya": {"min": 150, "max": 300, "unit": "quintal", "category": "fruit", "cost_per_acre": {"min": 40000, "max": 70000}},
    "mango": {"min": 40, "max": 100, "unit": "quintal", "category": "fruit", "cost_per_acre": {"min": 30000, "max": 60000}},
    "guava": {"min": 60, "max": 120, "unit": "quintal", "category": "fruit", "cost_per_acre": {"min": 25000, "max": 50000}},
}

# Maximum realistic ROI by crop category (%)
MAX_ROI_BY_CATEGORY = {
    "pulse": 100,        # Pulses: 50-100% ROI is realistic
    "cereal": 80,        # Cereals: 40-80% ROI
    "oilseed": 90,       # Oilseeds: 50-90% ROI
    "cash_crop": 120,    # Cash crops: 60-120% ROI
    "vegetable": 150,    # Vegetables: 80-150% ROI (high value)
    "fruit": 200,        # Fruits: 100-200% ROI (perennial, high value)
}

# Minimum realistic ROI (below this is concerning)
MIN_REALISTIC_ROI = 20  # Below 20% ROI is not economically viable for most farmers


def get_yield_range(crop_name):
    """Get realistic yield range for a crop"""
    crop_lower = crop_name.lower().strip()
    
    # Direct match
    if crop_lower in CROP_YIELD_RANGES:
        return CROP_YIELD_RANGES[crop_lower]
    
    # Partial match (e.g., "tur" in "tur dal")
    for key, value in CROP_YIELD_RANGES.items():
        if key in crop_lower or crop_lower in key:
            return value
    
    return None


def validate_yield(crop_name, yield_per_acre):
    """
    Validate if yield per acre is realistic
    Returns: (is_valid, corrected_yield, message)
    """
    yield_range = get_yield_range(crop_name)
    
    if not yield_range:
        # Unknown crop, can't validate
        return (True, yield_per_acre, "Unknown crop, cannot validate yield")
    
    min_yield = yield_range["min"]
    max_yield = yield_range["max"]
    unit = yield_range["unit"]
    
    if yield_per_acre < min_yield:
        return (False, min_yield, f"Yield too low. Minimum realistic: {min_yield} {unit}/acre")
    
    if yield_per_acre > max_yield * 1.5:  # Allow 50% buffer above max
        corrected = (min_yield + max_yield) // 2  # Use average
        return (False, corrected, f"Yield unrealistic ({yield_per_acre} {unit}/acre). Corrected to {corrected} {unit}/acre (realistic range: {min_yield}-{max_yield})")
    
    return (True, yield_per_acre, "Yield is realistic")


def validate_roi(crop_name, roi_percentage):
    """
    Validate if ROI is realistic for the crop category
    Returns: (is_valid, message)
    """
    yield_range = get_yield_range(crop_name)
    
    if not yield_range:
        # Unknown crop, can't validate
        return (True, "Unknown crop, cannot validate ROI")
    
    category = yield_range["category"]
    max_roi = MAX_ROI_BY_CATEGORY.get(category, 100)
    
    if roi_percentage < 0:
        return (True, f"Negative ROI ({roi_percentage:.0f}%) - crop not profitable in current conditions")
    
    if roi_percentage < MIN_REALISTIC_ROI:
        return (True, f"Low ROI ({roi_percentage:.0f}%) - economically challenging")
    
    if roi_percentage > max_roi * 1.5:  # Allow 50% buffer
        return (False, f"ROI unrealistic ({roi_percentage:.0f}%). Maximum realistic for {category}: {max_roi}%")
    
    return (True, f"ROI is realistic ({roi_percentage:.0f}%)")


def get_crop_category(crop_name):
    """Get crop category"""
    yield_range = get_yield_range(crop_name)
    if yield_range:
        return yield_range["category"]
    return "unknown"


def validate_cost(crop_name, total_cost_per_acre):
    """
    Validate if total cost per acre is realistic
    Returns: (is_valid, corrected_cost, message)
    """
    yield_range = get_yield_range(crop_name)
    
    if not yield_range or "cost_per_acre" not in yield_range:
        # Unknown crop or no cost data, can't validate
        return (True, total_cost_per_acre, "Unknown crop or no cost data, cannot validate")
    
    min_cost = yield_range["cost_per_acre"]["min"]
    max_cost = yield_range["cost_per_acre"]["max"]
    
    if total_cost_per_acre < min_cost * 0.5:  # Less than 50% of minimum
        corrected = (min_cost + max_cost) // 2  # Use average
        return (False, corrected, f"Cost too low (₹{total_cost_per_acre}/acre). Realistic range: ₹{min_cost:,}-₹{max_cost:,}/acre. Corrected to ₹{corrected:,}/acre")
    
    if total_cost_per_acre > max_cost * 1.5:  # More than 150% of maximum
        corrected = (min_cost + max_cost) // 2  # Use average
        return (False, corrected, f"Cost too high (₹{total_cost_per_acre}/acre). Realistic range: ₹{min_cost:,}-₹{max_cost:,}/acre. Corrected to ₹{corrected:,}/acre")
    
    return (True, total_cost_per_acre, f"Cost is realistic (₹{total_cost_per_acre:,}/acre, range: ₹{min_cost:,}-₹{max_cost:,})")


# Additional cost components that must be included
ADDITIONAL_COST_COMPONENTS = {
    "sugarcane": {
        "harvesting_per_ton": 150,  # ₹150 per ton harvesting cost
        "transport_per_ton": 100,   # ₹100 per ton transport to mill
        "electricity_diesel": 3000,  # ₹3000 per acre for irrigation
        "miscellaneous_percent": 8,  # 8% buffer for misc costs
        "interest_percent": 0,       # Interest if applicable (0 for now)
    },
    "cotton": {
        "harvesting_per_quintal": 50,
        "transport_per_quintal": 30,
        "electricity_diesel": 2000,
        "miscellaneous_percent": 7,
        "interest_percent": 0,
    },
    "default": {
        "harvesting_per_quintal": 40,
        "transport_per_quintal": 25,
        "electricity_diesel": 1500,
        "miscellaneous_percent": 7,
        "interest_percent": 0,
    }
}


def calculate_additional_costs(crop_name, yield_amount, base_cost):
    """
    Calculate additional costs (harvesting, transport, misc)
    Returns: dict with breakdown
    """
    crop_lower = crop_name.lower().strip()
    
    # Get cost components for this crop
    if crop_lower in ADDITIONAL_COST_COMPONENTS:
        components = ADDITIONAL_COST_COMPONENTS[crop_lower]
    else:
        components = ADDITIONAL_COST_COMPONENTS["default"]
    
    additional_costs = {}
    
    # Harvesting cost (per unit of yield)
    if "harvesting_per_ton" in components:
        additional_costs["harvesting"] = int(yield_amount * components["harvesting_per_ton"])
    elif "harvesting_per_quintal" in components:
        additional_costs["harvesting"] = int(yield_amount * components["harvesting_per_quintal"])
    else:
        additional_costs["harvesting"] = 0
    
    # Transport cost (per unit of yield)
    if "transport_per_ton" in components:
        additional_costs["transport"] = int(yield_amount * components["transport_per_ton"])
    elif "transport_per_quintal" in components:
        additional_costs["transport"] = int(yield_amount * components["transport_per_quintal"])
    else:
        additional_costs["transport"] = 0
    
    # Electricity/Diesel
    additional_costs["electricity_diesel"] = components.get("electricity_diesel", 0)
    
    # Miscellaneous (percentage of base cost)
    misc_percent = components.get("miscellaneous_percent", 7)
    additional_costs["miscellaneous"] = int(base_cost * misc_percent / 100)
    
    # Interest (if applicable)
    interest_percent = components.get("interest_percent", 0)
    if interest_percent > 0:
        additional_costs["interest"] = int(base_cost * interest_percent / 100)
    else:
        additional_costs["interest"] = 0
    
    additional_costs["total_additional"] = sum(additional_costs.values())
    
    return additional_costs


def enforce_mathematical_accuracy(budget_dict):
    """
    Enforce mathematical accuracy on all financial calculations
    This function MUST be called before returning any budget to user
    
    Returns: corrected budget dict with verified math
    """
    print(f"[MATH_ENFORCEMENT] Starting mathematical validation...")
    
    # 1. Calculate total cost from components (NEVER trust AI-generated total)
    cost_components = [
        budget_dict.get("seeds", 0),
        budget_dict.get("fertilizer", 0),
        budget_dict.get("pesticides", 0),
        budget_dict.get("irrigation", 0),
        budget_dict.get("labor", 0),
        budget_dict.get("machinery", 0),
        budget_dict.get("harvesting", 0),
        budget_dict.get("transport", 0),
        budget_dict.get("electricity_diesel", 0),
        budget_dict.get("miscellaneous", 0),
        budget_dict.get("interest", 0),
    ]
    
    calculated_total_cost = sum(cost_components)
    
    if budget_dict.get("total_cost", 0) != calculated_total_cost:
        print(f"[MATH_ENFORCEMENT] ⚠️  Total cost mismatch!")
        print(f"[MATH_ENFORCEMENT]    AI provided: ₹{budget_dict.get('total_cost', 0):,}")
        print(f"[MATH_ENFORCEMENT]    Calculated:  ₹{calculated_total_cost:,}")
        print(f"[MATH_ENFORCEMENT]    Correcting to calculated value")
        budget_dict["total_cost"] = calculated_total_cost
    
    # 2. Calculate revenue (Yield × Price)
    calculated_revenue = budget_dict.get("expected_yield", 0) * budget_dict.get("expected_price", 0)
    
    if budget_dict.get("expected_revenue", 0) != calculated_revenue:
        print(f"[MATH_ENFORCEMENT] ⚠️  Revenue mismatch!")
        print(f"[MATH_ENFORCEMENT]    AI provided: ₹{budget_dict.get('expected_revenue', 0):,}")
        print(f"[MATH_ENFORCEMENT]    Calculated:  ₹{calculated_revenue:,}")
        print(f"[MATH_ENFORCEMENT]    Formula: {budget_dict.get('expected_yield', 0)} × ₹{budget_dict.get('expected_price', 0)} = ₹{calculated_revenue:,}")
        budget_dict["expected_revenue"] = calculated_revenue
    
    # 3. Calculate profit (Revenue - Total Cost)
    calculated_profit = calculated_revenue - calculated_total_cost
    
    if budget_dict.get("expected_profit", 0) != calculated_profit:
        print(f"[MATH_ENFORCEMENT] ⚠️  Profit mismatch!")
        print(f"[MATH_ENFORCEMENT]    AI provided: ₹{budget_dict.get('expected_profit', 0):,}")
        print(f"[MATH_ENFORCEMENT]    Calculated:  ₹{calculated_profit:,}")
        print(f"[MATH_ENFORCEMENT]    Formula: ₹{calculated_revenue:,} - ₹{calculated_total_cost:,} = ₹{calculated_profit:,}")
        budget_dict["expected_profit"] = calculated_profit
    
    # 4. Calculate ROI ((Profit / Total Cost) × 100)
    if calculated_total_cost > 0:
        calculated_roi = (calculated_profit / calculated_total_cost) * 100
        budget_dict["roi"] = calculated_roi
        print(f"[MATH_ENFORCEMENT] ✅ ROI: {calculated_roi:.1f}%")
    else:
        budget_dict["roi"] = 0
        print(f"[MATH_ENFORCEMENT] ⚠️  Total cost is zero, cannot calculate ROI")
    
    # 5. Final verification
    print(f"[MATH_ENFORCEMENT] ===== FINAL VERIFIED NUMBERS =====")
    print(f"[MATH_ENFORCEMENT] Total Cost:    ₹{calculated_total_cost:,}")
    print(f"[MATH_ENFORCEMENT] Total Revenue:  ₹{calculated_revenue:,}")
    print(f"[MATH_ENFORCEMENT] Total Profit:   ₹{calculated_profit:,}")
    print(f"[MATH_ENFORCEMENT] ROI:            {budget_dict.get('roi', 0):.1f}%")
    print(f"[MATH_ENFORCEMENT] ===================================")
    
    return budget_dict


def sanity_check_budget(budget_dict):
    """
    Final sanity check before returning budget to user
    Triggers recalculation if numbers are unrealistic
    
    Returns: (is_sane, issues_list)
    """
    issues = []
    
    # Check 1: ROI > 300% for traditional crops
    roi = budget_dict.get("roi", 0)
    crop_name = budget_dict.get("crop", "")
    category = get_crop_category(crop_name)
    
    if category in ["pulse", "cereal", "oilseed"] and roi > 300:
        issues.append(f"ROI too high ({roi:.0f}%) for {category} crop")
    
    # Check 2: Profit per acre exceeds realistic benchmark
    land_size = budget_dict.get("land_size", 1)
    if land_size > 0:
        profit_per_acre = budget_dict.get("expected_profit", 0) / land_size
        
        # Realistic profit per acre benchmarks
        max_profit_per_acre = {
            "pulse": 30000,
            "cereal": 25000,
            "oilseed": 35000,
            "cash_crop": 60000,
            "vegetable": 80000,
            "fruit": 100000,
        }
        
        max_profit = max_profit_per_acre.get(category, 50000)
        if profit_per_acre > max_profit * 2:  # 2x buffer
            issues.append(f"Profit per acre (₹{profit_per_acre:,.0f}) exceeds realistic benchmark (₹{max_profit:,})")
    
    # Check 3: Yield per acre unrealistic
    if land_size > 0:
        yield_per_acre = budget_dict.get("expected_yield", 0) / land_size
        yield_range = get_yield_range(crop_name)
        
        if yield_range:
            max_yield = yield_range["max"]
            if yield_per_acre > max_yield * 1.5:
                issues.append(f"Yield per acre ({yield_per_acre:.0f}) exceeds realistic maximum ({max_yield})")
    
    # Check 4: Total cost seems wrong
    if land_size > 0:
        cost_per_acre = budget_dict.get("total_cost", 0) / land_size
        is_valid_cost, _, cost_msg = validate_cost(crop_name, cost_per_acre)
        
        if not is_valid_cost:
            issues.append(f"Cost per acre issue: {cost_msg}")
    
    is_sane = len(issues) == 0
    
    if not is_sane:
        print(f"[SANITY_CHECK] ⚠️  FAILED - {len(issues)} issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"[SANITY_CHECK]    {i}. {issue}")
    else:
        print(f"[SANITY_CHECK] ✅ PASSED - All checks passed")
    
    return (is_sane, issues)
