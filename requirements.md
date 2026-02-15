# KisaanMitra.AI - Requirements Document

## 1. Executive Summary

KisaanMitra.AI is a WhatsApp-based multi-agent AI system that serves as an intelligent agricultural assistant for Indian farmers. The system provides hyper-local crop guidance, financial planning, and market intelligence through three specialized AI agents accessible via WhatsApp.

## 2. Business Objectives

- Democratize access to advanced agricultural intelligence for farmers across India
- Increase farmer profitability through data-driven decision making
- Reduce crop losses through timely disease diagnosis and treatment recommendations
- Optimize input costs and improve financial planning
- Enable better market timing and crop selection decisions
- Provide hyper-local, personalized recommendations at village level

## 3. Target Users

### Primary Users
- Small and marginal farmers (0-5 acres)
- Medium farmers (5-10 acres)
- Large farmers (>10 acres)

### User Characteristics
- Primary language: Hindi and regional languages (Punjabi, Marathi, Telugu, Tamil, Bengali, etc.)
- Technology access: Basic smartphones with WhatsApp
- Literacy levels: Variable (voice message support required)
- Internet connectivity: Intermittent 2G/3G/4G

## 4. Functional Requirements

### 4.1 Crop Agent

#### FR-CA-001: Hyper-Local Crop Guidance
- System shall provide crop recommendations based on village-level data
- System shall maintain a knowledge graph of village-specific agricultural practices
- System shall consider soil type, climate, and historical crop performance
- System shall provide stage-wise crop management guidance (sowing, growth, flowering, harvest)

#### FR-CA-002: Disease & Pest Diagnosis
- System shall accept crop images for disease/pest identification
- System shall accept text descriptions of symptoms
- System shall provide diagnosis with confidence scores
- System shall recommend treatment options (organic and chemical)
- System shall provide severity assessment and urgency indicators

#### FR-CA-003: Fertilizer & Pesticide Recommendations
- System shall recommend fertilizers based on crop stage and soil conditions
- System shall suggest pesticides for identified diseases/pests
- System shall provide dosage and application timing
- System shall recommend cost-effective alternatives
- System shall warn about harmful chemical combinations

#### FR-CA-004: Best Practices Sharing
- System shall identify and share practices from successful nearby farmers
- System shall provide seasonal advisories
- System shall send weather-based alerts and recommendations
- System shall integrate real-time weather data for the farmer's location

#### FR-CA-005: Soil & Weather Integration
- System shall integrate soil test reports when available
- System shall provide recommendations based on current and forecasted weather
- System shall alert farmers about adverse weather conditions

### 4.2 Finance Agent

#### FR-FA-001: Budget Planning
- System shall create pre-planting budget estimates
- System shall calculate expected costs for seeds, fertilizers, pesticides, labor, irrigation
- System shall provide crop-wise cost breakdowns
- System shall track actual expenses vs planned budget
- System shall calculate expected ROI based on market prices

#### FR-FA-002: Government Scheme Discovery
- System shall maintain updated database of central and state schemes
- System shall match farmer profile with eligible schemes
- System shall provide application guidance and documentation requirements
- System shall track application status where possible
- System shall send alerts for new scheme launches and deadlines

#### FR-FA-003: Input Cost Optimization
- System shall compare prices of fertilizers/pesticides across local vendors
- System shall identify lowest-cost quality inputs
- System shall suggest bulk purchase opportunities
- System shall recommend generic alternatives to branded products

#### FR-FA-004: Loan & Subsidy Planning
- System shall calculate loan requirements based on budget
- System shall recommend suitable loan products (KCC, crop loans, etc.)
- System shall provide subsidy calculation and eligibility
- System shall guide on documentation and application process

#### FR-FA-005: Risk Assessment
- System shall estimate profit vs investment ratios
- System shall provide risk scores based on crop choice, weather, market volatility
- System shall suggest crop insurance options
- System shall calculate break-even points

### 4.3 Market Agent

#### FR-MA-001: Harvest Timing Optimization
- System shall predict optimal harvest dates based on market conditions
- System shall consider crop maturity, weather, and price trends
- System shall provide early/late harvest trade-off analysis
- System shall send harvest timing alerts

#### FR-MA-002: Demand & Price Forecasting
- System shall forecast crop prices for next 3-6 months
- System shall use time-series models trained on historical mandi data
- System shall provide confidence intervals for predictions
- System shall update forecasts weekly based on new data

