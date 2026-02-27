# Behavior Correction & System Refinement Plan

## Date: February 27, 2026
## Status: IN PROGRESS

---

## ISSUES IDENTIFIED

### 1. Language Consistency ❌
- English responses contain Hindi
- Language state not respected
- Mixed language in budget responses

### 2. Data Integrity ❌
- ROI calculations incorrect
- Placeholder text visible ("🔍 Research", "AI Research")
- Fake transparency (model names shown)
- Math errors in budget

### 3. Agent Isolation ❌
- Budget agent auto-injects weather
- Budget agent auto-injects reminders
- Unsolicited advisory content

### 4. Market Agent ❌
- Asks follow-up questions instead of showing price
- Doesn't directly return mandi price
- Generic responses

### 5. UX Issues ❌
- Repetitive "What would you like to do next?"
- Double responses
- Too many emojis
- Help button broken

### 6. Reminder Logic ❌
- Auto-sets reminders without asking
- No user confirmation

### 7. Fake Transparency ❌
- Shows "Claude Sonnet 4"
- Shows "Model: Claude Sonnet 4"
- Internal system notes visible

---

## FIXES TO IMPLEMENT

### Priority 1: CRITICAL (Fix Now)

1. ✅ Remove auto-weather injection from budget
2. ✅ Remove auto-reminder injection from budget
3. ✅ Remove model name display
4. ✅ Remove "AI Research" labels
5. ✅ Fix ROI calculation
6. ✅ Remove repetitive prompts
7. ✅ Fix market agent to show price directly

### Priority 2: HIGH

8. ✅ Validate all math in budget
9. ✅ Remove double responses
10. ✅ Limit emoji usage
11. ✅ Fix help button
12. ✅ Add reminder confirmation

### Priority 3: MEDIUM

13. ✅ Improve response structure
14. ✅ Professional tone
15. ✅ Clean data sources

---

## IMPLEMENTATION PLAN

### Step 1: Remove Auto-Injections
- Find weather injection code
- Find reminder injection code
- Comment out or remove

### Step 2: Clean Budget Response
- Remove model name
- Remove "AI Research" labels
- Remove "Data Sources" section
- Keep only essential info

### Step 3: Fix Market Agent
- Remove follow-up questions
- Show price directly
- Add mandi location
- Add trend

### Step 4: Fix Math
- Recalculate ROI
- Validate revenue = yield × price
- Validate profit = revenue - cost

### Step 5: UX Cleanup
- Remove repetitive prompts
- Fix double responses
- Limit emojis
- Professional tone

---

## TESTING CHECKLIST

After fixes:
- [ ] Budget response has NO weather
- [ ] Budget response has NO reminders
- [ ] Budget response has NO model name
- [ ] Market agent shows price directly
- [ ] ROI calculation correct
- [ ] No repetitive prompts
- [ ] No double responses
- [ ] Professional tone
- [ ] Limited emojis

---

**Status:** Ready to Implement
**Next:** Start with Priority 1 fixes
