#!/bin/bash

# Deploy KisaanMitra WhatsApp Lambda
# Fixes Bedrock model invocation and integrates all agents

set -e

FUNCTION_NAME="whatsapp-llama-bot"
REGION="ap-south-1"

echo "🚀 Deploying KisaanMitra WhatsApp Lambda with LangGraph..."

# Create deployment package
rm -f whatsapp_deployment.zip

# Check if package directory exists
if [ -d "package" ]; then
    echo "📦 Including LangGraph dependencies..."
    cd package
    zip -r -q ../whatsapp_deployment.zip .
    cd ..
    zip -q whatsapp_deployment.zip lambda_whatsapp_kisaanmitra.py agent_router.py market_data_sources.py
    
    # Add new hackathon feature modules
    echo "🚀 Including hackathon feature modules..."
    zip -q whatsapp_deployment.zip whatsapp_interactive.py ai_orchestrator.py enhanced_disease_detection.py reminder_manager.py sos_handler.py voice_handler.py weather_service.py crop_comparison.py user_state_manager.py navigation_controller.py crop_yield_database.py anthropic_client.py 2>/dev/null || echo "⚠️  Some feature modules not found"
    
    # Add onboarding and knowledge_graph modules
    if [ -d "deployment_package/onboarding" ]; then
        echo "📦 Including onboarding module..."
        cd deployment_package
        zip -r -q ../whatsapp_deployment.zip onboarding/
        cd ..
    fi
    
    if [ -d "deployment_package/knowledge_graph" ]; then
        echo "📦 Including knowledge_graph module..."
        cd deployment_package
        zip -r -q ../whatsapp_deployment.zip knowledge_graph/
        cd ..
    fi
else
    echo "⚠️  No package directory found. LangGraph will use fallback routing."
    echo "   Run: bash install_langgraph.sh to enable AI routing"
    zip -q whatsapp_deployment.zip lambda_whatsapp_kisaanmitra.py agent_router.py market_data_sources.py
    
    # Add new hackathon feature modules
    echo "🚀 Including hackathon feature modules..."
    zip -q whatsapp_deployment.zip whatsapp_interactive.py ai_orchestrator.py enhanced_disease_detection.py reminder_manager.py sos_handler.py voice_handler.py weather_service.py crop_comparison.py user_state_manager.py navigation_controller.py crop_yield_database.py anthropic_client.py 2>/dev/null || echo "⚠️  Some feature modules not found"
    
    # Add onboarding and knowledge_graph modules
    if [ -d "deployment_package/onboarding" ]; then
        echo "📦 Including onboarding module..."
        cd deployment_package
        zip -r -q ../whatsapp_deployment.zip onboarding/
        cd ..
    fi
    
    if [ -d "deployment_package/knowledge_graph" ]; then
        echo "📦 Including knowledge_graph module..."
        cd deployment_package
        zip -r -q ../whatsapp_deployment.zip knowledge_graph/
        cd ..
    fi
fi

echo "✅ Package created"

# Update Lambda function code
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://whatsapp_deployment.zip \
    --region $REGION

echo "⏳ Waiting for update to complete..."
aws lambda wait function-updated --function-name $FUNCTION_NAME --region $REGION

# Update handler and increase timeout for Claude 3.5 Sonnet
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --handler lambda_whatsapp_kisaanmitra.lambda_handler \
    --timeout 120 \
    --memory-size 1536 \
    --region $REGION

echo "⏳ Waiting for configuration update..."
aws lambda wait function-updated --function-name $FUNCTION_NAME --region $REGION

# Update IAM role permissions for cross-region Bedrock
ROLE_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --query 'Configuration.Role' --output text)
ROLE_NAME=$(echo $ROLE_ARN | rev | cut -d'/' -f1 | rev)

echo "📝 Updating IAM permissions for role: $ROLE_NAME"

cat > /tmp/bedrock-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:Converse",
                "bedrock:ConverseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                "arn:aws:bedrock:*::foundation-model/*"
            ]
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name BedrockCrossRegionAccess \
    --policy-document file:///tmp/bedrock-policy.json

echo "✅ Deployment complete!"
echo ""
echo "🧪 Test with:"
echo "   Send WhatsApp message to your number"
echo ""
echo "📊 View logs:"
echo "   aws logs tail /aws/lambda/$FUNCTION_NAME --follow --region $REGION"