#### FR-MA-003: Pre-Planting Crop Recommendation
- System shall recommend crops based on expected demand and prices
- System shall consider farmer's land, resources, and experience
- System shall provide comparative analysis of multiple crop options
- System shall factor in water availability and input costs

#### FR-MA-004: Mandi Price Tracking
- System shall provide real-time prices from nearby mandis (within 50km)
- System shall show price trends (daily, weekly, monthly)
- System shall compare prices across multiple mandis
- System shall identify best selling locations

#### FR-MA-005: Supply-Demand Intelligence
- System shall analyze regional supply-demand dynamics
- System shall alert on oversupply/undersupply situations
- System shall provide market sentiment indicators
- System shall track competitor crop planting patterns

#### FR-MA-006: Notification System
- System shall send price alerts when thresholds are crossed
- System shall notify about favorable selling opportunities
- System shall alert on sudden market changes
- System shall provide weekly market summaries

### 4.4 WhatsApp Interface

#### FR-WA-001: Multi-Language Support
- System shall support Hindi, English, and 10+ regional languages
- System shall auto-detect user language preference
- System shall allow language switching mid-conversation

#### FR-WA-002: Multi-Modal Input
- System shall accept text messages
- System shall accept voice messages (with speech-to-text)
- System shall accept images (crops, diseases, documents)
- System shall accept location data

#### FR-WA-003: Conversational AI
- System shall maintain conversation context across sessions
- System shall handle multi-turn dialogues
- System shall clarify ambiguous queries
- System shall provide quick reply buttons for common actions

#### FR-WA-004: User Onboarding
- System shall collect farmer profile (name, location, crops, land size)
- System shall verify mobile number
- System shall provide tutorial on system capabilities
- System shall allow profile updates

#### FR-WA-005: Agent Routing
- System shall intelligently route queries to appropriate agent
- System shall handle multi-agent queries
- System shall provide seamless handoffs between agents
- System shall allow explicit agent selection

## 5. Non-Functional Requirements

### 5.1 Performance
- NFR-001: System shall respond to text queries within 3 seconds (95th percentile)
- NFR-002: Image analysis shall complete within 10 seconds
- NFR-003: System shall support 100,000 concurrent users
- NFR-004: System shall handle 1 million messages per day

### 5.2 Scalability
- NFR-005: Architecture shall scale horizontally to support 10M+ users
- NFR-006: Database shall handle 100M+ farmer interactions
- NFR-007: System shall support multi-region deployment

### 5.3 Availability
- NFR-008: System shall maintain 99.9% uptime
- NFR-009: Critical services shall have automatic failover
- NFR-010: System shall gracefully degrade during partial outages

### 5.4 Security & Privacy
- NFR-011: All data shall be encrypted in transit (TLS 1.3)
- NFR-012: All data shall be encrypted at rest (AES-256)
- NFR-013: System shall comply with Indian data protection regulations
- NFR-014: Farmer data shall not be shared with third parties without consent
- NFR-015: System shall implement role-based access control
- NFR-016: System shall maintain audit logs for all data access

### 5.5 Reliability
- NFR-017: System shall have automated backup every 6 hours
- NFR-018: System shall support point-in-time recovery
- NFR-019: Critical bugs shall be resolved within 4 hours
- NFR-020: System shall have comprehensive error handling and logging

### 5.6 Usability
- NFR-021: Farmers shall complete onboarding within 5 minutes
- NFR-022: System shall use simple, jargon-free language
- NFR-023: Voice messages shall be transcribed with >90% accuracy
- NFR-024: System shall provide help/FAQ access within conversation

### 5.7 Localization
- NFR-025: System shall support 12+ Indian languages
- NFR-026: Currency shall be displayed in INR
- NFR-027: Measurements shall use local units (quintal, bigha, etc.)
- NFR-028: Dates shall follow DD/MM/YYYY format

### 5.8 Cost Efficiency
- NFR-029: Per-user operational cost shall be <₹10/month
- NFR-030: System shall optimize AI model inference costs
- NFR-031: System shall use spot instances where appropriate

## 6. Data Requirements

