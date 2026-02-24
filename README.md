# KisaanMitra.AI 🌾

**Team**: KisaanMitra.AI  
**Problem Statement**: AI for Rural Innovation & Sustainable Systems

> WhatsApp-based Multi-Agent AI System - From "Hi" to Profit in the Bank

## 🎯 The Problem

Farmers lack timely, hyper-local, integrated decision support across crop management, financial planning and market intelligence. Existing information is fragmented, non-personalized and difficult to apply at village level.

## 💡 Our Solution

KisaanMitra.AI is a **WhatsApp-based multi-agent AI system** - a farmer's all-in-one intelligent assistant.

### 🤖 Three Specialized AI Agents

**🌱 Crop Agent**
- Village-level knowledge graph
- Disease diagnosis (image + text, high accuracy)
- Fertilizer & pesticide recommendations
- Weather-aware suggestions

**📈 Market Agent**
- Demand trends & time-series forecasting
- Best crop to grow recommendations
- Optimal harvest timing
- Nearby farmer's market (mandi) price trends, supply vs demand signals

**💰 Finance Agent**
- End-to-end budget planning
- Government scheme discovery + eligibility matching
- Lowest price inputs (fertilizer/pesticide comparison)
- Loan & subsidy planning, risk estimation

### ✨ Key Features
- **WhatsApp Native**: No app download, works on basic smartphones
- **Local Language**: Hindi (USP), voice + text support
- **Image Support**: Disease detection from crop photos
- **Real-Time**: Instant response, high availability

## 🏗️ Architecture

```
Farmer (WhatsApp) → Meta WhatsApp Business API
    ↓
AWS API Gateway (Auth, Rate Limit)
    ↓
Lambda Orchestrator (Intent Detection + Agent Routing)
    ↓
┌─────────────┬─────────────┬──────────────┐
│ Crop Agent  │Market Agent │Finance Agent │
└─────────────┴─────────────┴──────────────┘
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

**1 Village Pilot Cost**: ₹47,000-74,000 Lakhs (setup + 1 month cost)
- Tech Infrastructure: ₹6-17K/month
- Village Data Agent: ₹10-12K/month
- Data Collection: One-time setup (₹28-40K)

**Revenue Model**:
- Data-as-a-Service (DaaS): Agri-input companies, insurers
- Sponsored Recommendations: Pay-per-lead
- B2B SaaS Licensing: FPOs, KVKs, agri-dealers
- Advisory & Referral Network: Farmer's Market(Mandis), banks

**Why It Works**: Village-level agricultural data doesn't exist in India. Every interaction creates a data moat that competitors can't replicate.

**Complete cycle**: From "Hi" on WhatsApp to profit in bank, powered by 3 AI agents

## 🏆 Why We're Unique

✅ **Multi-Agent System**: Holistic support across full agricultural lifecycle  
✅ **Hyper-Local**: Village-level knowledge graph
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


## 📚 Documentation

- **[Requirements](requirements.md)**: Functional requirements and success metrics
- **[Design](design.md)**: System architecture and AWS infrastructure
- **[Project Structure](PROJECT_STRUCTURE.md)**: Repository organization
- **[Lambda Setup](docs/LAMBDA_SETUP.md)**: AWS Lambda deployment guide
- **[Quick Start](docs/QUICK_START_LAMBDA.md)**: 5-minute Lambda deployment

## 📐 Repository Structure

```
src/
├── crop_agent/          # Crop Health API client
└── lambda/              # AWS Lambda functions

docs/                    # Documentation
assets/
├── diagrams/            # 6 AWS architecture diagrams
└── test_images/         # Sample test images
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete details.
