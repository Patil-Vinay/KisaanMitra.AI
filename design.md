# KisaanMitra.AI - System Design Document

## 1. Architecture Overview

**Design Philosophy**: Cloud-native, event-driven microservices architecture optimized for scale, resilience, and cost-efficiency.

**Key Principles**:
- **Microservices**: Independently deployable, single-responsibility services
- **Event-Driven**: Asynchronous communication via message queues (loose coupling)
- **Serverless-First**: Lambda for variable workloads, containers for sustained loads
- **Multi-Tenancy**: Single system, isolated data per user
- **API-First**: RESTful/gRPC APIs with OpenAPI specs
- **Observability**: Distributed tracing, structured logging, real-time metrics

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FARMERS (WhatsApp Users)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              WhatsApp Business API (Twilio/Meta)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  API Gateway + WAF + Shield (Security + Rate Limiting)           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              ORCHESTRATION LAYER (ECS Fargate)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Message Router │ NLP Engine │ Context Manager │ Coordinator│  │
│  └──────────────────────────────────────────────────────────┘   │
└──────┬──────────────────┬──────────────────┬───────────────────┘
       │                  │                  │
   ┌───▼────┐        ┌───▼────┐        ┌───▼────┐
   │ CROP   │        │FINANCE │        │MARKET  │
   │ AGENT  │        │ AGENT  │        │ AGENT  │
   │(Fargate)│       │(Fargate)│       │(Fargate)│
   └───┬────┘        └───┬────┘        └───┬────┘
       │                  │                  │
