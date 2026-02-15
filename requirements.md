# KisaanMitra.AI - Requirements Document

**Team**: KisaanMitra.AI

**Problem Statement**: AI for Rural Innovation & Sustainable Systems - Build an AI-powered solution that supports rural ecosystems, sustainability, or resource-efficient systems.

## 1. Problem Statement

Farmers lack timely, hyper-local and integrated decision support across crop management, financial planning and market intelligence, leading to low productivity, poor pricing decisions and financial risk. Existing information is fragmented, non-personalized and difficult to apply at village level.

## 2. Solution Overview

KisaanMitra.AI is a WhatsApp-based multi-agent AI system - a farmer's all-in-one intelligent assistant combining three specialized agents:

- **Crop Agent**: Hyper-local crop guidance, disease diagnosis, fertilizer/pesticide recommendations
- **Market Agent**: Demand forecasting, harvest timing, mandi prices, crop recommendations
- **Finance Agent**: Budget planning, government schemes, input cost optimization, loan planning

**Key Features**: Hindi + voice support, image-based disease detection, village-level knowledge graph

## 3. Functional Requirements

### 3.1 Crop Agent
- **Disease Detection**: Image + text input, high accuracy, instant response
- **Knowledge Graph**: Villages with crop-specific practices
- **Recommendations**: Fertilizer dosage, pesticide selection, irrigation schedule
- **Weather Integration**: Real-time alerts, 7-day forecast

### 3.2 Market Agent
- **Price Forecasting**: LSTM + Prophet models, high accuracy, 1-6 month horizon
- **Farmer's Market (Mandi) Tracking**: Large number of Farmer's Market (Mandis), daily updates, real-time prices
- **Crop Recommendation**: Multi-factor analysis (price, cost, risk, water)
- **Harvest Timing**: Optimal selling window with revenue scenarios

### 3.3 Finance Agent
- **Budget Planning**: Pre-planting cost estimation, ROI analysis
- **Scheme Matching**: 500+ schemes, AI-powered eligibility 
- **Price Comparison**: Lowest input costs across 10+ vendors
- **Loan Calculator**: crop loans, EMI, subsidy eligibility

### 3.4 WhatsApp Interface
- **Language**: Hindi (USP), voice + text support
- **Input Types**: Text, voice (AWS Transcribe), images, location
- **Response Time**: Instant Response
- **Onboarding**:Easy onboarding, progressive profiling

## 4. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| **Response Time** | Instant Response |
| **Uptime** | High Availability |
| **Cost per User** | <₹50/month |
| **Security** | TLS 1.3, AES-256, DPDP Act 2023 compliant |

## 5. User Journey

```
Onboarding → Pre-Planting → Growing → Harvest → Selling
```

## 6. Success Metrics

### Business Impact
- Farmer Income: **+20-30%**
- Crop Loss Reduction: **-40%**
- Input Cost Savings: **-15-20%**
- Better Market Prices: **+25%**

### User Adoption
- Target: 1M users (Year 1)
- DAU/MAU: >40%
- 90-day Retention: >60%

### Technical KPIs
- Response time: Instant response
- Uptime: high availability

## 7. Competitive Advantages

1. **Hyper-Local Intelligence**: Village-level knowledge graph (USP)
2. **Multi-Agent System**: Holistic vs fragmented solutions
3. **WhatsApp Native**: 500M+ users, zero friction
4. **Voice-First**: Low-literacy accessibility
5. **Data Moat**: Irreplaceable village-level data

## 8. Key Assumptions

- Farmers have WhatsApp on smartphones
- Basic literacy or voice message capability
- Willingness to share location and crop data
- Reliable data sources (weather, farmer market (mandi) prices)

## 10. Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Inaccurate disease diagnosis | Ensemble models, confidence thresholds, expert review |
| Wrong price predictions | Conservative estimates, confidence intervals, disclaimers |
| Data source unavailability | Multiple sources, caching, graceful degradation |
| Low user adoption | Local language, voice support, partnerships |

---

**Status**: Ready for Implementation
