# Farmer Count Query Fix

## Issue Description

**Problem**: When Vinay asked "How many farmers are in my village", the system responded with:
> "I couldn't find any OTHER farmers matching your criteria in the knowledge graph."

This was confusing because:
1. There are 15 farmers in Kolhapur (including Vinay)
2. The response said "OTHER farmers" which was misleading
3. The system didn't distinguish between "total count" vs "other farmers" queries

## Root Cause

The issue was in the knowledge graph query logic:

1. **AI Prompt Too Restrictive**: The prompt asked "Is this asking about OTHER FARMERS" which biased the system to always exclude the user
2. **No Query Type Detection**: The system didn't distinguish between:
   - "How many farmers are in my village" (wants TOTAL count including user)
   - "Who else grows sugarcane" (wants OTHER farmers excluding user)
3. **Confusing Response**: Always said "OTHER farmers" even for total count queries

## Solution Implemented

### 1. Enhanced Query Type Detection

Added AI-based detection to distinguish query types:

```python
count_prompt = f"""Is this asking for TOTAL/ALL farmers (including the user) or just OTHER farmers (excluding the user)? Reply ONLY "total" or "other".

Message: "{user_message}"

Examples of "total": "how many farmers", "total farmers", "कितने किसान हैं", "all farmers in my village"
Examples of "other": "who else grows", "other farmers", "और कौन उगाता है", "show me other farmers"

Reply: """
```

### 2. Updated `get_village_farmers()` Function

Added parameters to control behavior:

```python
def get_village_farmers(village_name, crop=None, exclude_user_id=None, include_self=False):
    """
    Get farmers from a village
    
    Args:
        village_name: Name of the village
        crop: Optional crop filter
        exclude_user_id: User ID to exclude (for "other farmers" queries)
        include_self: If True, include the current user in results
    
    Returns:
        farmers: List of farmer objects
        current_user: Current user object (if found)
    """
```

### 3. Enhanced `format_farmers_list()` Function

Added support for different query types:

```python
def format_farmers_list(farmers, language='english', current_user=None, query_type='other'):
    """
    Format farmers list for display
    
    Args:
        farmers: List of farmer objects
        language: 'english' or 'hindi'
        current_user: Current user object (if available)
        query_type: 'all' (total count) or 'other' (excluding user)
    """
```

### 4. Updated Response Format

**For "total count" queries:**
```
🌾 *Total Farmers in Village: 15*

*You (Vinay)*
📏 Land: 50 acres
🌾 Crops: Wheat, Sugarcane, Soyabean, Rice, Tur Daal

*Other Farmers (14):*

*1. Rajesh Patil*
...
```

**For "other farmers" queries:**
```
🌾 *Found 14 Other Farmer(s)*

*1. Rajesh Patil*
...
```

## Files Modified

1. **src/lambda/knowledge_graph_helper.py**
   - Updated `load_knowledge_graph_data()` to support multiple paths
   - Enhanced `get_village_farmers()` with `include_self` parameter
   - Enhanced `format_farmers_list()` with `query_type` parameter

2. **src/lambda/lambda_whatsapp_kisaanmitra.py**
   - Updated knowledge graph query detection
   - Added query type classification (total vs other)
   - Updated function calls to pass correct parameters

## Test Results

Created comprehensive test: `tests/test_farmer_count_fix.py`

**Test 1: Total Count Query**
- ✅ Shows correct total count (15 farmers)
- ✅ Shows user's own profile first
- ✅ Shows other farmers (14) below

**Test 2: Other Farmers Query**
- ✅ Shows only other farmers (14)
- ✅ Excludes the user from the list
- ✅ Correct heading "Other Farmer(s)"

**Test 3: Hindi Language**
- ✅ Correct Hindi response
- ✅ Shows "गांव में कुल किसान: 15"
- ✅ All formatting correct

## Deployment

### Step 1: Test Locally
```bash
python tests/test_farmer_count_fix.py
```

### Step 2: Deploy to Lambda
```bash
cd src/lambda
./deploy_whatsapp.sh
```

### Step 3: Verify in Production
Send these test messages via WhatsApp:
1. "How many farmers are in my village" → Should show 15 total
2. "Who else grows sugarcane" → Should show 14 other farmers
3. "कितने किसान हैं मेरे गांव में" → Should show Hindi response with 15 total

## Expected Behavior After Fix

### Query: "How many farmers are in my village"
**Response:**
```
🌾 *Total Farmers in Village: 15*

*You (Vinay)*
📏 Land: 50 acres
🌾 Crops: Wheat, Sugarcane, Soyabean, Rice, Tur Daal

*Other Farmers (14):*

*1. Rajesh Patil*
📍 Village: Kolhapur
🌾 Crops: Sugarcane
📏 Land: 15 acres

[... 13 more farmers ...]

💡 Type 'back' to go back, 'home' for main menu
```

### Query: "Who else grows sugarcane"
**Response:**
```
🌾 *Found 14 Other Farmer(s)*

*1. Rajesh Patil*
📍 Village: Kolhapur
🌾 Crops: Sugarcane
📏 Land: 15 acres

[... 13 more farmers ...]

💡 Type 'back' to go back, 'home' for main menu
```

## Impact

- ✅ Fixes confusing "OTHER farmers" message
- ✅ Correctly handles total count queries
- ✅ Shows user's own profile when asking for total
- ✅ Maintains backward compatibility for "other farmers" queries
- ✅ Works in both English and Hindi
- ✅ No breaking changes to existing functionality

## Data Verification

**Kolhapur Village:**
- Total farmers: 15
- Vinay's profile: ✅ Present
  - Phone: +919000000001
  - Land: 50 acres
  - Crops: Wheat, Sugarcane, Soyabean, Rice, Tur Daal
- Other farmers: 14 (Rajesh Patil, Suresh Jadhav, Vijay Shinde, etc.)

## Status

- ✅ Issue identified
- ✅ Root cause analyzed
- ✅ Solution implemented
- ✅ Tests created and passing
- ✅ Documentation complete
- ⏳ Ready for deployment

---

**Next Step**: Deploy to Lambda and verify with real WhatsApp messages.
