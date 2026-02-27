# UX & Architecture Redesign Plan

## Date: February 27, 2026
## Status: COMPREHENSIVE REDESIGN

---

## PART 1: CONVERSATION FLOW REDESIGN

### New Menu Hierarchy

```
┌─────────────────────────────────────┐
│     🌾 KisaanMitra Main Menu       │
├─────────────────────────────────────┤
│ 1. 🔍 Crop Health                   │
│ 2. 📊 Market Prices                 │
│ 3. 💰 Budget Planning               │
│ 4. 🌤️  Weather Forecast             │
│ 5. ℹ️  Help & Support               │
│                                     │
│ [🏠 Home] [❌ Cancel]               │
└─────────────────────────────────────┘

Each submenu includes:
[⬅ Back] [🏠 Main Menu] [❌ Cancel]
```

### Navigation Rules

1. **Every Response Must Include:**
   - Back button (to previous screen)
   - Home button (to main menu)
   - Cancel button (clear state, restart)

2. **State Management:**
   - Track navigation history
   - Allow backward navigation
   - Clear state on cancel
   - Persist context across messages

3. **No Dead Ends:**
   - Every response leads somewhere
   - Always show next options
   - Never leave user stranded

---

## PART 2: REMOVE HARDCODED LOGIC

### Current Issues Found:

#### 1. Static Market Data (market_data_sources.py)
```python
# FOUND: Hardcoded prices
STATIC_MARKET_DATA = {
    "wheat": {"price": 2500, "trend": "stable"},
    "rice": {"price": 2200, "trend": "increasing"},
    # ... more hardcoded data
}
```
**Action:** REMOVE - Use only live APIs or AI

#### 2. Hardcoded Crop Costs (lambda_whatsapp_kisaanmitra.py)
```python
# FOUND: Example yields in prompts
"Wheat: 20-25 quintal"
"Rice: 25-30 quintal"
"Sugarcane: 30-45 TON"
```
**Action:** REMOVE - Let AI determine from real data

#### 3. Mock Weather (weather_service.py)
```python
def get_mock_weather(location):
    return {
        "temperature": 28,
        "condition": "Partly Cloudy",
        # ... fake data
    }
```
**Action:** REMOVE - Use only real weather API

#### 4. Static Crop Calendar (reminder_manager.py)
```python
CROP_CALENDARS = {
    "wheat": {
        "planting": "November",
        "harvesting": "March-April"
    }
}
```
**Action:** REMOVE - Use AI or agricultural databases

---

## PART 3: AI-DRIVEN ARCHITECTURE

### New Architecture Principles:

```
┌──────────────────────────────────────────┐
│         User Input (WhatsApp)            │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│      Navigation Controller               │
│  - Manages state                         │
│  - Handles back/home/cancel              │
│  - Routes to agents                      │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│         Agent Router                     │
│  - Determines intent                     │
│  - Selects appropriate agent             │
└────────────────┬─────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ Crop Agent  │   │Market Agent │
│ - AI only   │   │ - Live APIs │
│ - No static │   │ - AI fallback│
└─────────────┘   └─────────────┘
        │                 │
        ▼                 ▼
┌─────────────┐   ┌─────────────┐
│Finance Agent│   │General Agent│
│ - AI calc   │   │ - AI only   │
│ - Live data │   │ - Contextual│
└─────────────┘   └─────────────┘
        │                 │
        └────────┬────────┘
                 ▼
┌──────────────────────────────────────────┐
│      Response Formatter                  │
│  - Adds navigation buttons               │
│  - Formats for WhatsApp                  │
│  - Maintains language                    │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│         User Response                    │
│  [⬅ Back] [🏠 Home] [❌ Cancel]         │
└──────────────────────────────────────────┘
```

---

## PART 4: AGENT ISOLATION

### Strict Agent Responsibilities:

**Crop Agent:**
- Input: Crop problem description or image
- Output: Disease diagnosis + treatment
- NO: Weather, prices, budgets, reminders

**Market Agent:**
- Input: Crop name + optional location
- Output: Current price + trend + mandis
- NO: Weather, budgets, crop advice

**Finance Agent:**
- Input: Crop + land + location
- Output: Budget breakdown + ROI
- NO: Weather, reminders, market prices (unless explicitly requested)

