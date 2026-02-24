# KisaanMitra.AI - Project Structure

```
kisaanmitra.ai/
│
├── README.md                    # Project overview and quick start
├── requirements.md              # Functional requirements
├── design.md                    # System architecture
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
│
├── src/                         # Source code
│   ├── crop_agent/              # Crop Agent implementation
│   │   └── crop_health_api.py   # Crop Health API client
│   │
│   └── lambda/                  # AWS Lambda functions
│       ├── lambda_crop_agent.py # Lambda handler for Crop Agent
│       ├── lambda_requirements.txt # Lambda dependencies
│       ├── deploy_lambda.sh     # Deployment script
│       └── test_event.json      # Sample test event
│
├── docs/                        # Documentation
│   ├── LAMBDA_SETUP.md          # Complete Lambda setup guide
│   └── QUICK_START_LAMBDA.md    # 5-minute quick start
│
└── assets/                      # Static assets
    ├── diagrams/                # Architecture diagrams (6 AWS diagrams)
    └── test_images/             # Sample test images
        └── 2.jpg                # Sugarcane rust test image
```

## File Descriptions

### Root Files
- **README.md**: Main project documentation with overview, features, and setup
- **requirements.md**: Detailed functional and non-functional requirements
- **design.md**: System architecture, technology stack, and AWS infrastructure
- **requirements.txt**: Python package dependencies
- **.env.example**: Template for environment variables (copy to .env)

### Source Code (`src/`)

#### Crop Agent (`src/crop_agent/`)
- **crop_health_api.py**: Standalone Crop Health API client
  - Disease detection from images
  - 95%+ accuracy
  - Supports local testing

#### Lambda Functions (`src/lambda/`)
- **lambda_crop_agent.py**: AWS Lambda handler
  - Serverless disease detection
  - S3 and base64 image support
  - Hindi response formatting
  - Secrets Manager integration

- **lambda_requirements.txt**: Lambda-specific dependencies
  - requests==2.32.5
  - boto3==1.35.0

- **deploy_lambda.sh**: Automated deployment script
  - Creates IAM roles
  - Packages dependencies
  - Deploys to AWS Lambda

- **test_event.json**: Sample Lambda test event

### Documentation (`docs/`)
- **LAMBDA_SETUP.md**: Complete AWS Lambda integration guide
  - Step-by-step deployment
  - Configuration details
  - Troubleshooting
  - Cost estimation

- **QUICK_START_LAMBDA.md**: 5-minute quick start guide

### Assets (`assets/`)
- **diagrams/**: 6 professional AWS architecture diagrams
  1. Production Architecture
  2. ML/AI Pipeline
  3. Complete System Overview
  4. Detailed Data Flow
  5. Cost Optimization
  6. Simplified Architecture

- **test_images/**: Sample crop images for testing
  - 2.jpg: Sugarcane rust (99% confidence)

## Usage

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API key

# Test Crop Health API
python src/crop_agent/crop_health_api.py
```

### AWS Lambda Deployment
```bash
# Deploy to AWS Lambda
cd src/lambda
./deploy_lambda.sh

# Test Lambda function
aws lambda invoke \
    --function-name kisaanmitra-crop-agent \
    --payload file://test_event.json \
    response.json
```

## Clean Repository Guidelines

### What to Commit
✅ Source code (`src/`)
✅ Documentation (`docs/`, `*.md`)
✅ Configuration templates (`.env.example`)
✅ Deployment scripts (`deploy_lambda.sh`)
✅ Test images (`assets/test_images/`)
✅ Architecture diagrams (`assets/diagrams/`)

### What NOT to Commit
❌ Environment variables (`.env`)
❌ Virtual environments (`venv/`)
❌ Python cache (`__pycache__/`)
❌ IDE settings (`.vscode/`, `.idea/`)
❌ Deployment artifacts (`package/`, `*.zip`)
❌ Temporary files (`*.tmp`, `*.log`)

## Maintenance

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-agent`
2. Add code to appropriate `src/` folder
3. Update documentation in `docs/`
4. Add tests if applicable
5. Update README.md if needed
6. Commit with clear message
7. Create pull request

### Updating Documentation
- Keep README.md concise (overview only)
- Detailed guides go in `docs/`
- Update PROJECT_STRUCTURE.md when adding folders

---

**Status**: Clean and Organized ✅  
**Last Updated**: 2024-02-25
