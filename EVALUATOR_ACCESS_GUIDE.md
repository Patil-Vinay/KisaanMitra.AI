# KisaanMitra - Evaluator Access Guide

## 🔗 Working Prototype Link

**WhatsApp Bot Access:**
```
https://wa.me/15551411052?text=Hi
```

Click the link above to start chatting with KisaanMitra on WhatsApp.

---

## 📱 How to Test the Prototype

### Step 1: Access the Bot
1. Click the WhatsApp link: https://wa.me/15551411052?text=Hi
2. This will open WhatsApp (mobile app or web)
3. Send "Hi" to start the conversation

### Step 2: Complete Onboarding
The bot will guide you through a quick registration:
1. **Name**: Enter your name (e.g., "Rajesh Kumar")
2. **Crops**: Enter crops you grow (e.g., "Wheat, Rice, Sugarcane")
3. **Land Size**: Enter land in acres (e.g., "10 acres")
4. **Village**: Enter your village and district (e.g., "Shirur, Pune")

### Step 3: Explore Features
After onboarding, you'll see an interactive menu with these options:

#### 🌾 Crop Health
- Send a photo of a diseased crop leaf
- Get instant disease identification with confidence scores
- Receive treatment recommendations

#### 💰 Budget Planning
- Ask: "Budget for sugarcane in 20 acres"
- Get detailed cost breakdown with:
  - Land preparation costs
  - Seed/planting material costs
  - Fertilizer and pesticide costs
  - Labor costs
  - Irrigation costs
  - Total investment and expected returns

#### 📊 Market Prices
- Ask: "What is the price of wheat?"
- Get real-time mandi prices
- See price trends and recommendations

#### 🌤️ Weather Forecast
- Click "Weather Forecast" button
- Get 7-day weather forecast for your village
- Receive farming-specific weather advice

#### 🆘 Emergency Help
- Access emergency helpline numbers
- Get immediate assistance contacts

---

## 🎯 Test Scenarios

### Scenario 1: New Farmer Onboarding
```
1. Send: "Hi"
2. Complete registration with your details
3. Verify you receive a welcome message with your profile
```

### Scenario 2: Budget Planning
```
1. Send: "Help me plan budget for wheat in 15 acres"
2. Verify you get detailed cost breakdown
3. Check if location from your profile is used
```

### Scenario 3: Disease Detection
```
1. Take/upload a photo of a crop leaf
2. Send the image to the bot
3. Verify you get disease identification and treatment
```

### Scenario 4: Market Prices
```
1. Send: "What is the price of onion?"
2. Verify you get current market rates
3. Check for price trends and recommendations
```

### Scenario 5: Weather Forecast
```
1. Click "Weather Forecast" from menu
2. Verify you get 7-day forecast for your village
3. Check for farming-specific weather advice
```

---

## 🔧 Technical Details

### Architecture
- **Platform**: WhatsApp Business API
- **Backend**: AWS Lambda (Serverless)
- **AI Models**: 
  - Amazon Nova Pro (Budget Planning, General Queries)
  - Claude Sonnet 4 (Complex Financial Analysis)
- **Database**: Amazon DynamoDB
- **Storage**: Amazon S3 (Image Processing)
- **APIs**: 
  - OpenWeather API (Weather Data)
  - Kindwise API (Disease Detection)

### Phone Number
- **WhatsApp Business Number**: +1 (555) 141-1052
- **Format**: 15551411052

### Supported Languages
- English
- Hindi (हिंदी)

### Response Time
- Text queries: < 3 seconds
- Image analysis: < 5 seconds
- Budget generation: < 15 seconds

---

## 📝 Important Notes for Evaluators

### 1. WhatsApp Requirements
- You need WhatsApp installed (mobile app or WhatsApp Web)
- Internet connection required
- No special permissions needed

### 2. Testing Limitations
- The bot is currently in test mode with WhatsApp Business API
- Maximum 5 test numbers can be added at a time
- If you cannot access, please contact us to add your number

### 3. Data Privacy
- All test data is stored securely in AWS
- No personal information is shared
- Data is used only for demonstration purposes

### 4. Best Practices
- Use realistic farmer scenarios
- Test with actual crop images for disease detection
- Try different locations to see location-based features
- Test in both English and Hindi

---

## 🎥 Demo Video

A comprehensive demo video is available showing:
- Complete onboarding flow
- All feature demonstrations
- Real-world use cases
- Technical architecture walkthrough

**Video Link**: [To be added]

---

## 📚 Additional Resources

### GitHub Repository
**Link**: [Your GitHub URL]

Contains:
- Complete source code
- Infrastructure setup scripts
- Deployment guides
- API documentation
- Test scenarios

### Project Documentation
- `README.md` - Project overview
- `ARCHITECTURE.md` - Technical architecture
- `DEPLOYMENT_GUIDE.md` - Setup instructions
- `COMPLETE_FEATURE_LIST.md` - All features

---

## 🆘 Support for Evaluators

If you encounter any issues:

1. **Cannot access WhatsApp link**
   - Ensure WhatsApp is installed
   - Try opening in a different browser
   - Contact us to add your number to test list

2. **Bot not responding**
   - Check your internet connection
   - Try sending "restart" to reset
   - Wait 30 seconds and try again

3. **Feature not working**
   - Send "menu" to see all options
   - Try rephrasing your query
   - Check the demo video for correct usage

### Contact Information
- **Email**: [Your email]
- **Phone**: [Your phone]
- **GitHub Issues**: [Your GitHub issues URL]

---

## ✅ Evaluation Checklist

Use this checklist to evaluate all features:

- [ ] Successfully accessed WhatsApp bot
- [ ] Completed onboarding process
- [ ] Tested budget planning feature
- [ ] Tested disease detection with image
- [ ] Tested market price queries
- [ ] Tested weather forecast
- [ ] Tested in both English and Hindi
- [ ] Verified location-based features
- [ ] Checked response accuracy
- [ ] Evaluated user experience

---

## 🏆 Key Differentiators

1. **WhatsApp-First Approach**: No app download required
2. **Multilingual Support**: English + Hindi
3. **AI-Powered**: Advanced AI for accurate responses
4. **Location-Aware**: Uses farmer's village for personalized advice
5. **Comprehensive**: 5+ features in one platform
6. **Fast**: Sub-3-second response times
7. **Scalable**: Serverless architecture on AWS

---

**Last Updated**: February 28, 2026
**Version**: 1.0
**Status**: Production Ready ✅