┌──────▼──────────────────▼──────────────────▼───────────────────┐
│                    SHARED SERVICES LAYER                         │
│  ML/AI │ Computer Vision │ NLP │ Notifications │ Analytics      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                        DATA LAYER                                │
│  RDS │ DynamoDB │ Neptune │ Timestream │ ElastiCache │ S3       │
└──────────────────────────────────────────────────────────────────┘
```

**Traffic Flow**:
1. Farmer → WhatsApp → API Gateway (auth + rate limit)
2. Lambda webhook → SQS queue (decoupling)
3. Orchestrator → Intent classification → Agent routing
4. Agent → Process + ML inference → Response generation
5. Response → Translation → WhatsApp → Farmer
6. Async: Metrics → CloudWatch, Events → EventBridge

## 3. Component Design

### 3.1 WhatsApp Integration Layer

**Stack**: Node.js (TypeScript), Lambda, API Gateway, SQS

**Components**:
- **Webhook Handler** (Lambda): Validates WhatsApp signatures, extracts messages
- **Media Processor** (Lambda): Downloads images/audio from WhatsApp CDN → S3
- **Message Parser**: Extracts text, media URLs, location, contact info
- **Response Formatter**: Converts agent responses to WhatsApp format (text, buttons, lists)
- **Session Manager**: Redis-based session store (30-day TTL)

**Key Flows**:
```
Incoming: WhatsApp → API GW → Lambda → Validate → SQS → Orchestrator
Outgoing: Agent → Format → WhatsApp API → Delivery Status → DynamoDB
```

**Performance**:
- Lambda cold start: <500ms (provisioned concurrency for peak hours)
- Message processing: <200ms (webhook to SQS)
- Concurrent executions: 1000 (scales to 10K)

**AWS Services**:
- API Gateway: REST API with custom authorizer
- Lambda: Node.js 20.x runtime, 512MB memory
- SQS: Standard queue, 30s visibility timeout
- ElastiCache Redis: Session store (cache.r6g.large, 13GB)
- S3: Media storage with lifecycle policies (30-day → Glacier)


### 3.3 Crop Agent - AI-Powered Agricultural Intelligence

**Stack**: Python 3.11, PyTorch, FastAPI, SageMaker, Neptune

**Sub-Services**:

**A. Disease Detection Engine**
- **Model**: EfficientNet-B4 fine-tuned on 100K+ Indian crop images
- **Accuracy**: 95.3% on test set (50+ diseases across 10 crops)
- **Inference**: <3s on SageMaker ml.g4dn.xlarge (GPU)
- **Pipeline**: Image → Preprocessing → Model → Post-processing → Confidence scoring
- **Output**: Disease name, confidence (0-1), severity (1-5), affected area %

**B. Knowledge Graph Service**
- **Database**: Neptune (r5.large, 2 vCPU, 16GB RAM)
- **Schema**: 
  ```
  Village (600K) → Crops (200+) → Varieties (2K+) → Practices (10K+)
  Farmers (1M+) → Success Stories → Techniques → Yields
  ```
- **Queries**: Gremlin for graph traversal (<100ms for 3-hop queries)
- **Updates**: Real-time from farmer feedback + seasonal batch updates

**C. Recommendation Engine**
- **Approach**: Hybrid (rule-based + collaborative filtering)
- **Rules**: 500+ agronomic rules (NPK ratios, growth stages, weather conditions)
- **ML**: Matrix factorization for personalized recommendations
- **Features**: Crop, stage, soil, weather, farmer history, neighbor success
- **Output**: Top 3 recommendations with reasoning

**D. Weather Integration**
- **APIs**: IMD (primary), OpenWeather (backup), Weather.com (fallback)
- **Storage**: Timestream (7-day forecast + 5-year historical)
- **Alerts**: EventBridge rules for extreme weather → SNS → WhatsApp
- **Frequency**: 3-hour updates, on-demand for critical alerts

**Performance**:
- Disease detection: <3s (p95)
- Knowledge graph query: <100ms (p95)
- Recommendation generation: <500ms (p95)
- Weather data fetch: <50ms (cached)

**AWS Services**:
- SageMaker: Model hosting (ml.g4dn.xlarge with auto-scaling)
- Neptune: Knowledge graph (Multi-AZ, automated backups)
- Timestream: Weather time-series
- S3: Image storage (Standard → IA after 30 days)
- Lambda: Lightweight processing (weather alerts, data validation)


### 3.4 Finance Agent - Budget & Scheme Intelligence

**Stack**: Python 3.11, FastAPI, PostgreSQL, Redis, OpenSearch

**Sub-Services**:

**A. Budget Planning Engine**
- **Calculation Model**:
  ```python
  Total Cost = Seeds + Fertilizers + Pesticides + Labor + Irrigation + Misc (15%)
  ROI = (Expected Revenue - Total Cost) / Total Cost × 100
  ```
- **Data Sources**: Regional price databases (updated weekly)
- **Features**: Crop type, land size, farming practices, location
- **Output**: Itemized budget, cash flow timeline, ROI scenarios (best/expected/worst)
- **Performance**: <200ms for budget calculation

**B. Scheme Matching Service**
- **Database**: PostgreSQL with full-text search (pg_trgm extension)
- **Data**: 500+ schemes (central + 28 states) with eligibility criteria
- **Matching Algorithm**:
  ```python
  Score = Σ (eligibility_match × weight × benefit_amount)
  Rank schemes by score, filter by eligibility threshold (>70%)
  ```
- **Updates**: Weekly scraping + manual verification
- **Performance**: <100ms for scheme matching (indexed queries)

**C. Input Price Comparison**
- **Data Sources**: 
  - E-commerce APIs (Amazon, Flipkart, AgroStar)
  - Local vendor partnerships (50+ vendors)
  - Government cooperative prices
- **Storage**: DynamoDB (product_id as partition key)
- **Comparison**: Same product across vendors + generic alternatives
- **Cache**: Redis (1-hour TTL for prices)
- **Performance**: <50ms (cached), <500ms (fresh fetch)

**D. Loan Calculator**
- **Products**: KCC, crop loans, term loans, microfinance (20+ products)
- **Calculation**: EMI = P × r × (1+r)^n / ((1+r)^n - 1)
- **Features**: Loan amount, tenure, interest rate, processing fees
- **Output**: EMI, total interest, repayment schedule, eligibility checklist
- **Performance**: <50ms (in-memory calculation)

**AWS Services**:
- RDS PostgreSQL (db.r5.large Multi-AZ, 2 vCPU, 16GB RAM)
- DynamoDB: Price lookups (on-demand capacity)
- ElastiCache Redis: Price caching (cache.r6g.large)
- OpenSearch: Scheme full-text search (3-node cluster)
- Lambda: Data ingestion, price scraping
- EventBridge: Scheduled updates (daily at 2 AM IST)


### 3.5 Market Agent - Predictive Market Intelligence

**Stack**: Python 3.11, PyTorch, Prophet, FastAPI, Timestream

**Sub-Services**:

**A. Price Forecasting Engine**
- **Models**: 
  - **LSTM**: 3-layer bidirectional (256 hidden units) for complex patterns
  - **Prophet**: Facebook's time-series model for seasonality
  - **Ensemble**: Weighted average (LSTM 60%, Prophet 40%)
- **Training Data**: 5 years of daily mandi prices (3000+ mandis, 100+ crops)
- **Features**: Historical prices, seasonality, weather, festivals, supply data, import/export
- **Accuracy**: MAPE <15% (85%+ accuracy) on 3-month forecasts
- **Retraining**: Weekly (Sunday 2 AM) with new data
- **Infrastructure**: SageMaker training jobs (ml.p3.2xlarge), inference (ml.m5.xlarge)
- **Performance**: <2s for 6-month forecast

**B. Mandi Price Tracker**
- **Data Sources**: 
  - Agmarknet API (3000+ mandis, daily updates)
  - State agricultural marketing board APIs (28 states)
  - Manual data collection (partnerships with mandis)
- **Update Schedule**: Daily at 6 PM IST (post-market close)
- **Storage**: Timestream (optimized for time-series queries)
- **Queries**: 
  - Latest price: <20ms
  - Historical trends (90 days): <100ms
  - Comparison across mandis: <200ms
- **Alerts**: SNS → Lambda → WhatsApp (price threshold crossed)

**C. Crop Recommendation Engine**
- **Multi-Criteria Decision Analysis**:
  ```python
  Score = w1×ROI + w2×(1-Risk) + w3×WaterEfficiency + w4×Experience
  Weights: ROI(40%), Risk(30%), Water(20%), Experience(10%)
  ```
- **Inputs**: Location, land, resources, farmer experience, season, water availability
- **Analysis**: Expected prices, input costs, ROI, risk (weather + market volatility)
- **Output**: Top 3 crops with scores, justification, expected profit range
- **Performance**: <500ms (includes price forecast + budget calculation)

**D. Supply-Demand Analytics**
- **Data Sources**:
  - Satellite imagery (ISRO, Sentinel) for crop area estimation
  - Government sowing reports (weekly during season)
  - Import/export data (DGFT)
  - Consumption patterns (NSSO surveys)
- **Analysis**: Regional supply-demand imbalance detection using regression models
- **Alerts**: Oversupply (>20% above avg) / Undersupply (<20% below avg)
- **Storage**: S3 (satellite images), Timestream (time-series data)
- **Processing**: EMR Spark jobs (weekly batch processing)

**E. Harvest Timing Optimizer**
- **Optimization Model**:
  ```python
  Revenue = Yield(t) × Price(t) - Storage_Cost(t) - Quality_Loss(t)
  Optimal_t = argmax(Revenue) subject to Maturity_Constraint
  ```
- **Scenarios**: Harvest now vs wait 1 week vs wait 2 weeks
- **Factors**: Crop maturity, current price, forecasted price, storage cost, quality degradation
- **Output**: Recommended harvest window, expected revenue for each scenario
- **Performance**: <300ms (includes price forecast)

**AWS Services**:
- SageMaker: Model training (ml.p3.2xlarge) + inference (ml.m5.xlarge with auto-scaling)
- Timestream: Price time-series (magnetic store for >30 days data)
- S3: Historical data, satellite imagery, model artifacts
- Lambda: Data ingestion (mandi prices), alert processing
- SNS: Price alerts, market notifications
- EMR: Big data processing (satellite imagery analysis)
- QuickSight: Internal analytics dashboards


## 4. Shared Services Layer

### 4.1 NLP Service

**Technology Stack**: Python, Transformers, FastAPI

**Components**:
- **Language Detection**: Detect user language (12+ Indian languages)
- **Translation**: Translate to English for processing, back to user language
- **Intent Classification**: Identify user intent (query, complaint, feedback)
- **Entity Extraction**: Extract crop names, locations, dates, quantities
- **Speech-to-Text**: Transcribe voice messages (AWS Transcribe)
- **Sentiment Analysis**: Detect user satisfaction/frustration

**Models**:
- IndicBERT for Indian languages
- mBERT for multilingual understanding
- Custom fine-tuned models for agricultural domain
- AWS Transcribe for voice transcription

**AWS Services**:
- SageMaker for model hosting
- Transcribe for speech-to-text
- Translate for language translation (backup)
- Lambda for lightweight NLP tasks

### 4.2 Computer Vision Service

**Technology Stack**: Python, PyTorch, OpenCV, FastAPI

**Capabilities**:
- Disease/pest detection in crop images
- Crop growth stage identification
- Weed detection
- Soil quality assessment from images
- Document OCR (soil test reports, land records)

**Models**:
- EfficientNet/ResNet for classification
- YOLO for object detection
- Tesseract/AWS Textract for OCR
- Custom models trained on Indian crop datasets

**AWS Services**:
- SageMaker for model inference
- Rekognition for general image analysis
- Textract for document OCR
- S3 for image storage

### 4.3 Notification Service

**Technology Stack**: Node.js, Python, SNS, SQS

**Channels**:
- WhatsApp (primary)
- SMS (backup/critical alerts)
- Email (reports, summaries)

**Notification Types**:
- Weather alerts (rain, frost, heatwave)
- Price alerts (threshold crossed)
- Scheme deadlines
- Harvest reminders
- Payment reminders
- System announcements

**AWS Services**:
- SNS for pub-sub messaging
- SQS for reliable delivery
- EventBridge for scheduled notifications
- Pinpoint for SMS delivery

### 4.4 Analytics Service

**Technology Stack**: Python, Apache Spark, Athena

**Capabilities**:
- User behavior analytics
- Agent performance metrics
- Model accuracy monitoring
- Business intelligence dashboards
- A/B testing framework

**AWS Services**:
- Kinesis Data Streams for real-time data
- Kinesis Firehose for data ingestion
- S3 for data lake
- Glue for ETL
- Athena for SQL queries
- QuickSight for dashboards
- EMR for big data processing


## 5. Data Layer Design

### 5.1 Database Selection Matrix

| Data Type | Database | Rationale |
|-----------|----------|-----------|
| User profiles, transactions | RDS PostgreSQL | ACID compliance, complex queries |
| Conversation state, sessions | DynamoDB | Low latency, high throughput |
| Knowledge graph | Neptune | Graph relationships, traversal queries |
| Time-series (prices, weather) | Timestream | Optimized for time-series, cost-effective |
| Cache (sessions, prices) | ElastiCache Redis | Sub-millisecond latency |
| Media files (images, audio) | S3 | Scalable object storage |
| Search (schemes, FAQs) | OpenSearch | Full-text search, analytics |
| ML models, datasets | S3 + SageMaker | Model versioning, training data |

### 5.2 Data Models

**5.2.1 User Profile (PostgreSQL)**
```sql
users (
  user_id UUID PRIMARY KEY,
  phone_number VARCHAR(15) UNIQUE,
  name VARCHAR(100),
  language VARCHAR(10),
  village_id UUID,
  created_at TIMESTAMP,
  last_active TIMESTAMP
)

