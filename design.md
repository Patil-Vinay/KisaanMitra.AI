# KisaanMitra.AI - System Design Document

**Team**: KisaanMitra.AI

## Quick Reference

**Platform**: WhatsApp Business API  
**Language**: Hindi (MVP)  
**Cloud**: AWS (Mumbai primary, Hyderabad DR)  
**Cost**: ₹50/user/month  
**Performance**: <2s response, High ML accuracy

## 1. Architecture Overview

```
Farmer (WhatsApp) → Meta WhatsApp Business API
    ↓
AWS API Gateway (Auth, Rate Limit, Secure Entry)
    ↓
Lambda Orchestrator (Intent Detection + Agent Routing)
    ↓
┌─────────────┬──────────────┬─────────────┐
│ Crop Agent  │Finance Agent │Market Agent │
└─────────────┴──────────────┴─────────────┘
    ↓
ML + Knowledge Layer
├─ Crop DB, Pest Models (SageMaker), Soil API
├─ Budget Engine, Schemes (RDS), Credit Scoring
└─ Time-Series Forecasting (SageMaker), Mandi Prices (Timestream)
    ↓
Data Layer
├─ DynamoDB (Sessions, Prices)
├─ S3 Data Lake (Images, Models)
├─ Neptune (Knowledge Graph)
└─ OpenSearch (Vector DB for RAG)
    ↓
AWS Bedrock LLM (RAG + Multilingual Hindi)
```

## 2. Technology Stack

### Interface Layer
- **WhatsApp Business API**: Farmer-first conversational access
- **AWS Transcribe**: Voice input → text (Hindi)
- **Amazon S3**: Image upload & media storage

### Backend & Orchestration
- **FastAPI (Python)**: High-performance backend APIs
- **LangGraph + LangChain**: Multi-agent orchestration & RAG
- **AWS Lambda**: Serverless routing & automation
- **API Gateway**: Secure entry point & throttling

### AI & ML Layer
- **AWS Bedrock (Claude/Llama)**: LLM inference & generation
- **PyTorch / XGBoost**: Disease detection & forecasting
- **SageMaker**: ML model training & deployment
- **OpenSearch**: Vector DB for RAG retrieval

### Data & Storage
- **DynamoDB**: Farmer profiles & real-time data
- **Neptune**: Village-level Knowledge Graph
- **Timestream**: Mandi prices time-series
- **RDS PostgreSQL**: Schemes, budget data
- **Redis (ElastiCache)**: Session memory & caching
- **S3**: Agricultural Data Lake

### Deployment & Scale
- **Docker + ECS/EKS**: Containerized microservices
- **EventBridge**: Real-time alerts & event routing
- **GitHub Actions + CodePipeline**: CI/CD automation

## 3. Component Design

### 3.1 WhatsApp Integration
- **Webhook Handler** (Lambda): Validates signatures, extracts messages
- **Media Processor** (Lambda): Downloads images/audio → S3
- **Session Manager**: Redis-based (30-day TTL)
- **Performance**: <500ms cold start, <200ms processing

### 3.2 Orchestration Layer (ECS Fargate)
- **Intent Classifier**: IndicBERT fine-tuned for Hindi (95%+ accuracy)
- **Agent Router**: Routes to Crop/Finance/Market based on intent
- **Context Manager**: DynamoDB conversation state
- **Scaling**: 2-20 tasks, auto-scale on CPU >70%

### 3.3 Crop Agent (ECS Fargate)
**Disease Detection**:
- Model: EfficientNet-B4 (PyTorch)
- Accuracy: 90%+ on 50+ diseases
- Inference: <3s on SageMaker ml.g4dn.xlarge (GPU)

**Knowledge Graph** (Neptune):
- 600K villages → crops → varieties → practices
- Query time: <100ms (3-hop queries)

**Recommendations**:
- Hybrid: Rule-based + collaborative filtering
- Features: Crop, stage, soil, weather, farmer history

### 3.4 Finance Agent (ECS Fargate)
**Budget Planning**:
- Calculation: Seeds + Fertilizers + Pesticides + Labor + Irrigation + 15% buffer
- ROI: (Revenue - Cost) / Cost × 100
- Performance: <200ms

**Scheme Matching** (RDS PostgreSQL):
- 500+ schemes (central + state)
- AI matching: 90%+ accuracy
- Full-text search: <100ms

**Price Comparison** (DynamoDB):
- 10+ sources (e-commerce, vendors, cooperatives)
- Cache: Redis (1-hour TTL)
- Performance: <50ms (cached)

### 3.5 Market Agent (ECS Fargate)
**Price Forecasting** (SageMaker):
- Models: LSTM + Prophet ensemble
- Training: 5 years mandi data (3000+ mandis)
- Accuracy: 85%+ (MAPE <15%)
- Inference: <2s on ml.m5.xlarge

