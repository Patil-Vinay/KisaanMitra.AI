# 🎯 KisaanMitra - Evaluator Demo Guide

## For AWS AI Challenge Evaluators

Welcome! This guide provides multiple ways to experience KisaanMitra, our AI-powered farming assistant built entirely on AWS.

---

## 🌐 Option 1: Interactive Web Demo (Recommended)

**Best for:** Instant access, no setup required

### Access URL
```
[WILL BE PROVIDED AFTER DEPLOYMENT]
```

### What You Can Do
- ✅ Chat with AI farming assistant
- ✅ Get real-time market prices & forecasts
- ✅ Request budget planning with ROI calculations
- ✅ Upload crop images for disease detection
- ✅ Get hyperlocal weather forecasts
- ✅ Switch between English and Hindi

### Quick Test Scenarios

1. **Market Intelligence**
   - Type: "What is the current price of tomato?"
   - Expected: Live mandi prices from AgMarkNet API

2. **Budget Planning**
   - Type: "Budget planning for wheat in 10 acres"
   - Expected: Complete cost breakdown, revenue projection, ROI

3. **Disease Detection**
   - Click 📎 icon and upload a crop disease image
   - Expected: AI diagnosis with treatment recommendations

4. **Weather Forecast**
   - Type: "Weather forecast"
   - Expected: Hyperlocal weather with farming advice

5. **Multi-language**
   - Click "हिंदी" button to switch language
   - Type: "गेहूं की कीमत क्या है?"
   - Expected: Response in Hindi

---

## 📊 Option 2: Knowledge Graph Dashboard

**Best for:** Visualizing farmer network and community insights

### Access URL
```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com
```

### Features
- Interactive D3.js visualization
- 50 farmers across 10 villages
- Drag-and-drop nodes
- Real-time statistics
- Community network analysis

---

## 📈 Option 3: Analytics Dashboard

**Best for:** System metrics and farmer data

### Access URL
```
[Deploy with: ./deploy_dashboard_now.sh]
```

### Features
- Real-time farmer count from DynamoDB
- Live conversation feed
- Crop distribution analytics
- Auto-refresh every 30 seconds
- CSV export capabilities

---

## 📱 Option 4: WhatsApp Access (Limited)

**Best for:** Real WhatsApp experience

Due to WhatsApp Business API limitations, we can only add a limited number of test users. If you'd like WhatsApp access:

1. **Request Access:** Email your WhatsApp number
2. **We'll Add You:** Within 24 hours
3. **Start Chatting:** Send "Hi" to get started

**Test Number:** [Your WhatsApp Business Number]

---

## 🎥 Option 5: Video Walkthrough

**Best for:** Quick overview without interaction

### Demo Video
```
[Upload your demo video to S3 and provide link]
```

### What's Covered
- Complete onboarding flow
- All agent capabilities
- Disease detection demo
- Hyperlocal alert system
- Knowledge graph visualization

---

## 🏗️ AWS Architecture Highlights

### Services Used
- **AWS Bedrock (Amazon Nova Pro)** - AI/ML inference
- **AWS Lambda** - Serverless compute
- **Amazon DynamoDB** - NoSQL database
- **Amazon API Gateway** - REST API
- **Amazon S3** - Static hosting
- **Amazon CloudWatch** - Monitoring

### Key Features
- 100% serverless architecture
- Auto-scaling
- Pay-per-use pricing
- Multi-region capable
- High availability

---

## 🧪 Test Scenarios

### Scenario 1: New Farmer Onboarding
1. Open web demo
2. Type "Hi"
3. Follow onboarding prompts
4. Provide: Name, Village, District, Crops, Land size
5. See profile created in real-time

### Scenario 2: Market Intelligence
1. Ask: "Current price of onion in Pune"
2. Get live AgMarkNet data
3. Ask: "7-day price forecast for onion"
4. Get AI-powered predictions

### Scenario 3: Budget Planning
1. Ask: "Budget planning for sugarcane in 20 acres"
2. Get complete breakdown:
   - Input costs (seeds, fertilizer, pesticides)
   - Labor costs
   - Equipment costs
   - Revenue projection
   - Net profit & ROI

### Scenario 4: Disease Detection
1. Upload tomato late blight image
2. Get AI diagnosis with:
   - Disease name
   - Confidence score
   - Symptoms
   - Treatment recommendations
   - Prevention tips

### Scenario 5: Hyperlocal Alerts
1. One farmer uploads diseased crop image
2. System detects disease
3. Nearby farmers in same village get alerts
4. Community-wide disease tracking

---

## 📊 Expected Performance

### Response Times
- Text queries: 2-4 seconds
- Image analysis: 3-5 seconds
- Market data: 1-2 seconds (cached)
- Weather: 1-2 seconds

### Accuracy
- Disease detection: 85%+ confidence
- Price forecasts: Based on historical trends
- Budget calculations: Real market data

### Scalability
- Concurrent users: 1000+
- Requests/second: 100+
- Auto-scaling enabled

---

## 🎯 Evaluation Criteria Coverage

### 1. Innovation
- ✅ Multi-agent AI architecture
- ✅ Hyperlocal disease alerts
- ✅ Knowledge graph for community insights
- ✅ Real-time price forecasting

### 2. AWS Integration
- ✅ AWS Bedrock for AI
- ✅ Serverless architecture
- ✅ DynamoDB for data
- ✅ API Gateway for web access

### 3. Impact
- ✅ Addresses 130M+ Indian farmers
- ✅ Multi-language support
- ✅ WhatsApp-based (800M+ users in India)
- ✅ Community-driven approach

### 4. Technical Excellence
- ✅ Microservice architecture
- ✅ Performance optimized
- ✅ Comprehensive error handling
- ✅ Monitoring & logging

### 5. Scalability
- ✅ Serverless auto-scaling
- ✅ Caching layer
- ✅ Rate limiting
- ✅ Connection pooling

---

## 🐛 Troubleshooting

### Web Demo Not Loading
- Check if API Gateway is deployed
- Verify Lambda handler is set to web mode
- Check browser console for errors

### No Response from Chat
- Verify API endpoint in HTML
- Check Lambda logs in CloudWatch
- Ensure CORS is configured

### Image Upload Fails
- Check file size (<5MB)
- Ensure image format (JPG, PNG)
- Verify Lambda timeout (120s)

---

## 📞 Contact & Support

### For Questions
- **Email:** [Your Email]
- **GitHub:** [Your GitHub Repo]
- **Documentation:** See WEB_DEMO_DEPLOYMENT.md

### For Issues
- Check CloudWatch logs
- Review API Gateway metrics
- Test with curl command

---

## 🎉 Quick Start for Evaluators

1. **Open Web Demo:** [Your S3 Website URL]
2. **Type:** "Hi"
3. **Try:** "Budget planning for wheat in 10 acres"
4. **Upload:** A crop disease image
5. **Explore:** Knowledge graph dashboard

**That's it!** You're experiencing KisaanMitra powered by AWS.

---

## 📚 Additional Resources

- **Architecture Diagram:** AWS_ARCHITECTURE_VISUAL.md
- **Feature List:** FEATURES_LIST.md
- **Sample Commands:** SAMPLE_COMMANDS.md
- **Deployment Guide:** WEB_DEMO_DEPLOYMENT.md
- **Performance Metrics:** PERFORMANCE_OPTIMIZATION_COMPLETE.md

---

**Built with ❤️ for Indian Farmers**  
**Powered by AWS Bedrock, Lambda, DynamoDB, and more**  
**Submission for AWS AI Challenge 2026**
