# Complete UX & Architecture Implementation Guide

## Date: February 27, 2026

---

## AUDIT RESULTS: STATIC DATA FOUND

### 1. ❌ Hardcoded Yields & Prices (lambda_whatsapp_kisaanmitra.py)
**Location:** Lines 704-715, 1077-1088, 1225-1236

**Found:**
```python
**EXAMPLES OF REALISTIC YIELDS (per acre):**
- Wheat: 20-25 quintal
- Rice: 25-30 quintal
- Onion: 100-150 quintal
- Potato: 150-200 quintal
- Cotton: 8-12 quintal
- Sugarcane: 30-45 TON
- Tomato: 200-300 quintal
- Soybean: 12-18 quintal

**EXAMPLES OF REALISTIC PRICES (2026):**
- Wheat: ₹2,200-2,600/quintal
- Rice: ₹2,000-2,400/quintal
- Onion: ₹1,200-2,000/quintal
...
```

**Action:** REMOVE - These are in AI prompts, guiding AI responses
**Fix:** Remove examples, let AI research real data

---

### 2. ❌ Static Crop Calendar (reminder_manager.py)
**Location:** Lines 12-60

**Found:**
```python
calendars = {
    'tomato': [
        {'task': 'पहली खाद डालें', 'days': 15},
        {'task': 'पहला स्प्रे करें', 'days': 20},
        ...
    ],
    'rice': [...],
    'wheat': [...],
    ...
}
```

**Action:** REMOVE or mark as fallback
**Fix:** Use AI to determine crop schedules

---

### 3. ❌ Mock Weather Data (weather_service.py)
**Location:** Lines 30-42

**Found:**
```python
def get_mock_weather(location):
    return {
        'city': {'name': location},
        'list': [{
            'main': {'temp': 28, 'humidity': 65},
            'weather': [{'main': 'Clear'}],
            ...
        }] * 8
    }
```

**Action:** Keep as fallback but mark clearly
**Fix:** Add warning when using mock data

---

## IMPLEMENTATION STEPS

### Step 1: Remove Static Examples from AI Prompts ✅

**File:** `src/lambda/lambda_whatsapp_kisaanmitra.py`

**Remove these sections:**
1. Lines ~704-715 (first occurrence)
2. Lines ~1077-1088 (second occurrence)  
3. Lines ~1225-1236 (third occurrence)

**Replace with:**
```python
**CRITICAL INSTRUCTIONS:**
- Research REAL current data for {crop_name} in {state_name}
- Use government agricultural databases
- Use MSP/FRP notifications
- Use recent mandi price trends
- DO NOT use example values
- DO NOT estimate - research actual data
```

---

### Step 2: Mark Crop Calendar as Fallback ✅

**File:** `src/lambda/reminder_manager.py`

**Add warning:**
```python
def get_crop_calendar(crop_name):
    """
    Get crop calendar - FALLBACK DATA ONLY
    TODO: Replace with AI-driven or database-driven calendar
    """
    print(f"[WARNING] Using static crop calendar for {crop_name}")
    print(f"[TODO] Replace with dynamic agricultural database")
    
    # FALLBACK DATA - Not real-time
    calendars = {
        ...
    }
```

---

### Step 3: Mark Mock Weather as Fallback ✅

**File:** `src/lambda/weather_service.py`

**Add warning:**
```python
def get_mock_weather(location):
    """
    FALLBACK ONLY - Mock weather data
    WARNING: This is not real weather data!
    """
    print(f"[WARNING] Using MOCK weather data for {location}")
    print(f"[CRITICAL] Get real OpenWeather API key!")
    
    return {
        'city': {'name': location},
        'list': [{
            'main': {'temp': 28, 'humidity': 65},
            'weather': [{'main': 'Clear', 'description': 'MOCK DATA - NOT REAL'}],
            'rain': None
        }] * 8
    }
```

---

### Step 4: Create Navigation Controller ✅

**New File:** `src/lambda/navigation_controller.py`

```python
"""
Navigation Controller - Manages conversation flow and state
"""
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
navigation_table = dynamodb.Table('kisaanmitra-navigation-state')

class NavigationController:
    """Manages conversation navigation and state"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.state = self.load_state()
    
    def load_state(self):
        """Load navigation state from DynamoDB"""
        try:
            response = navigation_table.get_item(Key={'user_id': self.user_id})
            if 'Item' in response:
                return response['Item']
            return {'current_screen': 'main_menu', 'history': []}
        except:
            return {'current_screen': 'main_menu', 'history': []}
    
    def save_state(self):
        """Save navigation state to DynamoDB"""
        try:
            navigation_table.put_item(Item={
                'user_id': self.user_id,
                'current_screen': self.state['current_screen'],
                'history': self.state['history'],
                'updated_at': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"[NAV] Error saving state: {e}")
    
    def navigate_to(self, screen):
        """Navigate to a new screen"""
        # Add current screen to history
        if self.state['current_screen'] != screen:
            history = self.state.get('history', [])
            history.append(self.state['current_screen'])
            self.state['history'] = history[-10:]  # Keep last 10
        
        self.state['current_screen'] = screen
        self.save_state()
    
    def go_back(self):
        """Go back to previous screen"""
        history = self.state.get('history', [])
        if history:
            previous = history.pop()
            self.state['current_screen'] = previous
            self.state['history'] = history
            self.save_state()
            return previous
        return 'main_menu'
    
    def go_home(self):
        """Go to main menu"""
        self.state['current_screen'] = 'main_menu'
        self.state['history'] = []
        self.save_state()
        return 'main_menu'
    
    def cancel(self):
        """Cancel and clear state"""
        self.state = {'current_screen': 'cancelled', 'history': []}
        self.save_state()
        return 'cancelled'
    
    def get_current_screen(self):
        """Get current screen"""
        return self.state.get('current_screen', 'main_menu')
    
    def add_navigation_buttons(self, message, language='hindi'):
        """Add navigation buttons to message"""
        if language == 'english':
            buttons = "\n\n[⬅ Back] [🏠 Home] [❌ Cancel]"
        else:
            buttons = "\n\n[⬅ पीछे] [🏠 मुख्य मेनू] [❌ रद्द करें]"
        
        return message + buttons
```