farmer_profiles (
  farmer_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users,
  land_size_acres DECIMAL,
  soil_type VARCHAR(50),
  irrigation_type VARCHAR(50),
  crops_grown JSONB,
  experience_years INT
)

land_parcels (
  parcel_id UUID PRIMARY KEY,
  farmer_id UUID REFERENCES farmer_profiles,
  size_acres DECIMAL,
  location GEOGRAPHY(POINT),
  soil_test_data JSONB
)
```

**5.2.2 Conversation State (DynamoDB)**
```json
{
  "session_id": "uuid",
  "user_id": "uuid",
  "conversation_history": [
    {"role": "user", "message": "...", "timestamp": "..."},
    {"role": "agent", "message": "...", "agent": "crop", "timestamp": "..."}
  ],
  "context": {
    "current_crop": "wheat",
    "current_stage": "flowering",
    "active_agent": "crop"
  },
  "ttl": 1234567890
}
```

**5.2.3 Knowledge Graph (Neptune)**
```
Nodes:
- Village (id, name, district, state, pincode)
- Crop (id, name, variety, season)
- Practice (id, description, stage, inputs)
- Farmer (id, success_score)
- Disease (id, name, symptoms, treatment)

Edges:
- Village -[GROWS]-> Crop
- Crop -[REQUIRES]-> Practice
- Farmer -[FOLLOWS]-> Practice
- Farmer -[ACHIEVED]-> Yield
- Crop -[AFFECTED_BY]-> Disease
```

**5.2.4 Market Data (Timestream)**
```
mandi_prices (
  time TIMESTAMP,
  mandi_id VARCHAR,
  crop_id VARCHAR,
  variety VARCHAR,
  price_per_quintal DECIMAL,
  arrival_quantity DECIMAL,
  measure_dimensions
)
```

### 5.3 Data Ingestion Pipelines

**5.3.1 Mandi Price Ingestion**
```
Agmarknet API → Lambda → Data Validation → Timestream
                    ↓
                  SNS (price alerts)
