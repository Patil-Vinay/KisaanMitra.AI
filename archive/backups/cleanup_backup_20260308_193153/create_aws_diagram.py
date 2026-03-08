"""
Create AWS Architecture Diagram for KisaanMitra.AI
Uses AWS MCP diagram tool with proper AWS icons
Shows clear Bedrock usage with bidirectional flows
"""
import os
import sys

# Ensure Graphviz is in PATH
os.environ['PATH'] += r';C:\Program Files\Graphviz\bin'

try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import Lambda
    from diagrams.aws.ml import Bedrock
    from diagrams.aws.database import Dynamodb
    from diagrams.aws.storage import S3
    from diagrams.aws.security import SecretsManager
    from diagrams.onprem.client import User
    from diagrams.generic.device import Mobile
    from diagrams.programming.framework import Fastapi
except ImportError:
    print("Installing diagrams package...")
    os.system(f"{sys.executable} -m pip install diagrams")
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import Lambda
    from diagrams.aws.ml import Bedrock
    from diagrams.aws.database import Dynamodb
    from diagrams.aws.storage import S3
    from diagrams.aws.security import SecretsManager
    from diagrams.onprem.client import User
    from diagrams.generic.device import Mobile
    from diagrams.programming.framework import Fastapi

# Create diagram - Horizontal for PowerPoint (16:9)
with Diagram('KisaanMitra.AI - Production Architecture', 
             show=False, 
             direction='LR',
             filename='generated-diagrams/kisaanmitra_aws_architecture',
             outformat='png',
             graph_attr={
                 'fontsize': '24', 
                 'bgcolor': 'white',
                 'pad': '0.8',
                 'ranksep': '2.0',  # More horizontal spacing
                 'nodesep': '1.2',
                 'ratio': '1.77',  # 16:9 aspect ratio
                 'size': '16,9!'
             }):
    
    # User Layer
    farmer = User('Farmer')
    
    # Interface Layer
    whatsapp = Mobile('WhatsApp\nBusiness API')
    
    # Compute Layer
    lambda_func = Lambda('AWS Lambda\nwhatsapp-llama-bot\n1536MB | Python 3.14')
    
    # AI Layer - BEDROCK (Simplified for presentation)
    with Cluster('Amazon Bedrock Nova Pro\n(us-east-1 Cross-Region)\n✅ 100% Routing | 92.86% Extraction | 2.96s Response'):
        bedrock_router = Bedrock('Intent\nRouter')
        bedrock_agents = Bedrock('Specialized\nAgents\n(Crop, Market,\nWeather, Advisory)')
    
    # Storage & Services (grouped)
    with Cluster('AWS Services (ap-south-1)'):
        dynamodb = Dynamodb('DynamoDB\n5 Tables')
        s3 = S3('S3\nImages')
        secrets = SecretsManager('Secrets\nManager')
    
    # External APIs (compact)
    with Cluster('External APIs'):
        apis = Fastapi('Kindwise\nAgMarkNet\nOpenWeather')
    
    # ========== CLEAN HORIZONTAL FLOW ==========
    # Main flow left to right
    farmer >> Edge(color='darkgreen', style='bold', label='Message') >> whatsapp
    whatsapp >> Edge(color='orange', style='bold', label='Webhook') >> lambda_func
    lambda_func >> Edge(color='purple', style='bold', label='ask_bedrock()') >> bedrock_router
    bedrock_router >> Edge(color='purple', label='Route') >> bedrock_agents
    bedrock_agents >> Edge(color='purple', style='bold', label='AI Response') >> lambda_func
    lambda_func >> Edge(color='orange', style='bold', label='Reply') >> whatsapp
    whatsapp >> Edge(color='darkgreen', style='bold', label='Deliver') >> farmer
    
    # Supporting connections (simplified)
    lambda_func >> Edge(color='blue', label='Data') >> dynamodb
    lambda_func >> Edge(color='teal', label='Images') >> s3
    lambda_func >> Edge(color='red', label='Keys') >> secrets
    lambda_func >> Edge(color='green', label='External Data') >> apis

print('✅ AWS Architecture diagram created: generated-diagrams/kisaanmitra_aws_architecture.png')
print('📊 Horizontal layout for PowerPoint (16:9 aspect ratio)')
print('   ✅ BEDROCK NOVA PRO - Primary AI Engine prominently displayed')
print('   ✅ Clean left-to-right flow: User → WhatsApp → Lambda → Bedrock → Response')
print('   ✅ Verified metrics shown: 100% routing, 92.86% extraction, 2.96s response')
print('   ✅ All AWS services grouped for clarity')
print('   ✅ Ready for presentation deck!')