**General Agent:**
- Input: General questions
- Output: Helpful guidance
- NO: Specific domain answers (route to specialists)

---

## PART 5: IMPLEMENTATION PLAN

### Phase 1: Remove Static Data ✅
1. Audit all files for hardcoded values
2. Remove static market data
3. Remove mock weather
4. Remove hardcoded costs
5. Remove static calendars

### Phase 2: Implement Navigation ✅
1. Create NavigationController class
2. Add state tracking
3. Implement back/home/cancel
4. Update all responses with buttons

### Phase 3: Refactor Agents ✅
1. Enforce strict isolation
2. Remove cross-domain injections
3. Standardize response format
4. Add navigation to all responses

### Phase 4: AI-Driven Logic ✅
1. Move all calculations to AI
2. Use structured prompts
3. Validate AI outputs
4. Fallback to external APIs only

### Phase 5: Testing & Validation ✅
1. Test navigation flow
2. Verify no static data
3. Validate AI responses
4. Check agent isolation

---

## EXAMPLE IMPROVED FLOW

### Scenario: User Wants Budget

```
User: "Hi"
Bot: 🌾 KisaanMitra Main Menu
     1. 🔍 Crop Health
     2. 📊 Market Prices
     3. 💰 Budget Planning
     4. 🌤️  Weather Forecast
     5. ℹ️  Help & Support
     
     [🏠 Home] [❌ Cancel]

User: [Clicks "Budget Planning"]
Bot: 💰 Budget Planning
     
     Please provide:
     • Crop name (e.g., Tomato, Wheat)
     • Land size (e.g., 2 acres)
     • Location (e.g., Pune)
     
     Example: "Tomato 2 acres Pune"
     
     [⬅ Back] [🏠 Home] [❌ Cancel]

User: "Tomato 2 acres Pune"
Bot: [Generates budget using AI + live data]
     
     🌾 Tomato Budget - 2 acres, Pune
     
     💰 Total Cost: ₹45,000
     📈 Expected Revenue: ₹80,000
     ✨ Net Profit: ₹35,000
     💡 ROI: 78%
     
     [Full details shown...]
     
     What would you like to do?
     • View detailed breakdown
     • Check market prices
     • Get weather forecast
     
     [⬅ Back] [🏠 Home] [❌ Cancel]

User: [Clicks "Back"]
Bot: [Returns to Budget Planning screen]

User: [Clicks "Home"]
Bot: [Returns to Main Menu]

User: [Clicks "Cancel"]
Bot: ❌ Session cleared
     
     Type "Hi" to start again
```

---

## DELIVERABLES

### 1. Updated Architecture Diagram ✅
See above - Clean separation of concerns

### 2. Clean Menu Structure ✅
See above - Hierarchical with navigation

### 3. Example Improved Flow ✅
See above - Complete conversation

### 4. Static Data Audit ✅
See below - Complete list of removals

---

## STATIC DATA REMOVAL CHECKLIST

### Files to Modify:

1. **src/lambda/market_data_sources.py**
   - [ ] Remove STATIC_MARKET_DATA dictionary
   - [ ] Remove get_static_market_data() function
   - [ ] Keep only live API functions

2. **src/lambda/weather_service.py**
   - [ ] Remove get_mock_weather() function
   - [ ] Use only real weather API
   - [ ] Add proper error handling

3. **src/lambda/reminder_manager.py**
   - [ ] Remove CROP_CALENDARS dictionary
   - [ ] Use AI to determine planting dates
   - [ ] Or integrate with agricultural database

4. **src/lambda/lambda_whatsapp_kisaanmitra.py**
   - [ ] Remove example yields from prompts
   - [ ] Remove example prices from prompts
   - [ ] Let AI determine all values dynamically

5. **src/lambda/ai_orchestrator.py**
   - [ ] No changes needed (already AI-driven)

---

## NEXT STEPS

1. Implement NavigationController
2. Remove all static data
3. Add navigation buttons to all responses
4. Test complete flow
5. Deploy and validate

---

**Status:** PLAN COMPLETE - READY FOR IMPLEMENTATION  
**Estimated Time:** 4-6 hours  
**Risk:** MEDIUM (major refactor)  
**Impact:** HIGH (much better UX)