```

**5.3.2 Weather Data Ingestion**
```
Weather APIs → Lambda (every 3 hours) → Timestream
                    ↓
              EventBridge → Alert Service
```

**5.3.3 Scheme Data Ingestion**
```
Government Portals → Web Scraper (Lambda) → Data Cleaning → PostgreSQL
                                                  ↓
                                            OpenSearch (indexing)
```


## 6. Infrastructure Architecture

### 6.1 AWS Services Mapping

**Compute**:
- ECS Fargate: Orchestration layer, agent services
- Lambda: Event-driven processing, webhooks, data ingestion
- SageMaker: ML model training and inference

**Storage**:
- S3: Media files, ML models, data lake, backups
- EBS: Persistent volumes for containers
- EFS: Shared file system (if needed)

**Database**:
- RDS PostgreSQL: Transactional data (Multi-AZ)
- DynamoDB: Session state, high-throughput data
- Neptune: Knowledge graph
- Timestream: Time-series data
- ElastiCache Redis: Caching layer
- OpenSearch: Full-text search

**Networking**:
- VPC: Isolated network environment
- ALB: Load balancing for services
- API Gateway: External API endpoints
- CloudFront: CDN for static assets
- Route 53: DNS management

**Security**:
- IAM: Access control
- Secrets Manager: API keys, credentials
- KMS: Encryption keys
- WAF: Web application firewall
- Shield: DDoS protection
- GuardDuty: Threat detection

**Monitoring & Logging**:
- CloudWatch: Metrics, logs, alarms
- X-Ray: Distributed tracing
- CloudTrail: Audit logs
- SNS: Alert notifications
- EventBridge: Event routing

**ML & AI**:
- SageMaker: Model training, hosting, pipelines
- Transcribe: Speech-to-text
- Translate: Language translation
- Rekognition: Image analysis
- Comprehend: NLP tasks

**Analytics**:
- Kinesis: Real-time data streaming
- Glue: ETL jobs
- Athena: SQL queries on S3
- QuickSight: BI dashboards
- EMR: Big data processing

### 6.2 Network Architecture

```
Internet
    ↓
CloudFront (CDN)
    ↓
Route 53 (DNS)
    ↓
WAF + Shield
    ↓
API Gateway
    ↓
┌─────────────────────────────────────────────────────────┐
│                         VPC                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Public Subnets (Multi-AZ)             │ │
│  │  ALB │ NAT Gateway │ Bastion Host                  │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │             Private Subnets (Multi-AZ)             │ │
│  │  ECS Fargate │ Lambda │ Application Services       │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Data Subnets (Multi-AZ)               │ │
│  │  RDS │ ElastiCache │ Neptune │ OpenSearch         │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Security Groups**:
- ALB SG: Allow 443 from internet
- App SG: Allow traffic from ALB SG
- DB SG: Allow traffic from App SG only
- Lambda SG: Outbound to App and DB SGs

**Subnets**:
- Public: 2 AZs, ALB, NAT Gateway
- Private: 2 AZs, Application services
- Data: 2 AZs, Databases (no internet access)


### 6.3 Deployment Architecture

**Multi-Region Strategy**:
- Primary Region: ap-south-1 (Mumbai)
- DR Region: ap-south-2 (Hyderabad)
- Global Services: CloudFront, Route 53

**High Availability**:
- Multi-AZ deployment for all critical services
- Auto-scaling groups for compute resources
- Read replicas for databases
- Cross-region replication for S3
- Automated failover for RDS

**Disaster Recovery**:
- RPO (Recovery Point Objective): 1 hour
- RTO (Recovery Time Objective): 4 hours
- Automated backups every 6 hours
- Cross-region backup replication
- Regular DR drills (quarterly)

### 6.4 Scaling Strategy

**Horizontal Scaling**:
- ECS Fargate: Auto-scaling based on CPU/memory
- Lambda: Automatic scaling (1000 concurrent executions)
- DynamoDB: On-demand capacity mode
- ElastiCache: Cluster mode with auto-scaling

**Vertical Scaling**:
- RDS: Upgrade instance types during maintenance windows
- SageMaker: Multi-model endpoints for cost optimization

**Scaling Triggers**:
- CPU utilization > 70%
- Memory utilization > 80%
- Request queue depth > 100
- Response time > 3 seconds

**Cost Optimization**:
- Spot instances for batch processing
- Reserved instances for baseline capacity
- S3 Intelligent-Tiering for storage
- Lambda provisioned concurrency for critical functions
- SageMaker Serverless Inference for variable traffic

## 7. Security Architecture

### 7.1 Authentication & Authorization

**User Authentication**:
- Phone number verification via OTP
- WhatsApp Business API handles initial auth
- JWT tokens for API access
- Session management in Redis (30-day expiry)

**Service Authentication**:
- IAM roles for AWS services
- Service-to-service auth via API keys
- mTLS for internal communication

**Authorization**:
- RBAC for admin/support users
- Farmer data access restricted to owner
- Audit logs for all data access

### 7.2 Data Security

**Encryption**:
- In-transit: TLS 1.3 for all communications
- At-rest: AES-256 encryption for all storage
- KMS for key management
- Field-level encryption for PII

**Data Privacy**:
- Data residency in India (compliance)
- PII anonymization in logs
- Data retention policy (3 years)
- Right to deletion (GDPR-style)
- Consent management

**Compliance**:
- DPDP Act 2023 compliance
- ISO 27001 certification (target)
- Regular security audits
- Penetration testing (quarterly)

### 7.3 API Security

**Rate Limiting**:
- 100 requests/minute per user
- 1000 requests/minute per service
- Exponential backoff for retries

