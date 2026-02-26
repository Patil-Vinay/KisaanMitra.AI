# KisaanMitra.AI - Project Structure

## 📁 Clean & Organized Structure

```
kisaanmitra.ai/
│
├── 📄 Core Files
│   ├── README.md                    # Project overview
│   ├── requirements.md              # Product requirements
│   ├── design.md                    # System architecture
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   └── .gitignore                   # Git ignore rules
│
├── 📂 src/                          # Source Code
│   ├── crop_agent/
│   │   ├── crop_health_api.py       # WhatsApp integration
│   │   └── crop_agent_enhanced.py   # Enhanced with memory
│   ├── market_agent/
│   │   └── market_agent.py          # Market intelligence
│   ├── finance_agent/
│   │   └── finance_agent.py         # Financial planning
│   └── lambda/
│       ├── lambda_crop_agent.py
│       ├── lambda_requirements.txt
│       ├── deploy_lambda.sh
│       ├── deploy_market_agent.sh
│       ├── deploy_finance_agent.sh
│       └── package/                 # (gitignored)
│
├── 📂 infrastructure/               # AWS Setup
│   ├── setup_dynamodb.sh
│   ├── setup_finance_tables.sh
│   └── update_iam_permissions.sh
│
├── 📂 scripts/                      # Organized Scripts
│   ├── demo/                        # Demo scripts
│   │   ├── demo_all_agents.sh
│   │   ├── demo_crop_agent.sh
│   │   ├── demo_market_agent.sh
│   │   └── demo_finance_agent.sh
│   └── test/                        # Test scripts
│       ├── test_all.sh
│       ├── test_crop_engine.py
│       ├── test_deployment.sh
│       ├── test_finance_agent.sh
│       ├── test_lambda_whatsapp.sh
│       ├── test_market_agent.sh
│       └── test_whatsapp_integration.sh
│
├── 📂 docs/                         # Documentation
│   ├── AWS_SETUP_GUIDE.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── LAMBDA_SETUP.md
│   ├── QUICK_START_LAMBDA.md
│   ├── TESTING_GUIDE.md
│   ├── QUICK_TEST.md
│   ├── QUICK_DEPLOY.md
│   └── implementation/              # Implementation docs
│       ├── ALL_AGENTS_COMPLETE.md
│       ├── FINANCE_AGENT_FEATURES.md
│       ├── IMPLEMENTATION_SUMMARY.md
│       ├── MARKET_AGENT_IMPLEMENTATION.md
│       └── WHATSAPP_INTEGRATION_STATUS.md
│
└── 📂 assets/                       # Static Assets
    ├── generated-diagrams/          # 6 AWS diagrams
    └── test_images/                 # Test images

```

## 🎯 Quick Access

### Run Demos
```bash
./scripts/demo/demo_all_agents.sh      # All 3 agents
./scripts/demo/demo_crop_agent.sh      # Crop agent only
./scripts/demo/demo_market_agent.sh    # Market agent only
./scripts/demo/demo_finance_agent.sh   # Finance agent only
```

### Run Tests
```bash
./scripts/test/test_all.sh             # All tests (32/32)
./scripts/test/test_whatsapp_integration.sh
./scripts/test/test_market_agent.sh
./scripts/test/test_finance_agent.sh
```

### Deploy
```bash
./infrastructure/setup_dynamodb.sh
./infrastructure/setup_finance_tables.sh
cd src/lambda && ./deploy_lambda.sh
```

## 📊 File Count

- Source files: 7 agents
- Test scripts: 7
- Demo scripts: 4
- Infrastructure: 3
- Documentation: 15
- Total: Clean & organized!

## ✅ What's Gitignored

- `.env` (secrets)
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `package/` (Lambda packages)
- `*.zip` (deployment zips)
- `response*.json` (test outputs)

---

**Status**: Clean & Production Ready ✅  
**Last Updated**: 2026-02-26
