# KisaanMitra.AI - Requirements Document

**Team**: KisaanMitra.AI | **Leader**: Aditya Mahesh Rane  
**Problem Statement**: AI for Rural Innovation & Sustainable Systems

## 1. Problem Statement

Farmers lack timely, hyper-local, and integrated decision support across crop management, financial planning, and market intelligence, leading to low productivity, poor pricing decisions, and financial risk. Existing information is fragmented, non-personalized, and difficult to apply at village level.

## 2. Solution Overview

KisaanMitra.AI is a WhatsApp-based multi-agent AI system - a farmer's all-in-one intelligent assistant combining three specialized agents:

- **Crop Agent**: Hyper-local crop guidance, disease diagnosis, fertilizer/pesticide recommendations
- **Finance Agent**: Budget planning, government schemes, input cost optimization, loan planning
- **Market Agent**: Demand forecasting, harvest timing, mandi prices, crop recommendations

**Key Features**: Hindi + voice support, image-based disease detection, village-level knowledge graph

## 3. Functional Requirements

### 3.1 Crop Agent
- **Disease Detection**: Image + text input, 95%+ accuracy, <3s response
- **Knowledge Graph**: 600K villages with crop-specific practices
- **Recommendations**: Fertilizer dosage, pesticide selection, irrigation schedule
- **Weather Integration**: Real-time alerts, 7-day forecast

### 3.2 Finance Agent
- **Budget Planning**: Pre-planting cost estimation, ROI analysis
- **Scheme Matching**: 500+ schemes, AI-powered eligibility (90%+ accuracy)
- **Price Comparison**: Lowest input costs across 10+ vendors
- **Loan Calculator**: KCC, crop loans, EMI, subsidy eligibility

### 3.3 Market Agent
- **Price Forecasting**: LSTM + Prophet models, 85%+ accuracy, 1-6 month horizon
- **Mandi Tracking**: 3000+ mandis, daily updates, real-time prices
- **Crop Recommendation**: Multi-factor analysis (price, cost, risk, water)
- **Harvest Timing**: Optimal selling window with revenue scenarios

### 3.4 WhatsApp Interface
- **Language**: Hindi (MVP), voice + text support
- **Input Types**: Text, voice (AWS Transcribe), images, location
- **Response Time**: <2s (p95)
- **Onboarding**: <3 minutes, progressive profiling

## 4. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| **Response Time** | <2s (p95) |
| **Uptime** | 99.9% |
| **Concurrent Users** | 100K |
| **ML Accuracy** | Disease >95%, Price >85%, Intent >95% |
| **Cost per User** | <₹5/month |
| **Security** | TLS 1.3, AES-256, DPDP Act 2023 compliant |

## 5. User Journey

```
Onboarding → Pre-Planting → Growing → Harvest → Selling
    ↓            ↓            ↓          ↓         ↓
  "Hi"    "Kaunsi fasal   Disease   "Kab      Market
          lagau?"         Diagnosis  harvest   Intelligence
                                     karu?"    + ROI
```

**Complete cycle**: From "Hi" on WhatsApp to profit in bank

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
- Response time: <2s (p95)
- Uptime: >99.9%
- Model accuracy: Disease >95%, Price >85%

## 7. MVP Scope (3 Months)

**Month 1**: Infrastructure + WhatsApp integration  
**Month 2**: 3 agents + ML models (disease detection, price forecasting)  
**Month 3**: Hindi optimization + beta (1000 farmers)

**Post-MVP**: 11 additional languages, satellite imagery, peer network

## 8. Competitive Advantages

1. **Hyper-Local Intelligence**: Village-level knowledge graph (unique)
2. **Multi-Agent System**: Holistic vs fragmented solutions
3. **WhatsApp Native**: 500M+ users, zero friction
4. **Voice-First**: Low-literacy accessibility
5. **Data Moat**: Irreplaceable village-level data

## 9. Key Assumptions

- Farmers have WhatsApp on smartphones
- Basic literacy or voice message capability
- Willingness to share location and crop data
- Reliable data sources (weather, mandi prices)

## 10. Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Inaccurate disease diagnosis | Ensemble models, confidence thresholds, expert review |
| Wrong price predictions | Conservative estimates, confidence intervals, disclaimers |
| Data source unavailability | Multiple sources, caching, graceful degradation |
| Low user adoption | Local language, voice support, partnerships |

---

**Status**: Ready for Implementation  
**Target**: 140M+ Indian Farmers