**Input Validation**:
- Schema validation for all inputs
- Sanitization of user inputs
- File type and size validation
- SQL injection prevention
- XSS prevention

**DDoS Protection**:
- AWS Shield Standard (automatic)
- AWS Shield Advanced (optional)
- WAF rules for common attacks
- CloudFront for traffic distribution


## 8. ML/AI Architecture

### 8.1 Model Training Pipeline

```
Data Collection → Data Labeling → Feature Engineering → Model Training
                                                              ↓
                                                    Model Evaluation
                                                              ↓
                                                    A/B Testing
                                                              ↓
                                                    Production Deployment
```

**Infrastructure**:
- SageMaker Training Jobs for model training
- SageMaker Processing for data preprocessing
- SageMaker Pipelines for MLOps
- S3 for training data and model artifacts
- ECR for custom training containers

**Model Registry**:
- SageMaker Model Registry for versioning
- Model metadata (accuracy, training date, dataset)
- Approval workflow for production deployment
- Rollback capability

### 8.2 Model Serving

**Deployment Options**:
- SageMaker Real-time Endpoints: Low-latency inference
- SageMaker Serverless: Variable traffic patterns
- SageMaker Batch Transform: Bulk predictions
- Lambda: Lightweight models

**Model Monitoring**:
- Data drift detection
- Model performance degradation alerts
- A/B testing framework
- Shadow deployment for new models

### 8.3 ML Models Inventory

| Model | Purpose | Framework | Hosting |
|-------|---------|-----------|---------|
| Disease Detection | Crop disease identification | PyTorch | SageMaker Endpoint |
| Price Forecasting | Crop price prediction | Prophet/LSTM | SageMaker Serverless |
| Intent Classification | User intent detection | Transformers | Lambda |
| Language Detection | Identify user language | FastText | Lambda |
| Crop Recommendation | Best crop suggestion | XGBoost | SageMaker Endpoint |
| Entity Extraction | Extract crop, location, etc. | spaCy/BERT | Lambda |
| Image Quality Check | Validate uploaded images | CNN | Lambda |
| Sentiment Analysis | User satisfaction | IndicBERT | Lambda |

### 8.4 Training Data Management

**Data Sources**:
- User interactions (with consent)
- Public datasets (PlantVillage, Kaggle)
- Government agricultural data
- Crowdsourced labels from agronomists
- Synthetic data generation

**Data Labeling**:
- Amazon SageMaker Ground Truth
- Partnership with agricultural universities
- Expert agronomist review
- Quality control (inter-annotator agreement)

**Data Versioning**:
- DVC (Data Version Control) on S3
- Dataset snapshots for reproducibility
- Metadata tracking (source, date, quality)

## 9. Monitoring & Observability

### 9.1 Metrics

**Application Metrics**:
- Request rate, error rate, latency (RED metrics)
- Agent response time (p50, p95, p99)
- Model inference time
- Queue depth and processing lag
- User engagement (DAU, MAU, messages/user)

**Infrastructure Metrics**:
- CPU, memory, disk utilization
- Network throughput
- Database connections, query performance
- Cache hit rate
- Lambda cold starts

**Business Metrics**:
- User acquisition and retention
- Feature adoption rates
- Agent accuracy (user feedback)
- Cost per user
- Revenue (if applicable)

### 9.2 Logging

**Log Aggregation**:
- CloudWatch Logs for centralized logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARN, ERROR
- Correlation IDs for request tracing

**Log Types**:
- Application logs (service logs)
- Access logs (API Gateway, ALB)
- Audit logs (data access, changes)
- Error logs (exceptions, failures)
- Security logs (auth attempts, violations)

**Log Retention**:
- Application logs: 30 days
- Audit logs: 7 years
- Error logs: 90 days
- Access logs: 90 days

### 9.3 Tracing

**Distributed Tracing**:
- AWS X-Ray for end-to-end tracing
- Trace user requests across services
- Identify bottlenecks and latency issues
- Service dependency mapping

### 9.4 Alerting

**Alert Channels**:
- PagerDuty for critical alerts
- Slack for warnings
- Email for informational alerts

**Alert Types**:
- Critical: Service down, data loss, security breach
- High: High error rate, slow response time
- Medium: Resource utilization, queue backlog
- Low: Deployment notifications, scheduled maintenance

**On-Call Rotation**:
- 24/7 on-call support
- Escalation policy (15 min → 30 min → 1 hour)
- Runbooks for common issues


## 10. API Design

### 10.1 External APIs

**WhatsApp Webhook API**
```
POST /webhooks/whatsapp
Request:
{
  "from": "+919876543210",
  "message": {
    "type": "text|image|audio",
    "content": "...",
    "media_url": "..."
  },
  "timestamp": "2024-01-15T10:30:00Z"
}

Response: 200 OK
```

**Agent Query API** (Internal)
```
POST /api/v1/agents/{agent_type}/query
Headers:
  Authorization: Bearer <jwt_token>
  X-Request-ID: <uuid>

Request:
{
  "user_id": "uuid",
  "query": "What fertilizer for wheat?",
  "context": {
    "crop": "wheat",
    "stage": "tillering",
    "location": {...}
  },
  "language": "hi"
}

Response:
{
  "response": "गेहूं के लिए यूरिया...",
  "confidence": 0.95,
  "sources": [...],
  "follow_up_questions": [...]
}
```

### 10.2 Internal Service APIs

**User Service**
- GET /users/{user_id}
- POST /users
- PUT /users/{user_id}
- GET /users/{user_id}/profile

**Conversation Service**
- GET /conversations/{session_id}
- POST /conversations
- PUT /conversations/{session_id}/messages

**Knowledge Graph Service**
- GET /knowledge/villages/{village_id}/crops
- GET /knowledge/crops/{crop_id}/practices
- POST /knowledge/feedback

