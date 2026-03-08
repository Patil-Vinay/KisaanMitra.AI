# KisaanMitra.AI 🌾

[![AWS](https://img.shields.io/badge/AWS-Serverless-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://www.python.org/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Business_API-25D366?logo=whatsapp)](https://business.whatsapp.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Team**: KisaanMitra.AI  
**Problem Statement**: AI for Rural Innovation & Sustainable Systems

> WhatsApp-based Multi-Agent AI System - From "Hi" to Profit in the Bank

---

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

### AWS Services (Core Infrastructure)
**Compute**: AWS Lambda (Serverless, Python 3.14, 1536MB)  
**Database**: Amazon DynamoDB (5 tables, pay-per-request)  
**Storage**: Amazon S3 (Images, data lake)  
**AI/ML**: Amazon Bedrock (Nova Pro), Claude Sonnet 4  
**Security**: AWS Secrets Manager, IAM  
**Monitoring**: Amazon CloudWatch (Logs, Metrics, Alarms)  
**Planned**: API Gateway, CloudFront, Route 53

### AI Models
**Primary**: Amazon Nova Pro (fast routing, entity extraction)  
**Secondary**: Claude Sonnet 4 (complex reasoning, budget planning)  
**Specialized**: Kindwise API (crop disease detection, 85%+ accuracy)

### External APIs
**Interface**: WhatsApp Business API (Meta)  
**Weather**: OpenWeather API (7-day forecasts)  
**Market**: AgMarkNet API (Government of India mandi prices)  

## 📊 Expected Impact

| Metric | Target | Description |
|--------|--------|-------------|
| 💰 Farmer Income | **+20-30%** | Better market timing and crop selection |
| 🌾 Crop Loss Reduction | **-40%** | Early disease detection and prevention |
| 💵 Input Cost Savings | **-15-20%** | Optimized fertilizer and pesticide usage |
| 📈 Better Market Prices | **+25%** | Demand forecasting and optimal harvest timing |

---

## 💰 Cost & Revenue

### Pilot Cost (1 Village)
**₹47,000-74,000** (setup + 1 month operation)

| Component | Cost |
|-----------|------|
| Tech Infrastructure | ₹6-17K/month |
| Village Data Agent | ₹10-12K/month |
| Data Collection | ₹28-40K (one-time) |

### Revenue Model
1. **Data-as-a-Service (DaaS)** - Agri-input companies, insurers
2. **Sponsored Recommendations** - Pay-per-lead model
3. **B2B SaaS Licensing** - FPOs, KVKs, agri-dealers
4. **Advisory & Referral Network** - Mandis, banks

**Why It Works**: Village-level agricultural data doesn't exist in India. Every interaction creates a data moat that competitors can't replicate.

---

## 🤖 Why AI is Essential

### 1. Natural Language Understanding
Farmers communicate in mixed Hindi-English with varying literacy levels. AI (Amazon Nova Pro + Claude) processes unstructured queries, extracts intent, and responds naturally - impossible with rule-based systems.

### 2. Intelligent Routing
Multi-domain queries require AI to analyze complexity and route to specialized agents (Crop/Market/Finance/General) while maintaining context.

### 3. Visual Disease Detection
Computer vision identifies crop diseases from images with 85%+ accuracy - replacing expensive expert consultations.

### 4. Personalized Recommendations
AI synthesizes user profile (village, crops, land, soil) + real-time data (weather, prices, disease outbreaks) for contextual advice.

### 5. Financial Planning
Complex budget calculations considering multiple variables (crop type, land size, input costs, yields, market prices, loans, subsidies) require AI reasoning.

### 6. Market Intelligence
Time-series analysis and demand forecasting predict optimal harvest timing and selling strategies.

**Value**: 40% crop loss reduction, 20-30% income increase, 15-20% cost savings

## ☁️ AWS Architecture Highlights

### Serverless-First Design
- **AWS Lambda**: Auto-scaling compute (1000+ concurrent executions)
- **DynamoDB**: Unlimited scalability, single-digit ms latency
- **S3**: Unlimited storage with lifecycle policies
- **Cost**: 85% cheaper than traditional EC2+RDS ($29 vs $200/month for 1K users)

### Multi-Model AI Strategy
- **Amazon Nova Pro**: Fast queries (1-2s), $0.00008/1K tokens
- **Claude Sonnet 4**: Complex analysis (3-5s), high accuracy
- **Right model for right task**: Optimal cost-performance

### Security & Compliance
- **IAM**: Least-privilege access control
- **Secrets Manager**: Encrypted credential storage
- **CloudWatch**: Real-time monitoring and alerting
- **Encryption**: At rest (DynamoDB, S3) and in transit (HTTPS)

### Scalability
- **Current**: 300K requests/month, 1K users
- **Tested**: 1M requests/month, 10K users
- **Capacity**: 10M+ requests/month without redesign
- **Performance**: <3s text queries, <7s image analysis, 99.9% uptime  

## 👥 Team

- **Aditya Rane** - Project Manager, Agile Delivery Strategy
- **Vinay Patil** - Lead Engineer, Backend AI Systems, Cloud Architecture
- **Parth Nikam** - Advanced Analytics, Data Science, Agentic AI

---


## 🌐 Live Demos

### 🎮 Interactive Demos
- **[Web Chat Demo](http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com/)** - Try the AI assistant in your browser
- **[Knowledge Graph Dashboard](http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com/)** - Live visualization of 10,007 farmers across 191 villages
- **[Knowledge Graph (Alternative)](http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com/knowledge-graph.html)** - Interactive network visualization

### 🎥 Video Demo
- **[YouTube Demo](https://youtu.be/HGGA7kz9L8U)** - Complete system walkthrough

### 💻 Source Code
- **[GitHub Repository](https://github.com/parth-nikam/KisaanMitra.AI)** - Full source code and documentation

---

## 📚 Documentation

### 📋 Submission Documents
- **[AWS AI Submission Guide](AWS_AI_SUBMISSION_GUIDE.md)** - Complete explanation of AI requirements and AWS services
- **[AWS Architecture Visual](AWS_ARCHITECTURE_VISUAL.md)** - Detailed architecture diagrams and data flows
- **[Submission Package](SUBMISSION_PACKAGE.md)** - Hackathon submission checklist
- **[Submission Ready](SUBMISSION_READY.md)** - Final submission status

### 🔧 Technical Documentation
- **[Architecture](ARCHITECTURE.md)** - System architecture and AWS infrastructure
- **[Requirements](requirements.md)** - Functional requirements and success metrics
- **[Design](design.md)** - System design and AWS services
- **[Quick Reference](QUICK_REFERENCE.md)** - Quick start guide
- **[Features List](FEATURES_LIST.md)** - Complete feature documentation
- **[Sample Commands](SAMPLE_COMMANDS.md)** - Usage examples

### 🚀 Implementation Guides
- **[Disease Alert System](DISEASE_ALERT_SYSTEM.md)** - Hyperlocal disease tracking
- **[Hyperlocal Alert Demo](HYPERLOCAL_ALERT_DEMO.md)** - Alert system demonstration

### 📐 Architecture Diagrams
6 professional AWS diagrams in `generated-diagrams/`:
1. Production Architecture
2. ML/AI Pipeline
3. Complete System Overview
4. Detailed Data Flow
5. Cost Optimization
6. Simplified Architecture

---

## 📐 Repository Structure

```
KisaanMitra.AI/
├── src/
│   ├── lambda/              # AWS Lambda functions
│   │   ├── agents/          # Specialized AI agents
│   │   └── services/        # Core services
│   ├── crop_agent/          # Crop health API client
│   ├── hyperlocal/          # Disease tracking system
│   └── onboarding/          # Farmer onboarding
├── docs/                    # Documentation
├── tests/                   # Test suites
├── infrastructure/          # AWS setup scripts
├── demo/                    # Demo applications
├── dashboard/               # Analytics dashboard
├── generated-diagrams/      # Architecture diagrams
└── archive/                 # Historical logs and scripts

```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete details.

---

## 🏆 Tagline

**"The AI is the interface. The data is the moat."**

*Building India's first village-level agricultural data infrastructure*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by Team KisaanMitra.AI
