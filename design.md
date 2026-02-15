# KisaanMitra.AI - System Design Document

## 1. System Overview

KisaanMitra.AI is a cloud-native, microservices-based multi-agent AI system built on AWS infrastructure. The system uses a hub-and-spoke architecture where WhatsApp serves as the primary interface, a central orchestration layer routes requests to specialized AI agents, and shared services provide common functionality.

### 1.1 Architecture Principles

- **Microservices**: Loosely coupled, independently deployable services
- **Event-Driven**: Asynchronous communication using message queues
- **Cloud-Native**: Leveraging AWS managed services for scalability
- **Multi-Tenancy**: Single system serving multiple users with data isolation
- **API-First**: All services expose RESTful/gRPC APIs
- **Observability**: Comprehensive logging, monitoring, and tracing

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FARMER (WhatsApp)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    WhatsApp Business API                         │
│                    (Twilio/MessageBird)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   API Gateway (AWS API Gateway)                  │
│              Authentication │ Rate Limiting │ Routing            │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  Orchestration Layer (ECS/EKS)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Message Router │ Context Manager │ Agent Coordinator    │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────┬──────────────────┬──────────────────┬───────────────────┘
       │                  │                  │
   ┌───▼────┐        ┌───▼────┐        ┌───▼────┐
   │ Crop   │        │Finance │        │Market  │
   │ Agent  │        │ Agent  │        │ Agent  │
   └───┬────┘        └───┬────┘        └───┬────┘
       │                  │                  │