**Price Service**
- GET /prices/mandis/{mandi_id}/latest
- GET /prices/forecast/{crop_id}
- GET /prices/compare

### 10.3 API Versioning

- URL-based versioning: /api/v1/, /api/v2/
- Backward compatibility for 2 versions
- Deprecation notice 6 months in advance
- API documentation via OpenAPI/Swagger

### 10.4 API Rate Limits

| User Type | Rate Limit | Burst |
|-----------|------------|-------|
| Free User | 100/min | 150 |
| Premium User | 500/min | 750 |
| Internal Service | 10000/min | 15000 |
| Admin | Unlimited | - |

## 11. Data Flow Diagrams

### 11.1 User Query Flow

```
1. Farmer sends WhatsApp message
   ↓
2. WhatsApp Business API → API Gateway → Lambda
   ↓
3. Message published to SQS queue
   ↓
4. Orchestration service picks message
   ↓
5. Retrieve user context from DynamoDB
   ↓
6. NLP service: Language detection, translation, intent classification
   ↓
7. Route to appropriate agent (Crop/Finance/Market)
   ↓
8. Agent processes query:
   - Fetch data from databases
   - Run ML models if needed
   - Apply business logic
   ↓
9. Generate response
   ↓
10. Translate response to user language
   ↓
11. Format for WhatsApp
   ↓
12. Send via WhatsApp Business API
   ↓
13. Update conversation state in DynamoDB
   ↓
14. Log metrics to CloudWatch
```

### 11.2 Disease Detection Flow

```
1. Farmer sends crop image via WhatsApp
   ↓
2. Image downloaded and stored in S3
   ↓
3. Image quality check (Lambda)
   ↓
4. If quality OK:
   - Invoke SageMaker endpoint
   - Disease detection model inference
   ↓
5. Get disease prediction + confidence
   ↓
6. Query knowledge graph for treatment
   ↓
7. Check local pesticide availability (Finance Agent)
   ↓
8. Generate comprehensive response:
   - Disease name (local language)
   - Severity assessment
   - Treatment recommendations
   - Product suggestions with prices
   - Application instructions
   ↓
9. Send response with image annotations
   ↓
10. Store interaction for model improvement
```

### 11.3 Price Alert Flow

```
1. EventBridge triggers daily price ingestion (6 PM)
   ↓
2. Lambda fetches mandi prices from Agmarknet
   ↓
3. Store in Timestream
   ↓
4. Compare with user alert thresholds (DynamoDB)
   ↓
5. If threshold crossed:
   - Publish to SNS topic
   ↓
6. SNS triggers notification service
   ↓
7. Format alert message
   ↓
8. Send via WhatsApp + SMS
   ↓
9. Log delivery status
```


## 12. DevOps & CI/CD

### 12.1 CI/CD Pipeline

**Source Control**: GitHub/GitLab
**CI/CD Tool**: AWS CodePipeline + CodeBuild + CodeDeploy

**Pipeline Stages**:
```
1. Source: Git push triggers pipeline
   ↓
2. Build:
   - Run unit tests
   - Code quality checks (SonarQube)
   - Security scanning (Snyk, Trivy)
   - Build Docker images
   - Push to ECR
   ↓
3. Test:
   - Integration tests
   - API tests
   - Load tests (Locust)
   ↓
4. Deploy to Staging:
   - Update ECS task definitions
   - Deploy to staging environment
   - Run smoke tests
   ↓
5. Manual Approval (for production)
   ↓
6. Deploy to Production:
   - Blue-green deployment
   - Health checks
   - Rollback on failure
   ↓
7. Post-Deployment:
   - Monitor metrics
   - Run synthetic tests
   - Notify team
```

**Infrastructure as Code**:
- Terraform for AWS infrastructure
- Helm charts for Kubernetes (if using EKS)
- CloudFormation for some AWS-specific resources
- Version controlled in Git

**Configuration Management**:
- AWS Systems Manager Parameter Store
- AWS Secrets Manager for sensitive data
- Environment-specific configs (dev, staging, prod)

### 12.2 Testing Strategy

**Unit Tests**:
- Coverage target: >80%
- Run on every commit
- Fast execution (<5 minutes)

**Integration Tests**:
- Test service interactions
- Use test databases
- Run on every PR

**End-to-End Tests**:
- Simulate user journeys
- Run on staging before production
- Automated via Selenium/Playwright

**Load Tests**:
- Simulate 100K concurrent users
- Run weekly on staging
- Identify bottlenecks

**Model Tests**:
- Accuracy benchmarks
- Inference time tests
- Data drift detection
- A/B testing in production

### 12.3 Deployment Strategy

**Blue-Green Deployment**:
- Maintain two identical environments
- Switch traffic after validation
- Quick rollback if issues

**Canary Deployment**:
- Deploy to 5% of users first
- Monitor metrics for 1 hour
- Gradually increase to 100%

**Feature Flags**:
- LaunchDarkly or custom solution
- Enable/disable features without deployment
- A/B testing capabilities
- Gradual rollout

### 12.4 Backup & Recovery

**Backup Strategy**:
- RDS: Automated daily backups, 7-day retention
- DynamoDB: Point-in-time recovery enabled
- S3: Versioning enabled, cross-region replication
- Neptune: Daily snapshots
- Configuration: Stored in Git

**Recovery Procedures**:
- Database restore: <1 hour
- Full system restore: <4 hours
- Regular DR drills: Quarterly
- Documented runbooks

## 13. Cost Estimation

### 13.1 Monthly Cost Breakdown (for 100K users)

**Compute**:
- ECS Fargate (10 tasks): $500
- Lambda (10M invocations): $200
- SageMaker Endpoints (3 instances): $1,500

**Storage**:
- S3 (10TB): $230
- EBS (1TB): $100
- Backup storage: $150

