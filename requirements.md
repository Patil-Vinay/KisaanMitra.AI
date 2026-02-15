# KisaanMitra.AI - Requirements Document

## 1. Executive Summary

KisaanMitra.AI is a WhatsApp-based multi-agent AI system delivering hyper-local agricultural intelligence to Indian farmers. Three specialized AI agents—Crop, Finance, and Market—provide real-time, data-driven recommendations through conversational AI, making advanced agricultural technology accessible via the most widely-used platform in rural India.

**Core Value Proposition**: Transform farmer decision-making from guesswork to data-driven precision, increasing profitability by 20-30% through optimized crop selection, reduced input costs, and better market timing.

## 2. Business Objectives

- **Increase Farmer Income**: 20-30% profit improvement through optimized decisions
- **Reduce Crop Losses**: 40% reduction via early disease detection and treatment
- **Optimize Input Costs**: 15-20% savings through price comparison and scheme matching
- **Improve Market Timing**: 25% better prices through demand forecasting
- **Scale Rapidly**: Reach 1M farmers in Year 1, 10M by Year 3
- **Hyper-Local Intelligence**: Village-level recommendations using knowledge graphs

## 3. Target Users

**Primary**: 140M+ Indian farmers with smartphones
- **Small/Marginal** (0-5 acres): 86% of farmers, highest impact potential
- **Medium** (5-10 acres): 12% of farmers, early adopters
- **Large** (>10 acres): 2% of farmers, premium features

**User Context**:
- **Languages**: Hindi (MVP), English + 10 regional languages (future roadmap)
- **Platform**: WhatsApp (500M+ users in India, 80%+ rural penetration)
- **Connectivity**: 2G/3G/4G intermittent (offline-first design)
- **Literacy**: Variable (voice + visual interface required)

## 4. Functional Requirements

### 4.1 Crop Agent - Hyper-Local Agricultural Intelligence

**FR-CA-001: Village-Level Knowledge Graph**
- 600K+ villages mapped with crop-specific practices, soil types, climate patterns
- Real-time updates from successful farmer practices (crowdsourced intelligence)
- Graph queries: Village → Crops → Varieties → Practices → Success Metrics
- Stage-wise guidance: Sowing → Growth → Flowering → Harvest (automated reminders)

**FR-CA-002: AI-Powered Disease Detection**
- Computer vision model: 95%+ accuracy on 50+ common Indian crop diseases
- Multi-image support with severity scoring (mild/moderate/severe)
- Response time: <5 seconds from image upload to diagnosis
- Treatment recommendations: Organic + chemical options with local availability
- Cost-benefit analysis for each treatment option

**FR-CA-003: Smart Fertilizer & Pesticide Recommendations**
- NPK calculation based on soil test + crop stage + target yield
- Dosage optimization (prevent over-application, save costs)
- Weather-aware application timing (rain forecasts, temperature)
- Generic alternatives to branded products (30-40% cost savings)
- Safety warnings for harmful combinations

**FR-CA-004: Weather-Integrated Advisory**
- Real-time weather data (IMD + private APIs) updated every 3 hours
- 7-day forecast with crop-specific impact analysis
- Extreme weather alerts: Frost, heatwave, heavy rain, hailstorm
- Automated recommendations: Irrigation scheduling, pest outbreak predictions

### 4.2 Finance Agent - Complete Financial Planning

**FR-FA-001: Pre-Planting Budget Calculator**
- Comprehensive cost estimation: Seeds, fertilizers, pesticides, labor, irrigation, misc
- Regional price variations (district-level accuracy)
- Cash flow timeline: When to spend, when to expect returns
- ROI projections with risk scenarios (best/expected/worst case)
- Comparison across crop options for same land

**FR-FA-002: Government Scheme Intelligence**
- 500+ schemes database (central + all states) updated weekly
- AI-powered eligibility matching (90%+ accuracy)
- Ranked recommendations with expected benefits in ₹
- Application guidance: Documents, deadlines, online/offline process
- Status tracking integration (where available)

**FR-FA-003: Input Price Comparison Engine**
- Real-time price aggregation from 10+ sources (vendors, e-commerce, cooperatives)
- Same-product comparison with quality ratings
- Generic alternatives identification (save 30-40%)
- Bulk purchase opportunities (group buying suggestions)
- Delivery cost and time factored in

**FR-FA-004: Loan & Subsidy Optimizer**
- Loan requirement calculation based on budget gap
- Product recommendations: KCC, crop loans, microfinance (with interest rates)
- Subsidy eligibility and quantum calculation
- EMI calculator with repayment capacity analysis
- Documentation checklist and bank branch locator

### 4.3 Market Agent - Predictive Market Intelligence

**FR-MA-001: Price Forecasting (Time-Series AI)**
- LSTM + Prophet ensemble models trained on 5+ years of mandi data
- Forecast horizon: 1-6 months with 85%+ accuracy
- Confidence intervals and trend direction (bullish/bearish/stable)
- Weekly model retraining with latest data
- Crop-specific and variety-specific predictions

