"""
Multi-Crop Comparison & Planning
"""

def compare_crops(budgets):
    """Compare multiple crop budgets"""
    if not budgets or len(budgets) < 2:
        return None
    
    comparison = {
        'crops': [],
        'best_roi': None,
        'lowest_risk': None,
        'highest_profit': None
    }
    
    best_roi = -999
    highest_profit = -999999
    
    for budget in budgets:
        crop_data = {
            'name': budget['crop'],
            'cost': budget['total_cost'],
            'revenue': budget['expected_revenue'],
            'profit': budget['expected_profit'],
            'roi': int((budget['expected_profit'] / budget['total_cost'] * 100)) if budget['total_cost'] > 0 else 0,
            'feasibility': budget.get('feasibility', 'UNKNOWN')
        }
        
        comparison['crops'].append(crop_data)
        
        if crop_data['roi'] > best_roi:
            best_roi = crop_data['roi']
            comparison['best_roi'] = crop_data['name']
        
        if crop_data['profit'] > highest_profit:
            highest_profit = crop_data['profit']
            comparison['highest_profit'] = crop_data['name']
    
    return comparison

def format_comparison_table(comparison):
    """Format comparison as text table"""
    if not comparison or len(comparison['crops']) < 2:
        return ""
    
    message = "\n\n📊 *फसल तुलना*\n\n"
    
    # Header
    message += "```\n"
    message += f"{'फसल':<12} {'लागत':<10} {'लाभ':<10} {'ROI':<8}\n"
    message += "-" * 42 + "\n"
    
    # Rows
    for crop in comparison['crops']:
        name = crop['name'][:10]
        cost = f"₹{crop['cost']//1000}k"
        profit = f"₹{crop['profit']//1000}k"
        roi = f"{crop['roi']}%"
        
        message += f"{name:<12} {cost:<10} {profit:<10} {roi:<8}\n"
    
    message += "```\n"
    
    # Recommendations
    message += "\n*💡 सिफारिश*:\n"
    if comparison['best_roi']:
        message += f"• सबसे अच्छा ROI: {comparison['best_roi']}\n"
    if comparison['highest_profit']:
        message += f"• सबसे अधिक लाभ: {comparison['highest_profit']}\n"
    
    return message

def suggest_crop_rotation(crops):
    """Suggest crop rotation"""
    rotations = {
        ('rice', 'wheat'): "धान → गेहूं → मूंग (उत्तम चक्र)",
        ('tomato', 'onion'): "टमाटर → प्याज → गेहूं (सब्जी चक्र)",
        ('cotton', 'wheat'): "कपास → गेहूं → चना (नकदी चक्र)",
        ('sugarcane', 'wheat'): "गन्ना → गेहूं → सोयाबीन (लंबा चक्र)"
    }
    
    crop_tuple = tuple(sorted([c.lower() for c in crops[:2]]))
    
    for key, rotation in rotations.items():
        if all(c in crop_tuple for c in key):
            return f"\n\n🔄 *फसल चक्र सुझाव*: {rotation}"
    
    return ""