**Database**:
- RDS PostgreSQL (db.r5.xlarge Multi-AZ): $600
- DynamoDB (on-demand): $300
- Neptune (db.r5.large): $400
- Timestream: $200
- ElastiCache (cache.r5.large): $200
- OpenSearch (3 nodes): $400

**Networking**:
- Data transfer: $500
- CloudFront: $200
- API Gateway: $100

**ML/AI**:
- SageMaker training: $500
- SageMaker inference: $1,500
- Transcribe: $200
- Rekognition: $100

**Monitoring & Security**:
- CloudWatch: $100
- X-Ray: $50
- GuardDuty: $50
- WAF: $50

**Third-Party**:
- WhatsApp Business API: $2,000
- Weather APIs: $200
- SMS gateway: $300

**Total Monthly Cost**: ~$10,000
**Cost per User**: ~$0.10/month

### 13.2 Cost Optimization Strategies

- Use Spot instances for batch processing (30-70% savings)
- Reserved instances for baseline capacity (40% savings)
- S3 Intelligent-Tiering (automatic cost optimization)
- Right-size instances based on actual usage
- Implement caching to reduce database queries
- Optimize ML model inference (quantization, pruning)
- Use SageMaker Serverless for variable traffic
- Implement data lifecycle policies (archive old data)
- Monitor and eliminate unused resources



### 3.2 Orchestration Layer

**Stack**: Python 3.11, FastAPI, ECS Fargate, SQS, EventBridge

**Components**:
- **Message Router**: SQS consumer → Intent classification → Agent selection
- **NLP Engine**: IndicBERT for language detection, mBERT for intent (95%+ accuracy)
- **Context Manager**: DynamoDB-based conversation state with 30-day TTL
- **Agent Coordinator**: Handles multi-agent queries (parallel execution with timeout)
- **Response Aggregator**: Merges agent responses, handles conflicts

**Intent Classification**:
```python
Intents → Agent Mapping:
- crop_disease, fertilizer, pest_control → Crop Agent
- budget, loan, scheme, subsidy → Finance Agent  
- price, mandi, harvest_timing, crop_recommendation → Market Agent
- multi_intent → Parallel execution → Merge responses
```

**Performance**:
- Intent classification: <100ms (cached model in memory)
- Context retrieval: <50ms (DynamoDB + Redis cache)
- Agent routing: <20ms
- Total orchestration overhead: <200ms

**Scaling**:
- ECS Fargate: 2-20 tasks (auto-scale on CPU >70%)
- Task size: 2 vCPU, 4GB RAM
- SQS: 10K messages/sec throughput
- DynamoDB: On-demand capacity (auto-scales)

**AWS Services**:
- ECS Fargate: Container orchestration
- SQS: Message queue (FIFO for ordered processing)
- DynamoDB: Conversation state (partition key: user_id)
- EventBridge: Scheduled tasks (price updates, alerts)
- CloudWatch: Metrics + alarms


## 14. Technology Stack Summary

### Programming Languages
- **Python 3.11**: ML models, agents, data processing (80% of codebase)
- **Node.js 20.x (TypeScript)**: WhatsApp integration, webhooks (15%)
- **SQL**: Database queries, analytics (5%)

### Frameworks & Libraries
- **FastAPI**: REST APIs (high performance, async)
- **PyTorch**: Deep learning models (disease detection, LSTM)
- **Prophet**: Time-series forecasting
- **Transformers (HuggingFace)**: NLP models (IndicBERT, mBERT)
- **Gremlin**: Graph database queries (Neptune)

### AWS Services (Core)
| Category | Service | Purpose | Instance Type |
|----------|---------|---------|---------------|
| Compute | ECS Fargate | Agents, orchestration | 2 vCPU, 4GB RAM |
| Compute | Lambda | Webhooks, data processing | 512MB-1GB |
| Compute | SageMaker | ML model training/inference | ml.g4dn.xlarge |
| Database | RDS PostgreSQL | User data, schemes | db.r5.large Multi-AZ |
| Database | DynamoDB | Sessions, prices | On-demand |
| Database | Neptune | Knowledge graph | db.r5.large |
| Database | Timestream | Price/weather time-series | Magnetic store |
| Cache | ElastiCache Redis | Session, price cache | cache.r6g.large |
| Storage | S3 | Media, models, backups | Standard + IA + Glacier |
| Search | OpenSearch | Scheme search | 3-node cluster |
| Queue | SQS | Message queuing | Standard + FIFO |
| API | API Gateway | REST endpoints | Regional |
| Security | WAF + Shield | DDoS protection | Standard |
| Monitoring | CloudWatch | Logs, metrics, alarms | - |
| Tracing | X-Ray | Distributed tracing | - |

### Development & Operations
- **IaC**: Terraform (infrastructure), CloudFormation (AWS-specific)
- **CI/CD**: AWS CodePipeline, CodeBuild, CodeDeploy
- **Version Control**: Git (GitHub/GitLab)
- **Containerization**: Docker, ECR
- **Monitoring**: CloudWatch, X-Ray, Prometheus (custom metrics)
- **Logging**: CloudWatch Logs (structured JSON)
- **Secrets**: AWS Secrets Manager, Parameter Store

## 15. Deployment Strategy

### Multi-Region Architecture
- **Primary**: ap-south-1 (Mumbai) - 100% traffic
- **DR**: ap-south-2 (Hyderabad) - Standby (automated failover)
- **Global**: CloudFront (CDN), Route 53 (DNS with health checks)

### High Availability
- **Multi-AZ**: All databases, ECS tasks, load balancers
- **Auto-Scaling**: ECS (2-20 tasks), Lambda (1000 concurrent), DynamoDB (on-demand)
- **Health Checks**: ALB (30s interval), Route 53 (60s interval)
- **Failover**: RDS (automatic, <2 min), Route 53 (DNS failover, <1 min)