**Mandi Tracking** (Timestream):
- 3000+ mandis, daily updates (6 PM IST)
- Query: <20ms (latest), <200ms (comparison)

**Crop Recommendation**:
- Multi-criteria: ROI (40%), Risk (30%), Water (20%), Experience (10%)
- Performance: <500ms

## 4. Data Layer

| Database | Purpose | Instance | Performance |
|----------|---------|----------|-------------|
| **RDS PostgreSQL** | User data, schemes | db.r5.large Multi-AZ | <100ms queries |
| **DynamoDB** | Sessions, prices | On-demand | <10ms reads |
| **Neptune** | Knowledge graph | db.r5.large | <100ms (3-hop) |
| **Timestream** | Mandi prices | Magnetic store | <200ms queries |
| **ElastiCache Redis** | Cache | cache.r6g.large | <1ms |
| **OpenSearch** | Scheme search | 3-node cluster | <100ms |

## 5. ML Models

| Model | Purpose | Framework | Accuracy | Inference |
|-------|---------|-----------|----------|-----------|
| **Disease Detection** | Crop disease ID | PyTorch (EfficientNet-B4) | 95%+ | <3s |
| **Price Forecasting** | Mandi price prediction | LSTM + Prophet | 85%+ | <2s |
| **Intent Classification** | User intent | IndicBERT (Hindi) | 95%+ | <100ms |
| **Voice Transcription** | Speech-to-text | AWS Transcribe | 90%+ | Real-time |

## 6. Infrastructure

### Compute
- **ECS Fargate**: 2-20 tasks (2 vCPU, 4GB each)
- **Lambda**: 1000 concurrent executions
- **SageMaker**: ml.g4dn.xlarge (disease), ml.m5.xlarge (price)

### Security
- **Encryption**: TLS 1.3 (transit), AES-256 (rest)
- **WAF + Shield**: DDoS protection
- **KMS**: Key management
- **Secrets Manager**: API keys, credentials

### Monitoring
- **CloudWatch**: Logs, metrics, alarms
- **X-Ray**: Distributed tracing
- **EventBridge**: Scheduled tasks, alerts

### High Availability
- **Multi-AZ**: All databases, ECS tasks
- **Auto-Scaling**: CPU >70% triggers scale-out
- **DR**: Hyderabad region (RTO: 4h, RPO: 1h)

## 7. Cost Breakdown (100K Users)

| Category | Monthly Cost | % |
|----------|-------------|---|
| Compute (ECS + Lambda) | $700 | 9.7% |
| ML (SageMaker) | $1,500 | 20.7% |
| Databases | $1,700 | 23.5% |
| Storage (S3) | $230 | 3.2% |
| Network | $700 | 9.7% |
| WhatsApp API | $2,000 | 27.7% |
| Other | $400 | 5.5% |
| **Total** | **$7,230** | **100%** |

**Cost per User**: $0.07/month (₹5.8/month)

### Cost Optimization
- Spot instances: 50% savings on batch jobs
- Reserved instances: 40% savings on baseline
- S3 lifecycle: 30% savings (Standard → IA → Glacier)
- Model optimization: 50% savings (quantization)
- Caching: 80% cache hit rate reduces DB load 5x

## 8. Deployment Strategy

### CI/CD Pipeline
```
Git Push → CodePipeline
    ↓
CodeBuild (Test + Build + Security Scan)
    ↓
Deploy to Staging → Integration Tests
    ↓
Manual Approval
    ↓
Blue-Green Deployment to Production
    ↓
Health Checks → Auto-Rollback if errors >1%
```

### Rollout
- **Canary**: 5% → 25% → 50% → 100% (1 hour between)
- **Feature Flags**: LaunchDarkly for gradual rollout
- **Rollback**: Automated <5 min if error rate >1%

## 9. Security & Compliance

- **Data Residency**: All data in India (Mumbai/Hyderabad)
- **Compliance**: DPDP Act 2023, ISO 27001 (target)
- **Access Control**: RBAC with audit logging
- **Backup**: Every 6 hours, 30-day retention
- **DR**: RTO 4 hours, RPO 1 hour

## 10. Scalability

| Metric | Current | Target (Year 3) |
|--------|---------|-----------------|
| Users | 100K | 10M |
| Concurrent Users | 100K | 1M |
| Messages/Day | 10M | 100M |
| Response Time | <2s (p95) | <2s (p95) |
| Uptime | 99.9% | 99.9% |

## 11. Architecture Diagrams

6 professional AWS diagrams in `generated-diagrams/`:
1. **Production Architecture**: Complete AWS infrastructure
2. **ML/AI Pipeline**: Training and inference workflow
3. **Complete System Overview**: High-level with metrics
4. **Detailed Data Flow**: Component interactions
5. **Cost Optimization**: Savings strategies
6. **Simplified Architecture**: Overview

---

**Status**: Production-Ready  
**Built on**: AWS · Open-Source AI Stack · Scalable for 100M+ Farmers