**FR-MA-002: Real-Time Mandi Price Tracking**
- 3000+ mandis across India (Agmarknet + state APIs)
- Daily updates at 6 PM IST (post-market close)
- Price comparison: Nearby mandis (50km radius) + state average + national average
- Historical trends: 7-day, 30-day, 90-day, 1-year
- Arrival quantity data (supply indicator)

**FR-MA-003: Pre-Planting Crop Recommendation**
- Multi-factor analysis: Expected prices, input costs, water availability, farmer experience
- ROI ranking for top 5 suitable crops
- Risk assessment: Market volatility, weather risk, disease susceptibility
- Diversification suggestions (don't put all eggs in one basket)
- Success probability scores

**FR-MA-004: Harvest Timing Optimizer**
- Dynamic optimization: Current price vs forecasted price vs crop maturity
- Scenario analysis: Harvest now vs wait 1 week vs wait 2 weeks
- Storage cost consideration (if applicable)
- Quality degradation risk (over-ripening)
- Recommended action with expected revenue impact

**FR-MA-005: Supply-Demand Intelligence**
- Satellite imagery analysis for crop area estimation (ISRO data)
- Government sowing reports (real-time during season)
- Import/export trends and policy changes
- Regional oversupply/undersupply alerts
- Market sentiment indicators

**FR-MA-006: Smart Alerts & Notifications**
- Price threshold alerts (user-defined triggers)
- Favorable selling opportunity notifications
- Sudden market movement alerts (>10% change)
- Weekly market summary (voice message option)
- Scheme deadline reminders

### 4.4 WhatsApp Interface - Conversational AI

**FR-WA-001: Intelligent Multi-Language NLP**
- **MVP**: Hindi only (covers 43% of Indian farmers)
- **Future**: English, Punjabi, Marathi, Telugu, Tamil, Bengali, Gujarati, Kannada, Malayalam, Odia, Assamese (11 additional languages)
- Auto-detection with 98%+ accuracy (IndicBERT-based)
- Context-aware translation (agricultural domain-specific)
- Code-mixing support (Hinglish, etc.)

**FR-WA-002: Multi-Modal Input Processing**
- Text: Natural language queries with entity extraction
- Voice: Speech-to-text with 90%+ accuracy (AWS Transcribe + custom models)
- Images: Disease detection, document OCR (soil reports, land records)
- Location: GPS-based village identification for hyper-local recommendations

**FR-WA-003: Context-Aware Conversation**
- Session persistence: 30-day conversation history
- Multi-turn dialogue with context retention
- Proactive clarification for ambiguous queries
- Quick reply buttons for common actions (Yes/No, crop selection, etc.)
- Conversation summarization for long interactions

**FR-WA-004: Smart Agent Routing**
- Intent classification: 95%+ accuracy using fine-tuned BERT
- Multi-agent query handling (e.g., "Which crop to grow and what's the budget?")
- Seamless handoffs between agents with context transfer
- Explicit agent selection via keywords or menu

**FR-WA-005: Rapid Onboarding (<3 minutes)**
- Progressive profiling: Collect data as needed, not upfront
- OTP-based phone verification
- Location auto-detection with manual override
- Interactive tutorial with sample queries
- Profile completion incentives

## 5. Non-Functional Requirements

### 5.1 Performance (Critical for User Experience)
- **Response Time**: <2s for text queries (p95), <5s for image analysis (p95)
- **Throughput**: 100K concurrent users, 10M messages/day
- **Model Inference**: <500ms for NLP, <3s for disease detection
- **Database Queries**: <100ms for 95% of queries

### 5.2 Scalability (Built for 10M+ Users)
- Horizontal auto-scaling: 10x capacity in <5 minutes
- Multi-region deployment: Mumbai (primary), Hyderabad (DR)
- Database sharding: User-based partitioning for 100M+ users
- CDN for media: <200ms latency globally

### 5.3 Availability (Always-On Service)
- **Uptime**: 99.9% (8.76 hours downtime/year max)
- **RTO**: 4 hours (Recovery Time Objective)
- **RPO**: 1 hour (Recovery Point Objective - max data loss)
- Multi-AZ deployment with automatic failover

### 5.4 Security & Privacy (Farmer Data Protection)
- **Encryption**: TLS 1.3 (transit), AES-256 (rest)
- **Compliance**: DPDP Act 2023, ISO 27001 (target)
- **Data Residency**: All data stored in India
- **Access Control**: RBAC with audit logging
- **PII Protection**: Anonymization in logs, right to deletion

### 5.5 Reliability (Zero Data Loss)
- Automated backups: Every 6 hours with 30-day retention
- Point-in-time recovery: 5-minute granularity
- Data replication: 3x redundancy (Multi-AZ)
- Chaos engineering: Monthly resilience testing

### 5.6 Cost Efficiency (Sustainable Economics)
- **Target**: <₹5/user/month operational cost
- Spot instances for batch jobs (50% savings)
- Reserved instances for baseline (40% savings)
- Model optimization: Quantization, pruning (3x faster inference)
- Intelligent caching: 80%+ cache hit rate

### 5.7 Accuracy (Trust is Everything)
- Disease detection: >95% accuracy (validated against agronomists)
- Price forecasting: >85% accuracy (MAPE <15%)
- Intent classification: >95% accuracy
- Speech-to-text: >90% accuracy for Indian accents
- Scheme matching: >90% precision

## 6. Data Requirements

### 6.1 Critical Data Sources
| Data Type | Source | Update Frequency | Coverage |
|-----------|--------|------------------|----------|
| Weather | IMD + OpenWeather | 3 hours | Pan-India |
| Mandi Prices | Agmarknet + State APIs | Daily (6 PM) | 3000+ mandis |
| Satellite Imagery | ISRO + Sentinel | Weekly | 1m resolution |
| Soil Data | ICAR + State Depts | On-demand | District-level |
| Schemes | Govt Portals (scraped) | Weekly | 500+ schemes |
| Disease Images | PlantVillage + Custom | Continuous | 50+ diseases |
| Crop Yields | Govt Reports + Farmers | Seasonal | Village-level |

### 6.2 Knowledge Graph Structure
```
Village (600K nodes)
  ├─ Soil Type, Climate, Water Availability
  ├─ Crops Grown (historical 5 years)
  │   ├─ Varieties
  │   ├─ Success Rate
  │   ├─ Average Yield
  │   └─ Best Practices
  └─ Successful Farmers
      ├─ Techniques Used
      └─ Results Achieved
```

### 6.3 Data Storage Strategy
- **Hot Data** (last 30 days): DynamoDB, ElastiCache (sub-ms access)
- **Warm Data** (30-365 days): RDS, Timestream (ms access)
- **Cold Data** (>1 year): S3 Glacier (archival, hours access)
- **ML Training Data**: S3 with versioning (DVC for lineage)

## 7. Success Metrics (Measurable Impact)

### 7.1 User Adoption
- **Target**: 1M users in Year 1, 10M by Year 3
- DAU/MAU ratio: >40% (high engagement)
- Retention: >60% at 90 days
- Messages per user: >20/month
- Feature adoption: >70% use all 3 agents

### 7.2 Business Impact (Real-World Outcomes)
- **Farmer Income**: +20-30% average increase
- **Crop Loss Reduction**: -40% via early disease detection
- **Input Cost Savings**: -15-20% through optimization
- **Market Timing**: +25% better prices vs random selling
- **Scheme Access**: 10x increase in successful applications

### 7.3 Technical Excellence
- Model accuracy: Disease >95%, Price >85%, Intent >95%
- System uptime: >99.9%
- Response time: <2s (p95)
- Error rate: <0.1%
- Cost per user: <₹5/month

### 7.4 User Satisfaction
- NPS Score: >50 (world-class)
- 5-star rating: >4.5/5
- Support tickets: <2% of users/month
- Resolution time: <4 hours (critical issues)

## 8. Competitive Advantages

1. **Hyper-Local Intelligence**: Village-level knowledge graph (no competitor has this)
2. **Multi-Agent Architecture**: Holistic solution vs point solutions
3. **WhatsApp Native**: 500M+ users, zero app download friction
4. **Real-Time Price Forecasting**: LSTM models with 85%+ accuracy
5. **Voice-First Design**: Accessibility for low-literacy farmers
6. **Offline Resilience**: Cached responses for common queries
7. **Free Forever**: Ad-supported or govt-subsidized model

## 9. Technical Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Inaccurate disease diagnosis | High | Ensemble models + confidence thresholds + expert review loop |
| Price prediction failures | High | Conservative estimates + confidence intervals + disclaimers |
| WhatsApp API rate limits | Medium | Multi-number strategy + queue management + user communication |
| Data source unavailability | Medium | Multiple sources + caching + graceful degradation |
| Model bias (region/crop) | Medium | Diverse training data + fairness metrics + continuous monitoring |
| Scalability bottlenecks | Medium | Load testing + auto-scaling + performance budgets |
| Security breach | High | Penetration testing + bug bounty + incident response plan |

## 10. MVP Scope (3-Month Timeline)

**Phase 1 (Month 1): Core Infrastructure**
- WhatsApp integration + basic NLP (Hindi + English)
- User onboarding + profile management
- Single-region deployment (Mumbai)

**Phase 2 (Month 2): Agent Development**
- Crop Agent: Disease detection + basic recommendations
- Finance Agent: Budget calculator + scheme database
- Market Agent: Mandi price tracking + simple forecasting

**Phase 3 (Month 3): Polish & Launch**
- Hindi language optimization (voice + text)
- Knowledge graph (100K villages)
- Beta testing with 1000 farmers
- Performance optimization + monitoring

**Post-MVP Roadmap**:
- Multi-language support (English + 10 regional languages)
- Advanced ML models (LSTM, graph neural networks)
- Voice interface optimization
- Satellite imagery integration
- Peer-to-peer farmer network
- Equipment rental marketplace