### 6.1 Input Data Sources
- Weather data (IMD, private weather APIs)
- Mandi prices (Agmarknet, state agricultural marketing boards)
- Soil data (ICAR, state agriculture departments)
- Satellite imagery (ISRO, Sentinel)
- Government schemes database
- Historical crop yield data
- Disease/pest image datasets
- Fertilizer/pesticide databases
- Local vendor pricing data

### 6.2 Data Storage Requirements
- User profiles and preferences
- Conversation history (minimum 1 year)
- Farmer location and land details
- Crop cultivation history
- Financial transactions and budgets
- Image uploads (diseases, soil tests)
- Knowledge graph (village-level agricultural data)
- Time-series market data (minimum 5 years)
- Model training data and versions

### 6.3 Data Quality
- Weather data shall be updated every 3 hours
- Mandi prices shall be updated daily
- Government schemes shall be reviewed monthly
- Knowledge graph shall be updated based on farmer feedback
- Model accuracy shall be monitored continuously

## 7. Integration Requirements

### 7.1 External Integrations
- WhatsApp Business API
- Payment gateways (for future premium features)
- Government portals (scheme applications)
- Mandi price APIs
- Weather service APIs
- SMS gateway (backup communication)
- Email service (reports, notifications)

### 7.2 Internal Integrations
- All three agents shall share common user context
- Agents shall exchange relevant information
- Unified analytics and monitoring
- Centralized user management

## 8. Compliance Requirements

- Compliance with IT Act, 2000
- Compliance with Digital Personal Data Protection Act, 2023
- Compliance with WhatsApp Business Policy
- Compliance with agricultural advisory regulations
- Compliance with financial advisory regulations (if applicable)

## 9. Success Metrics

### 9.1 User Engagement
- Daily Active Users (DAU)
- Monthly Active Users (MAU)
- Messages per user per month
- User retention rate (30-day, 90-day)
- Feature adoption rates

### 9.2 Business Impact
- Farmer income improvement (%)
- Reduction in crop losses (%)
- Cost savings on inputs (%)
- Successful government scheme applications
- Market timing accuracy

### 9.3 Technical Metrics
- System uptime (%)
- Response time (p50, p95, p99)
- Error rates
- Model accuracy (disease detection, price prediction)
- API success rates

### 9.4 User Satisfaction
- Net Promoter Score (NPS)
- User satisfaction rating
- Feature usefulness ratings
- Support ticket volume and resolution time

## 10. Future Enhancements (Out of Scope for V1)

- Equipment rental marketplace
- Peer-to-peer farmer network
- Video tutorials and training
- Integration with farm equipment IoT sensors
- Crop insurance claim assistance
- Direct buyer-farmer marketplace
- Community forums
- Expert consultation booking
- Livestock management features
- Water management and irrigation optimization

## 11. Assumptions and Constraints

### Assumptions
- Farmers have access to WhatsApp on smartphones
- Basic literacy or ability to use voice messages
- Willingness to share location and crop data
- Availability of reliable data sources (weather, mandi prices)

### Constraints
- WhatsApp message size limits (16MB for media)
- WhatsApp rate limits (80 messages per second per number)
- Limited offline functionality
- Dependency on third-party data sources
- Regional language NLP model availability
- Budget constraints for AI model training and inference

## 12. Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Inaccurate disease diagnosis | High | Medium | Multi-model ensemble, confidence thresholds, expert review |
| Wrong price predictions | High | Medium | Conservative predictions, confidence intervals, disclaimers |
| Data source unavailability | High | Low | Multiple data sources, caching, graceful degradation |
| WhatsApp API changes | Medium | Low | Abstraction layer, multi-channel strategy |
| Low user adoption | High | Medium | User education, local language support, partnerships |
| Data privacy breach | High | Low | Strong security measures, compliance, audits |
| Scalability issues | Medium | Medium | Cloud-native architecture, load testing, monitoring |
| Model bias | Medium | Medium | Diverse training data, fairness testing, continuous monitoring |

## 13. Glossary

- **Mandi**: Agricultural market/marketplace
- **Quintal**: Unit of weight (100 kg)
- **Bigha**: Unit of land area (varies by region, ~0.25 acres)
- **KCC**: Kisan Credit Card
- **IMD**: India Meteorological Department
- **ICAR**: Indian Council of Agricultural Research
- **Agmarknet**: Government portal for mandi prices
- **Rabi**: Winter crop season
- **Kharif**: Monsoon crop season
- **Zaid**: Summer crop season