┌──────▼──────────────────▼──────────────────▼───────────────────┐
│                      Shared Services Layer                       │
│  NLP │ Vision │ Knowledge Graph │ Time Series │ Notification    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                        Data Layer                                │
│  RDS │ DynamoDB │ S3 │ Neptune │ Timestream │ ElastiCache      │
└──────────────────────────────────────────────────────────────────┘
```

## 3. Component Design

### 3.1 WhatsApp Integration Layer

**Technology Stack**: Node.js, AWS Lambda, API Gateway


**Components**:
- **Webhook Handler**: Receives incoming WhatsApp messages
- **Message Parser**: Extracts text, media, location from messages
- **Response Formatter**: Formats agent responses for WhatsApp
- **Media Handler**: Downloads/uploads images, voice messages
- **Session Manager**: Maintains conversation state

**AWS Services**:
- AWS Lambda for serverless message processing
- API Gateway for webhook endpoints
- S3 for media storage
- ElastiCache (Redis) for session management

**Flow**:
1. WhatsApp message → API Gateway → Lambda
2. Lambda validates webhook, extracts message
3. Message published to SQS queue
4. Session context retrieved from Redis
5. Message forwarded to Orchestration Layer

### 3.2 Orchestration Layer

**Technology Stack**: Python/Go, ECS Fargate, SQS, EventBridge

**Components**:
- **Message Router**: Routes messages to appropriate agent
- **Intent Classifier**: Determines user intent using NLP
- **Context Manager**: Maintains conversation context
- **Agent Coordinator**: Manages multi-agent workflows
- **Response Aggregator**: Combines responses from multiple agents

**Routing Logic**:
```
Keywords/Intent → Agent Mapping
- Disease, pest, fertilizer, crop care → Crop Agent
- Budget, loan, scheme, subsidy, cost → Finance Agent
- Price, mandi, sell, harvest, demand → Market Agent
- Multi-intent → Agent Coordinator (sequential/parallel)
```

**AWS Services**:
- ECS Fargate for container orchestration
- SQS for message queuing
- EventBridge for event routing
- DynamoDB for conversation state


### 3.3 Crop Agent

**Technology Stack**: Python, FastAPI, PyTorch, TensorFlow

**Sub-Components**:

**3.3.1 Disease Detection Service**
- **Model**: EfficientNet-B4 / ResNet-50 fine-tuned on PlantVillage + custom Indian crop dataset
- **Input**: Crop images (leaves, stems, fruits)
- **Output**: Disease name, confidence score, severity, treatment recommendations
- **Infrastructure**: SageMaker for model hosting, S3 for image storage
- **Performance**: <5s inference time, batch processing for multiple images

**3.3.2 Knowledge Graph Service**
- **Database**: Amazon Neptune (graph database)
- **Schema**: Village → Crops → Varieties → Practices → Farmers → Success Metrics
- **Queries**: Cypher/Gremlin for traversal
- **Data**: 600,000+ villages, crop-specific practices, farmer success stories
- **Updates**: Continuous learning from farmer feedback

**3.3.3 Recommendation Engine**
- **Input**: Crop type, growth stage, location, weather, soil data
- **Logic**: Rule-based + ML hybrid approach
- **Rules**: Agronomic best practices, regional guidelines
- **ML**: Collaborative filtering for personalized recommendations
- **Output**: Fertilizer dosage, pesticide selection, irrigation schedule

**3.3.4 Weather Integration**
- **APIs**: IMD, OpenWeatherMap, Weather.com
- **Data**: Current conditions, 7-day forecast, historical data
- **Alerts**: Extreme weather warnings, frost alerts, rainfall predictions
- **Storage**: Timestream for time-series weather data

**AWS Services**:
- SageMaker for ML model training and inference
- Neptune for knowledge graph
- Timestream for weather time-series
- Lambda for serverless processing
- S3 for image and model storage


### 3.4 Finance Agent

**Technology Stack**: Python, FastAPI, PostgreSQL, Redis

**Sub-Components**:

**3.4.1 Budget Planning Service**
- **Input**: Crop type, land size, location, farming practices
- **Calculation Engine**: 
  - Seeds: ₹/acre based on variety
  - Fertilizers: NPK requirements × market prices
  - Pesticides: Preventive + curative costs
  - Labor: Regional wage rates × operations
  - Irrigation: Electricity/diesel costs
  - Miscellaneous: 10-15% buffer
- **Output**: Detailed budget breakdown, timeline, cash flow projection
- **Database**: PostgreSQL for structured financial data

**3.4.2 Scheme Matching Service**
- **Database**: PostgreSQL with full-text search
- **Data**: 500+ central and state schemes
- **Matching Logic**:
  - Farmer profile (land size, crop, location, category)
  - Eligibility criteria (income, age, land ownership)
  - Scoring algorithm for best matches
- **Updates**: Weekly scraping of government portals
- **Output**: Ranked list of schemes, eligibility %, application links

**3.4.3 Input Price Comparison**
- **Data Sources**: 
  - Local vendor APIs/partnerships
  - E-commerce platforms (Amazon, Flipkart, AgroStar)
  - Government cooperative prices
- **Database**: DynamoDB for fast lookups
- **Comparison**: Same product across vendors, generic alternatives
- **Output**: Lowest price, quality ratings, delivery options

**3.4.4 Loan Calculator**
- **Input**: Budget requirement, repayment capacity, collateral
- **Products**: KCC, crop loans, term loans, microfinance
- **Calculation**: EMI, interest rates, tenure options
- **Integration**: Bank APIs for real-time rates (future)
- **Output**: Loan recommendations, documentation checklist

**AWS Services**:
- RDS PostgreSQL for transactional data
- DynamoDB for price lookups
- ElastiCache for caching scheme data
- Lambda for serverless calculations
- EventBridge for scheduled data updates


### 3.5 Market Agent

**Technology Stack**: Python, FastAPI, Prophet/LSTM, Timestream

**Sub-Components**:

**3.5.1 Price Forecasting Service**
- **Models**: 
  - Prophet (Facebook) for seasonal trends
  - LSTM/GRU for complex patterns
  - ARIMA for baseline
  - Ensemble for final prediction
- **Training Data**: 5+ years of daily mandi prices (Agmarknet)
- **Features**: Historical prices, seasonality, weather, festivals, supply data
- **Output**: Price forecast (1-6 months), confidence intervals, trend direction
- **Retraining**: Weekly with new data
- **Infrastructure**: SageMaker for training, Lambda for inference

**3.5.2 Mandi Price Tracker**
- **Data Sources**: 
  - Agmarknet API (3000+ mandis)
  - State agricultural marketing board APIs
  - Manual data collection (partnerships)
- **Update Frequency**: Daily at 6 PM IST
- **Database**: Timestream for time-series storage
- **Queries**: Latest prices, historical trends, price comparisons
- **Alerts**: Price threshold notifications via SNS

**3.5.3 Crop Recommendation Engine**
- **Input**: Location, land size, resources, farmer experience, season
- **Analysis**:
  - Expected prices (from forecasting)
  - Input costs (from Finance Agent)
  - ROI calculation
  - Risk assessment (weather, market volatility)
  - Water requirements vs availability
- **Scoring**: Multi-criteria decision analysis
- **Output**: Top 3 crop recommendations with justification

**3.5.4 Demand-Supply Analytics**
- **Data Sources**:
  - Satellite imagery (crop area estimation)
  - Government crop sowing reports
  - Import/export data
  - Consumption patterns
- **Analysis**: Regional supply-demand imbalance detection
- **Output**: Oversupply/undersupply alerts, market sentiment

**3.5.5 Harvest Timing Optimizer**
- **Input**: Crop maturity stage, current prices, price forecast
- **Logic**: 
  - Early harvest: Lower yield but higher price?
  - Optimal harvest: Balance yield and price
  - Late harvest: Higher yield but price risk?
- **Output**: Recommended harvest window, expected revenue scenarios

**AWS Services**:
- SageMaker for ML model training and hosting
- Timestream for price time-series data
- S3 for historical data and model artifacts
- Lambda for data ingestion and processing
- SNS for price alerts
- QuickSight for internal analytics dashboards


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

