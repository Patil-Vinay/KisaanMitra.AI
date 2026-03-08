"""
Create Complete AWS Architecture Overview for KisaanMitra.AI
Shows all components, agents, data flows, and integrations
"""
import os
import sys

# Ensure Graphviz is in PATH
os.environ['PATH'] += r';C:\Program Files\Graphviz\bin'

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.ml import Bedrock
from diagrams.aws.database import Dynamodb, Neptune
from diagrams.aws.storage import S3
from diagrams.aws.security import SecretsManager
from diagrams.aws.integration import SNS, SQS, Eventbridge
from diagrams.aws.analytics import Kinesis
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.onprem.client import User
from diagrams.generic.device import Mobile
from diagrams.programming.framework import Fastapi
from diagrams.onprem.analytics import Tableau

# Create comprehensive diagram
with Diagram('KisaanMitra.AI - Complete System Overview', 
             show=False, 
             direction='TB',
             filename='generated-diagrams/kisaanmitra_complete_overview',
             outformat='png',
             graph_attr={
                 'fontsize': '24', 
                 'bgcolor': 'white',
                 'pad': '0.8',
                 'ranksep': '1.5',
                 'nodesep': '1.0',
                 'splines': 'ortho'
             }):
    
    # ============ USER LAYER ============
    with Cluster('User Layer'):
        farmer = User('Farmers\n(10,000+ Users)')
        admin = User('Admin\nDashboard')
    
    # ============ INTERFACE LAYER ============
    with Cluster('Interface Layer'):
        whatsapp = Mobile('WhatsApp\nBusiness API')
        dashboard = Tableau('Streamlit\nDashboard')
    
    # ============ COMPUTE LAYER ============
    with Cluster('AWS Compute Layer (ap-south-1)'):
        with Cluster('Main Lambda Function'):
            lambda_main = Lambda('whatsapp-llama-bot\n1536MB | Python 3.14\nMulti-Agent Orchestrator')
        
        with Cluster('Background Processing'):
            lambda_onboard = Lambda('Onboarding\nProcessor')
            lambda_analytics = Lambda('Analytics\nAggregator')
    
    # ============ AI/ML LAYER ============
    with Cluster('AI/ML Layer (us-east-1 Cross-Region)'):
        with Cluster('Amazon Bedrock - Nova Pro'):
            bedrock_router = Bedrock('Intent Router\n100% Accuracy')
            bedrock_crop = Bedrock('Crop Health\nAgent')
            bedrock_market = Bedrock('Market Price\nAgent')
            bedrock_weather = Bedrock('Weather\nAgent')
            bedrock_advisory = Bedrock('Advisory\nAgent')
            bedrock_budget = Bedrock('Budget Planning\nAgent')
    
    # ============ EXTERNAL AI SERVICES ============
    with Cluster('External AI Services'):
        kindwise = Fastapi('Kindwise API\nDisease Detection\n95% Accuracy')
        openweather = Fastapi('OpenWeather\nAPI')
        agmarknet = Fastapi('AgMarkNet\nMarket Data')
    
    # ============ DATA STORAGE LAYER ============
    with Cluster('Data Storage Layer (ap-south-1)'):
        with Cluster('DynamoDB Tables'):
            ddb_conv = Dynamodb('Conversations\nTable')
            ddb_farmers = Dynamodb('Farmers\nTable')
            ddb_crops = Dynamodb('Crop Health\nTable')
            ddb_market = Dynamodb('Market Data\nTable')
            ddb_weather = Dynamodb('Weather\nTable')
        
        with Cluster('S3 Storage'):
            s3_images = S3('Crop Images\nBucket')
            s3_docs = S3('Documents\nBucket')
        
        with Cluster('Knowledge Graph'):
            neptune = Neptune('Neptune\nFarmer Profiles\n& Relationships')
    
    # ============ SECURITY & CONFIG ============
    with Cluster('Security & Configuration'):
        secrets = SecretsManager('Secrets Manager\nAPI Keys & Tokens')
        eventbridge_sched = Eventbridge('EventBridge\nScheduled Tasks')
    
    # ============ MONITORING & ANALYTICS ============
    with Cluster('Monitoring & Analytics'):
        kinesis = Kinesis('Kinesis\nReal-time Analytics')
        sqs = SQS('SQS Queue\nAsync Processing')
    
    # ============== MAIN USER FLOW ==============
    farmer >> Edge(color='darkgreen', style='bold', label='1. Send Message') >> whatsapp
    whatsapp >> Edge(color='orange', style='bold', label='2. Webhook') >> lambda_main
    
    # ============== AI ROUTING (Lambda → Bedrock) ==============
    lambda_main >> Edge(color='purple', style='bold', label='3. ask_bedrock()') >> bedrock_router
    bedrock_router >> Edge(color='purple', style='bold', label='Response') >> lambda_main
    
    # Lambda routes to specific Bedrock agents
    lambda_main >> Edge(color='purple', label='Crop Health') >> bedrock_crop
    lambda_main >> Edge(color='purple', label='Market Price') >> bedrock_market
    lambda_main >> Edge(color='purple', label='Weather') >> bedrock_weather
    lambda_main >> Edge(color='purple', label='Advisory') >> bedrock_advisory
    lambda_main >> Edge(color='purple', label='Budget Planning') >> bedrock_budget
    
    # Bedrock agents respond back to Lambda
    bedrock_crop >> Edge(color='purple', style='dotted') >> lambda_main
    bedrock_market >> Edge(color='purple', style='dotted') >> lambda_main
    bedrock_weather >> Edge(color='purple', style='dotted') >> lambda_main
    bedrock_advisory >> Edge(color='purple', style='dotted') >> lambda_main
    bedrock_budget >> Edge(color='purple', style='dotted') >> lambda_main
    
    # ============== EXTERNAL API CALLS (from Lambda) ==============
    lambda_main >> Edge(color='green', label='Disease Detection') >> kindwise
    lambda_main >> Edge(color='blue', label='Weather Data') >> openweather
    lambda_main >> Edge(color='brown', label='Price Data') >> agmarknet
    
    # External APIs respond back
    kindwise >> Edge(color='green', style='dotted') >> lambda_main
    openweather >> Edge(color='blue', style='dotted') >> lambda_main
    agmarknet >> Edge(color='brown', style='dotted') >> lambda_main
    
    # ============== DATA OPERATIONS ==============
    lambda_main >> Edge(color='blue', label='Store/Retrieve') >> ddb_conv
    lambda_main >> Edge(color='blue') >> ddb_farmers
    lambda_main >> Edge(color='blue') >> ddb_crops
    lambda_main >> Edge(color='blue') >> ddb_market
    lambda_main >> Edge(color='blue') >> ddb_weather
    
    lambda_main >> Edge(color='green', label='Upload Images') >> s3_images
    lambda_main >> Edge(color='green', label='Store Docs') >> s3_docs
    
    # ============== ONBOARDING FLOW ==============
    lambda_main >> Edge(color='orange', label='New User') >> lambda_onboard
    lambda_onboard >> Edge(color='red', label='Build Profile') >> neptune
    lambda_onboard >> Edge(color='blue') >> ddb_farmers
    
    # ============== SECURITY ==============
    lambda_main >> Edge(color='red', label='Get Credentials') >> secrets
    
    # ============== ANALYTICS ==============
    lambda_main >> Edge(color='teal', label='Stream Events') >> kinesis
    lambda_main >> Edge(color='gray', label='Queue Tasks') >> sqs
    sqs >> Edge(color='gray') >> lambda_analytics
    
    # ============== SCHEDULED TASKS ==============
    eventbridge_sched >> Edge(color='purple', label='Daily Updates') >> lambda_analytics
    lambda_analytics >> Edge(color='blue') >> ddb_market
    lambda_analytics >> Edge(color='blue') >> ddb_weather
    
    # ============== RESPONSE FLOW ==============
    lambda_main >> Edge(color='orange', style='bold', label='4. Send Response') >> whatsapp
    whatsapp >> Edge(color='darkgreen', style='bold', label='5. Deliver') >> farmer
    
    # ============== ADMIN DASHBOARD ==============
    admin >> Edge(color='darkblue', label='View Analytics') >> dashboard
    dashboard >> Edge(color='darkblue') >> ddb_conv
    dashboard >> Edge(color='darkblue') >> ddb_farmers
    dashboard >> Edge(color='darkblue') >> kinesis
    dashboard >> Edge(color='darkblue') >> neptune

print('✅ Complete AWS Architecture Overview created: generated-diagrams/kisaanmitra_complete_overview.png')
print('📊 Diagram includes:')
print('   - User Layer: Farmers + Admin')
print('   - Interface: WhatsApp + Streamlit Dashboard')
print('   - Compute: 3 Lambda functions (main, onboarding, analytics)')
print('   - AI/ML: 6 Bedrock Nova Pro agents (router, crop, market, weather, advisory, budget)')
print('   - External APIs: Kindwise, OpenWeather, AgMarkNet')
print('   - Storage: 5 DynamoDB tables + 2 S3 buckets + Neptune graph')
print('   - Security: Secrets Manager + EventBridge')
print('   - Analytics: Kinesis + SQS')
print('   - Complete data flows and integrations')