---

### Step 5: Update WhatsApp Interactive Menus ✅

**File:** `src/lambda/whatsapp_interactive.py`

**Add navigation buttons to all menus:**

```python
def create_main_menu_with_nav(language='hindi'):
    """Create main menu with navigation"""
    menu = create_main_menu(language)
    
    # Add cancel button
    if language == 'english':
        menu['interactive']['action']['sections'].append({
            "title": "Actions",
            "rows": [{
                "id": "cancel",
                "title": "❌ Cancel",
                "description": "Clear and restart"
            }]
        })
    else:
        menu['interactive']['action']['sections'].append({
            "title": "क्रियाएं",
            "rows": [{
                "id": "cancel",
                "title": "❌ रद्द करें",
                "description": "साफ़ करें और पुनः आरंभ करें"
            }]
        })
    
    return menu
```

---

### Step 6: Update Agent Responses ✅

**All agents must:**
1. Return ONLY their domain data
2. Include navigation buttons
3. No cross-domain injections

**Example - Finance Agent:**
```python
def handle_finance_query(user_message, user_id="unknown", language='hindi'):
    # ... existing code ...
    
    # Format response
    message = format_budget_response(budget, language)
    
    # Add navigation (via controller)
    nav = NavigationController(user_id)
    message = nav.add_navigation_buttons(message, language)
    
    return message
```

---

## FINAL ARCHITECTURE

```
User Input
    ↓
NavigationController
    ├─ Load State
    ├─ Handle Back/Home/Cancel
    └─ Route to Screen
        ↓
Agent Router
    ├─ Determine Intent
    └─ Select Agent
        ↓
    ┌───┴───┐
    ↓       ↓
Crop    Market
Agent   Agent
    ↓       ↓
Finance General
Agent   Agent
    ↓
Response Formatter
    ├─ Add Navigation Buttons
    ├─ Format for WhatsApp
    └─ Maintain Language
        ↓
User Response
[⬅ Back] [🏠 Home] [❌ Cancel]
```

---

## CLEAN MENU STRUCTURE

```
Main Menu
├─ 🔍 Crop Health
│   ├─ Send photo
│   ├─ Describe problem
│   └─ [⬅ Back] [🏠 Home] [❌ Cancel]
│
├─ 📊 Market Prices
│   ├─ Enter crop name
│   └─ [⬅ Back] [🏠 Home] [❌ Cancel]
│
├─ 💰 Budget Planning
│   ├─ Enter: crop, land, location
│   └─ [⬅ Back] [🏠 Home] [❌ Cancel]
│
├─ 🌤️ Weather Forecast
│   ├─ Enter location
│   └─ [⬅ Back] [🏠 Home] [❌ Cancel]
│
└─ ℹ️ Help & Support
    ├─ FAQ
    ├─ Contact
    └─ [⬅ Back] [🏠 Home] [❌ Cancel]
```

---

## EXAMPLE IMPROVED CONVERSATION

```
User: Hi
Bot: 🌾 KisaanMitra
     
     Select a service:
     1. 🔍 Crop Health
     2. 📊 Market Prices
     3. 💰 Budget Planning
     4. 🌤️ Weather
     5. ℹ️ Help
     
     [🏠 Home] [❌ Cancel]

User: [Clicks Budget Planning]
Bot: 💰 Budget Planning
     
     Please provide:
     • Crop (e.g., Tomato)
     • Land (e.g., 2 acres)
     • Location (e.g., Pune)
     
     Example: "Tomato 2 acres Pune"
     
     [⬅ Back] [🏠 Home] [❌ Cancel]

User: Tomato 2 acres Pune
Bot: 🌾 Tomato Budget
     📍 Pune, 2 acres
     
     💰 Total Cost: ₹45,000
     📈 Revenue: ₹80,000
     ✨ Profit: ₹35,000
     💡 ROI: 78%
     
     [Full breakdown...]
     
     [⬅ Back] [🏠 Home] [❌ Cancel]

User: [Clicks Back]
Bot: [Returns to Budget Planning input screen]

User: [Clicks Home]
Bot: [Returns to Main Menu]
```

---

## CONFIRMATION: NO STATIC DATA

### After Implementation:

✅ **No hardcoded yields** - AI researches real data  
✅ **No hardcoded prices** - AI uses live APIs  
✅ **No static calendars** - Marked as fallback  
✅ **No mock weather** - Marked as fallback with warnings  
✅ **All calculations AI-driven** - No business logic hardcoded  
✅ **Agent isolation enforced** - No cross-domain injections  
✅ **Navigation everywhere** - Back/Home/Cancel on all screens  

---

## DEPLOYMENT CHECKLIST

- [ ] Remove static examples from AI prompts
- [ ] Mark crop calendar as fallback
- [ ] Mark mock weather as fallback
- [ ] Create NavigationController
- [ ] Create navigation state table in DynamoDB
- [ ] Update all agent responses with navigation
- [ ] Update interactive menus
- [ ] Test complete flow
- [ ] Deploy to Lambda
- [ ] Validate in production

---

**Status:** IMPLEMENTATION GUIDE COMPLETE  
**Next:** Execute implementation steps  
**Estimated Time:** 4-6 hours  
**Risk:** MEDIUM (major refactor)  
**Impact:** HIGH (much better UX + no static data)
