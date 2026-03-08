# Repository Structure

## 📁 Main Directories

### `/src` - Source Code
- **`lambda/`** - AWS Lambda functions and handlers
  - `agents/` - Specialized AI agents (Crop, Market, Finance, General)
  - `services/` - Core services (AI, WhatsApp, Monitoring, Cache)
- **`crop_agent/`** - Crop health API client
- **`hyperlocal/`** - Disease tracking system
- **`onboarding/`** - Farmer onboarding module

### `/docs` - Documentation
- AWS setup guides
- Lambda deployment guides
- API documentation
- Architecture documentation

### `/tests` - Test Suites
- Agent test scenarios
- Integration tests
- Validation scripts

### `/infrastructure` - AWS Setup Scripts
- DynamoDB table setup
- EventBridge configuration
- API Gateway setup
- IAM and security configuration

### `/demo` - Demo Applications
- **`web-chat-demo.html`** - Interactive web chat interface
- **`knowledge_graph_dashboard_embedded.html`** - Live KG visualization
- Data generation scripts
- Visualization tools

### `/dashboard` - Analytics Dashboard
- Streamlit dashboard application
- Deployment scripts
- Dashboard documentation

### `/generated-diagrams` - Architecture Diagrams
- 6 professional AWS architecture diagrams
- System flow diagrams
- Cost optimization diagrams

### `/assets` - Static Assets
- Test images
- Logos and branding
- Sample data

### `/archive` - Historical Files
- **`status-logs/`** - Development status logs
- **`deployment-scripts/`** - Old deployment scripts
- **`demo-versions/`** - Previous dashboard versions
- **`backups/`** - Backup files
- **`diagram-generators/`** - Diagram generation scripts
- **`test-files/`** - Old test files

## 📄 Root Files

### Documentation
- **`README.md`** - Main project documentation
- **`ARCHITECTURE.md`** - System architecture
- **`AWS_AI_SUBMISSION_GUIDE.md`** - AWS AI hackathon submission
- **`AWS_ARCHITECTURE_VISUAL.md`** - Architecture diagrams
- **`SUBMISSION_PACKAGE.md`** - Hackathon submission checklist
- **`SUBMISSION_READY.md`** - Final submission status
- **`FEATURES_LIST.md`** - Complete feature list
- **`SAMPLE_COMMANDS.md`** - Usage examples
- **`QUICK_REFERENCE.md`** - Quick start guide
- **`DISEASE_ALERT_SYSTEM.md`** - Disease tracking documentation
- **`HYPERLOCAL_ALERT_DEMO.md`** - Alert system demo

### Configuration
- **`requirements.txt`** - Python dependencies
- **`km_logo.png`** - Project logo

## 🗂️ Archive Organization

All historical, debug, and development files are organized in the `/archive` directory:

```
archive/
├── status-logs/           # 39 development status logs
├── deployment-scripts/    # 7 old deployment scripts
├── demo-versions/         # 7 previous dashboard versions
├── backups/              # Backup files and logs
├── diagram-generators/   # 4 diagram generation scripts
├── test-files/           # Old test scripts
└── [other archived files]
```

## 🎯 Key Files for Getting Started

1. **`README.md`** - Start here for project overview
2. **`ARCHITECTURE.md`** - Understand the system design
3. **`src/lambda/lambda_handler_v2.py`** - Main Lambda handler
4. **`demo/web-chat-demo.html`** - Try the live demo
5. **`docs/AWS_SETUP_GUIDE.md`** - Deploy your own instance

## 📊 Statistics

- **Total Source Files**: ~100+ Python files
- **Lambda Functions**: 3 main handlers + 4 specialized agents
- **Test Files**: 10+ test suites
- **Documentation**: 11 main docs + archived logs
- **Demo Applications**: 2 live demos
- **Architecture Diagrams**: 6 professional diagrams

---

**Note**: The archive folder contains historical development files that are kept for reference but are not needed for understanding or deploying the current system.
