# KisaanMitra Process Flow - PowerPoint Design Guide

## Slide Specifications
- **Format**: 16:9 Landscape
- **Layout**: Horizontal left-to-right flow
- **Style**: Clean, professional, hackathon-ready
- **Colors**: AWS orange (#FF9900), Blue (#232F3E), White, Light gray backgrounds

---

## Process Flow (8 Steps)

### Step 1: Farmer (User Input)
**Icon**: 👨‍🌾 or user icon  
**Label**: "Farmer"  
**Sublabel**: "WhatsApp Query"  
**Color**: Blue (#232F3E)  
**Shape**: Rounded rectangle (150px × 100px)

**Arrow** → Orange, 10px thick

---

### Step 2: Input Layer
**Icon**: 📱 WhatsApp logo  
**Label**: "WhatsApp API"  
**Sublabel**: "Message Received"  
**Color**: Green (#25D366)  
**Shape**: Rounded rectangle (150px × 100px)

**Arrow** → Orange, 10px thick

---

### Step 3: Processing Layer
**Icon**: ⚡ Lambda icon  
**Label**: "Lambda"  
**Sublabel**: "Orchestrator"  
**Color**: AWS Orange (#FF9900)  
**Shape**: Rounded rectangle (150px × 100px)

**Arrow** → Orange, 10px thick

---

### Step 4: GenAI Engine
**Icon**: 🤖 AI/Brain icon  
**Label**: "Amazon Bedrock"  
**Sublabel**: "Nova Pro AI"  
**Color**: Purple (#8B5CF6)  
**Shape**: Rounded rectangle (150px × 100px)

**Arrows** → Split into 2 arrows (one to DynamoDB, one to S3)

---

### Step 5: AWS Infrastructure (Grouped)
**Container**: Light gray box (#F3F4F6) with dashed border  
**Label**: "AWS Services"

#### 5a. DynamoDB
**Icon**: 🗄️ Database icon  
**Label**: "DynamoDB"  
**Sublabel**: "User Profiles"  
**Color**: Blue (#3B82F6)  
**Shape**: Rounded rectangle (120px × 80px)

#### 5b. S3
**Icon**: 📦 Storage icon  
**Label**: "S3"  
**Sublabel**: "Images"  
**Color**: Green (#10B981)  
**Shape**: Rounded rectangle (120px × 80px)

**Arrows** → Both converge to next step

---

### Step 6: Output Layer
**Icon**: 📱 WhatsApp logo  
**Label**: "WhatsApp"  
**Sublabel**: "Response"  
**Color**: Green (#25D366)  
**Shape**: Rounded rectangle (150px × 100px)

**Arrow** → Orange, 10px thick

---

### Step 7: End User
**Icon**: 👨‍🌾 or user icon with checkmark  
**Label**: "Farmer"  
**Sublabel**: "Insights Delivered"  
**Color**: Green (#10B981)  
**Shape**: Rounded rectangle (150px × 100px)

---

## Layout Specifications

### Positioning (for 16:9 slide, 1920×1080px)
```
Step 1: X=100,  Y=400
Step 2: X=350,  Y=400
Step 3: X=600,  Y=400
Step 4: X=850,  Y=400
Step 5a: X=1100, Y=300 (DynamoDB - upper)
Step 5b: X=1100, Y=500 (S3 - lower)
Step 6: X=1350, Y=400
Step 7: X=1600, Y=400
```

### Spacing
- Horizontal gap between steps: 200px
- Vertical gap for split: 200px
- Arrow length: 50px between boxes

---

## Color Palette

### Primary Colors
- **AWS Orange**: #FF9900 (arrows, accents)
- **AWS Blue**: #232F3E (text, farmer icon)
- **WhatsApp Green**: #25D366 (WhatsApp boxes)
- **Bedrock Purple**: #8B5CF6 (AI box)

### Secondary Colors
- **DynamoDB Blue**: #3B82F6
- **S3 Green**: #10B981
- **Background**: White (#FFFFFF)
- **Container**: Light Gray (#F3F4F6)

---

## Typography

### Labels (Main Text)
- **Font**: Segoe UI Bold or Arial Bold
- **Size**: 18pt
- **Color**: #232F3E (dark blue)
- **Alignment**: Center

### Sublabels (Secondary Text)
- **Font**: Segoe UI Regular or Arial Regular
- **Size**: 12pt
- **Color**: #6B7280 (gray)
- **Alignment**: Center

---

## PowerPoint Implementation Steps

### 1. Create Boxes
- Insert → Shapes → Rounded Rectangle
- Size: 150px × 100px (main), 120px × 80px (AWS services)
- Fill: Use colors from palette above
- Border: None or 2px white
- Shadow: Subtle drop shadow (optional)

### 2. Add Icons
- Use PowerPoint icons (Insert → Icons)
- Search: "user", "mobile", "lightning", "brain", "database", "storage"
- Size: 40px × 40px
- Position: Top center of each box

### 3. Add Text
- Insert text boxes inside shapes
- Main label: 18pt bold
- Sublabel: 12pt regular
- Center aligned

### 4. Create Arrows
- Insert → Shapes → Block Arrow or Line with Arrow
- Width: 10px
- Color: #FF9900 (AWS Orange)
- Style: Solid line

### 5. Group AWS Services
- Draw rounded rectangle container
- Fill: #F3F4F6 (light gray)
- Border: 2px dashed #D1D5DB
- Send to back
- Add "AWS Services" label at top

### 6. Align Everything
- Select all shapes
- Format → Align → Distribute Horizontally
- Format → Align → Align Middle (for main flow)

---

## Alternative: Simple Text Version

If you want ultra-minimal:

```
Farmer → WhatsApp → Lambda → Bedrock → [DynamoDB + S3] → Response → Insights
  📱        📱         ⚡        🤖         🗄️ 📦           📱          ✅
```

---

## Quick PowerPoint Template

### Slide Title
"KisaanMitra.AI - System Architecture"

### Subtitle
"WhatsApp-Based Multi-Agent AI System"

### Footer
"Powered by AWS | Bedrock | Lambda | DynamoDB"

---

## Pro Tips for Hackathon Presentation

1. **Animate the flow**: Use "Appear" animation with 0.5s delay between steps
2. **Highlight AI**: Make Bedrock box slightly larger or add glow effect
3. **Show data flow**: Use dotted lines for data, solid for control flow
4. **Add metrics**: Small text below each box (e.g., "<3s response time")
5. **Keep it clean**: White background, minimal text, clear hierarchy

---

## Example Metrics to Add (Optional)

- **Lambda**: "1000+ concurrent"
- **Bedrock**: "95% accuracy"
- **DynamoDB**: "<10ms latency"
- **S3**: "Unlimited storage"
- **Response**: "<3 seconds"

---

## File Export

Once created in PowerPoint:
- Save as PNG: File → Export → PNG (High Quality)
- Resolution: 1920×1080 or higher
- Use for: Pitch deck, documentation, website

---

**Ready to implement in 5 minutes!** 🚀