### Deployment Pipeline
```
Git Push → CodePipeline Trigger
  ↓
CodeBuild: Test + Build + Security Scan
  ↓
Deploy to Staging (auto)
  ↓
Integration Tests + Load Tests
  ↓
Manual Approval (for production)
  ↓
Blue-Green Deployment to Production
  ↓
Health Checks (5 min monitoring)
  ↓
Auto-Rollback if errors >1%
```

### Rollout Strategy
- **Canary**: 5% → 25% → 50% → 100% (1 hour between stages)
- **Feature Flags**: LaunchDarkly for gradual rollout
- **Rollback**: Automated (<5 min) if error rate >1% or latency >3s

## 16. Cost Optimization

### Monthly Cost Breakdown (100K users)
| Category | Service | Cost (USD) |
|----------|---------|------------|
| Compute | ECS Fargate (10 tasks) | $500 |
| Compute | Lambda (10M invocations) | $200 |
| ML | SageMaker (3 endpoints) | $1,500 |
| Database | RDS PostgreSQL | $600 |
| Database | DynamoDB | $300 |
| Database | Neptune | $400 |
| Database | Timestream | $200 |
| Cache | ElastiCache Redis | $200 |
| Storage | S3 (10TB) | $230 |
| Network | Data Transfer + CloudFront | $700 |
| Third-Party | WhatsApp Business API | $2,000 |
| Other | Monitoring, Security, etc. | $400 |
| **Total** | | **$7,230** |

**Cost per User**: $0.07/month (₹5.8/month at ₹83/$)

### Optimization Strategies
1. **Spot Instances**: 50% savings on batch processing (EMR, training jobs)
2. **Reserved Instances**: 40% savings on RDS, ElastiCache (1-year commitment)
3. **S3 Intelligent-Tiering**: Automatic cost optimization (30% savings)
4. **Model Optimization**: Quantization (INT8) for 3x faster inference, 50% cost reduction
5. **Caching**: 80%+ cache hit rate reduces database queries by 5x
6. **Right-Sizing**: Continuous monitoring + auto-scaling prevents over-provisioning
7. **Data Lifecycle**: S3 Standard (30 days) → IA (90 days) → Glacier (1 year+)

## 17. Security Architecture

### Defense in Depth
```
Layer 1: WAF + Shield (DDoS protection, SQL injection, XSS)
Layer 2: API Gateway (rate limiting, authentication, throttling)
Layer 3: VPC (private subnets, security groups, NACLs)
Layer 4: IAM (least privilege, role-based access)
Layer 5: Encryption (TLS 1.3 in-transit, AES-256 at-rest)
Layer 6: Monitoring (GuardDuty, CloudTrail, Security Hub)
```

### Data Protection
- **Encryption**: All data encrypted (KMS-managed keys, automatic rotation)
- **PII Handling**: Anonymization in logs, field-level encryption for sensitive data
- **Data Residency**: All data stored in India (compliance with DPDP Act 2023)
- **Backup**: Automated backups (6-hour interval), cross-region replication
- **Access Control**: RBAC with MFA, audit logs for all data access

### Compliance
- **DPDP Act 2023**: Data protection, consent management, right to deletion
- **ISO 27001**: Information security management (target certification)
- **SOC 2 Type II**: Security, availability, confidentiality (target)
- **WhatsApp Business Policy**: Message templates, opt-in/opt-out

## 18. Monitoring & Observability

### Key Metrics (CloudWatch)
- **Application**: Request rate, error rate, latency (p50, p95, p99)
- **Business**: DAU, MAU, messages/user, agent usage, feature adoption
- **Infrastructure**: CPU, memory, disk, network, database connections
- **ML Models**: Inference time, accuracy, data drift, prediction distribution

### Alerting (PagerDuty + Slack)
- **Critical** (P1): Service down, data loss, security breach → PagerDuty (immediate)
- **High** (P2): Error rate >1%, latency >3s, database issues → PagerDuty (15 min)
- **Medium** (P3): Resource utilization >80%, queue backlog → Slack (1 hour)
- **Low** (P4): Deployment notifications, scheduled maintenance → Slack (next day)

### Distributed Tracing (X-Ray)
- End-to-end request tracing across all services
- Service dependency map (auto-generated)
- Bottleneck identification (latency analysis)
- Error root cause analysis

## 19. Disaster Recovery

### Backup Strategy
- **RDS**: Automated daily backups, 7-day retention, cross-region replication
- **DynamoDB**: Point-in-time recovery (35-day window), on-demand backups
- **S3**: Versioning enabled, cross-region replication (Mumbai → Hyderabad)
- **Neptune**: Daily snapshots, 30-day retention
- **Configuration**: Git-based (infrastructure as code)

### Recovery Procedures
- **RTO** (Recovery Time Objective): 4 hours
- **RPO** (Recovery Point Objective): 1 hour (max data loss)
- **Failover**: Automated for RDS, manual for full region failover
- **DR Drills**: Quarterly (full failover test)
- **Runbooks**: Documented procedures for all failure scenarios

## 20. Success Criteria

### Technical KPIs
- ✅ Response time: <2s (p95) for text queries
- ✅ Uptime: >99.9% (8.76 hours downtime/year max)
- ✅ Model accuracy: Disease >95%, Price >85%, Intent >95%
- ✅ Scalability: Support 100K concurrent users
- ✅ Cost efficiency: <₹5/user/month

### Business KPIs
- ✅ User adoption: 1M users in Year 1
- ✅ Engagement: DAU/MAU >40%
- ✅ Retention: >60% at 90 days
- ✅ Impact: +20-30% farmer income, -40% crop losses
- ✅ NPS: >50 (world-class)

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Authors**: KisaanMitra.AI Engineering Team  
**Status**: Ready for Implementation
