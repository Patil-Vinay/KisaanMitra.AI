# KisaanMitra.AI 🌾

**Team**: KisaanMitra.AI  
**Problem Statement**: AI for Rural Innovation & Sustainable Systems

> WhatsApp-based Multi-Agent AI System - From "Hi" to Profit in the Bank

## 🎯 The Problem

Farmers lack timely, hyper-local, integrated decision support across crop management, financial planning, and market intelligence. Existing information is fragmented, non-personalized, and difficult to apply at village level.

## 💡 Our Solution

KisaanMitra.AI is a **WhatsApp-based multi-agent AI system** - a farmer's all-in-one intelligent assistant.

### 🤖 Three Specialized AI Agents

**🌱 Crop Agent**
- Hyper-local crop guidance (village-level knowledge graph)
- Disease diagnosis (image + text, 95%+ accuracy)
- Fertilizer & pesticide recommendations
- Weather-aware suggestions

**💰 Finance Agent**
- End-to-end budget planning
- Government scheme discovery + eligibility matching
- Lowest price inputs (fertilizer/pesticide comparison)
- Loan & subsidy planning, risk estimation

**📈 Market Agent**
- Demand trends & time-series forecasting
- Best crop to grow recommendations
- Optimal harvest timing
- Nearby mandi price trends, supply vs demand signals

### ✨ Key Features
- **WhatsApp Native**: No app download, works on basic smartphones
- **Local Language**: Hindi (MVP), voice + text support
- **Image Support**: Disease detection from crop photos
- **Real-Time**: <2s response time, 99.9% uptime

## 🏗️ Architecture

```
Farmer (WhatsApp) → Meta WhatsApp Business API
    ↓
AWS API Gateway (Auth, Rate Limit)
    ↓
Lambda Orchestrator (Intent Detection + Agent Routing)
    ↓
┌─────────────┬──────────────┬─────────────┐
│ Crop Agent  │Finance Agent │Market Agent │
└─────────────┴──────────────┴─────────────┘
    ↓
ML + Knowledge Layer
├─ Crop DB, Pest Models, Soil API
├─ Budget Engine, Schemes, Credit Scoring
└─ Time-Series Forecasting (ARIMA, Mandi Prices)
    ↓
Data Layer: DynamoDB | S3 | Neptune | OpenSearch
    ↓
AWS Bedrock LLM (RAG + Multilingual)
```

## 🚀 Technology Stack

**Interface**: WhatsApp Business API, AWS Transcribe (voice)  
**Backend**: FastAPI (Python), LangGraph + LangChain (multi-agent)  
**AI/ML**: AWS Bedrock (Claude/Llama), PyTorch, XGBoost, SageMaker  
**Data**: S3 (Data Lake), DynamoDB, Neptune (Knowledge Graph), OpenSearch (Vector DB)  
**Deployment**: Docker + ECS/EKS, Lambda, API Gateway, EventBridge  

## 📊 Expected Impact

| Metric | Target |
|--------|--------|
| Farmer Income | +20-30% |
| Crop Loss Reduction | -40% |
| Input Cost Savings | -15-20% |
| Better Market Prices | +25% |

## � Cost & Revenue

**1 Village Pilot Cost**: ₹1.5-2.5 Lakhs (setup + 3 months)
- Tech Infrastructure: ₹6-17K/month
- Village Data Agent: ₹10-12K/month
- Data Collection: One-time setup

**Revenue Model**:
- Data-as-a-Service (DaaS): Agri-input companies, insurers
- Sponsored Recommendations: Pay-per-lead
- B2B SaaS Licensing: FPOs, KVKs, agri-dealers
- Advisory & Referral Network: Mandis, banks

**Why It Works**: Village-level agricultural data doesn't exist in India. Every interaction creates a data moat that competitors can't replicate.

## 🛣️ Farmer Journey

```
Onboarding → Pre-Planting → Growing → Harvest → Selling
    ↓            ↓            ↓          ↓         ↓
  "Hi"    "Kaunsi fasal   Disease   "Kab      Market
          lagau?"         Diagnosis  harvest   Intelligence
                                     karu?"    + ROI
```

**Complete cycle**: From "Hi" on WhatsApp to profit in bank, powered by 3 AI agents

## 🏆 Why We're Unique

✅ **Multi-Agent System**: Holistic support across full agricultural lifecycle  
✅ **Hyper-Local**: Village-level knowledge graph (600K villages)  
✅ **WhatsApp Native**: 500M+ users, zero friction  
✅ **Voice-First**: Accessibility for low-literacy farmers  
✅ **Data Moat**: Every interaction generates irreplaceable hyper-local data  

## 👥 Team

- **Aditya Rane**: Project Manager, Agile Delivery Strategy
- **Vinay Patil**: Lead Engineer, Backend AI Systems, Cloud
- **Parth Nikam**: Advanced Analytics, Data Science, Agentic AI

## � Documenntation

- **[Requirements](requirements.md)**: Functional requirements and success metrics
- **[Design](design.md)**: System architecture and AWS infrastructure
- **[Technical Specs](TECHNICAL_SPECS.md)**: Detailed specifications
- **[Pitch Deck](HACKATHON_PITCH.md)**: Hackathon presentation

## 📐 Architecture Diagrams

6 professional AWS diagrams in `generated-diagrams/`:
1. Production Architecture
2. ML/AI Pipeline
3. Complete System Overview
4. Detailed Data Flow
5. Cost Optimization
6. Simplified Architecture

---

**"The AI is the interface. The data is the moat."**

*Building India's first village-level agricultural data infrastructure*
