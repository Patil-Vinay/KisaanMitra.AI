# KisaanMitra.AI - Project Structure

```
kisaanmitra.ai/
│
├── README.md                    # Project overview
├── requirements.md              # Functional requirements
├── design.md                    # System architecture
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
│
├── src/                         # Source code
│   ├── crop_agent/              # Crop Agent
│   │   ├── crop_health_api.py   # Original WhatsApp integration
│   │   └── crop_agent_enhanced.py # Enhanced with memory + language
│   │
│   ├── market_agent/            # Market Agent
│   │   └── market_agent.py      # Price trends + recommendations
│   │
│   └── lambda/                  # AWS Lambda functions
│       ├── lambda_crop_agent.py
│       ├── lambda_requirements.txt
│       ├── deploy_lambda.sh
│       ├── deploy_market_agent.sh
│       └── package/             # Dependencies (gitignored)
│
├── infrastructure/              # AWS infrastructure
│   ├── setup_dynamodb.sh        # Create DynamoDB tables
│   └── update_iam_permissions.sh
│
├── docs/                        # Documentation
│   ├── AWS_SETUP_GUIDE.md
│   ├── LAMBDA_SETUP.md
│   ├── QUICK_START_LAMBDA.md
│   └── DEPLOYMENT_CHECKLIST.md
│
├── assets/                      # Static assets
│   ├── generated-diagrams/      # 6 AWS architecture diagrams
│   └── test_images/             # Sample test images
│
├── test_*.sh                    # Test scripts
├── WHATSAPP_INTEGRATION_STATUS.md
└── MARKET_AGENT_IMPLEMENTATION.md
```

## Key Components

### Crop Agent
- **crop_health_api.py**: WhatsApp integration with Bedrock AI + Crop Health API
- **crop_agent_enhanced.py**: Added system prompt, conversation memory, language detection

### Market Agent
- **market_agent.py**: Mandi prices, trend analysis, crop recommendations

### Infrastructure
- **DynamoDB**: Conversation history, market data cache, user preferences
- **Lambda**: Serverless functions for both agents
- **IAM**: Permissions for Bedrock, DynamoDB, S3, Secrets Manager

### Testing
- **test_whatsapp_integration.sh**: WhatsApp features (10/10 passed)
- **test_market_agent.sh**: Market agent features (10/10 passed)
- **test_deployment.sh**: Lambda deployment verification

## Status

✅ Crop Agent: Fully functional with WhatsApp
✅ Market Agent: Implemented and tested
✅ Infrastructure: Scripts ready
✅ Documentation: Complete
✅ Testing: All tests passing

**Last Updated**: 2026-02-26
