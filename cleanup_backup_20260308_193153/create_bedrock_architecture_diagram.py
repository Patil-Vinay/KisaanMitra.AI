import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.lines as mlines

# Create figure with 16:9 aspect ratio
fig, ax = plt.subplots(figsize=(20, 11.25))
ax.set_xlim(0, 20)
ax.set_ylim(0, 11.25)
ax.axis('off')

# Colors
aws_orange = '#FF9900'
aws_blue = '#232F3E'
bedrock_purple = '#8B5CF6'
dynamodb_blue = '#3B82F6'
s3_green = '#10B981'
lambda_orange = '#FF9900'
whatsapp_green = '#25D366'
light_gray = '#F3F4F6'
text_color = '#1F2937'

def create_box(ax, x, y, width, height, color, label, sublabel='', icon=''):
    """Create a rounded rectangle box with text"""
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.15", 
                         facecolor=color, edgecolor='white', linewidth=3)
    ax.add_patch(box)
    
    # Icon (emoji)
    if icon:
        ax.text(x, y + 0.35, icon, fontsize=40, ha='center', va='center')
    
    # Main label
    ax.text(x, y - 0.05, label, fontsize=16, weight='bold', 
            ha='center', va='center', color='white')
    
    # Sublabel
    if sublabel:
        ax.text(x, y - 0.35, sublabel, fontsize=11, 
                ha='center', va='center', color='white', alpha=0.9)

def create_arrow(ax, x1, y1, x2, y2, color=aws_orange, label=''):
    """Create an arrow between two points"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=40,
                           color=color, linewidth=3.5)
    ax.add_patch(arrow)
    
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.2, label, fontsize=10, 
                ha='center', color=color, weight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color))

# Title
ax.text(10, 10.5, 'KisaanMitra.AI - Production Architecture', 
        fontsize=28, weight='bold', ha='center', color=aws_blue)
ax.text(10, 10, 'AWS Bedrock Nova Pro | Multi-Agent System', 
        fontsize=14, ha='center', color=text_color, style='italic')

# Layer 1: User
create_box(ax, 2, 5.5, 2.2, 1.4, aws_blue, 'Farmer', 'WhatsApp User', '👨‍🌾')

# Layer 2: Interface
create_box(ax, 5, 5.5, 2.2, 1.4, whatsapp_green, 'WhatsApp', 'Business API', '📱')

# Layer 3: Lambda
create_box(ax, 8, 5.5, 2.5, 1.6, lambda_orange, 'AWS Lambda', 
           'whatsapp-llama-bot\n1536MB | Python 3.14', '⚡')

# Layer 4: Bedrock (larger, prominent)
create_box(ax, 11.5, 8, 2.8, 1.8, bedrock_purple, 'Amazon Bedrock', 
           'Nova Pro\n100% Routing Accuracy', '🤖')

# Layer 5: Storage (grouped)
# Container
container = FancyBboxPatch((13.5, 2.5), 4, 4.5,
                          boxstyle="round,pad=0.2",
                          facecolor=light_gray, edgecolor=text_color, 
                          linewidth=2, linestyle='--', alpha=0.3)
ax.add_patch(container)
ax.text(15.5, 6.7, 'Data Storage', fontsize=13, weight='bold', 
        ha='center', color=text_color)

create_box(ax, 15.5, 5.5, 2, 1.2, dynamodb_blue, 'DynamoDB', 
           '5 Tables', '🗄️')
create_box(ax, 15.5, 3.8, 2, 1.2, s3_green, 'S3', 
           'Images & Docs', '📦')

# Layer 6: Security
create_box(ax, 11.5, 3, 2.2, 1.2, '#DC2626', 'Secrets Manager', 
           'API Keys', '🔐')

# External APIs (bottom)
create_box(ax, 8, 1.5, 1.8, 1, '#6366F1', 'Kindwise API', 
           'Disease Detection', '🌿')
create_box(ax, 11, 1.5, 1.8, 1, '#059669', 'AgMarkNet', 
           'Market Prices', '📊')

# Arrows - Main flow
create_arrow(ax, 3.1, 5.5, 3.9, 5.5, aws_orange)
create_arrow(ax, 6.1, 5.5, 6.75, 5.5, aws_orange)

# Lambda to Bedrock
create_arrow(ax, 9, 6.3, 10.3, 7.5, bedrock_purple, 'AI Routing')

# Bedrock back to Lambda
create_arrow(ax, 10.3, 7, 9, 6, bedrock_purple)

# Lambda to Storage
create_arrow(ax, 9.25, 5.2, 14.5, 5.5, dynamodb_blue)
create_arrow(ax, 9.25, 4.8, 14.5, 3.8, s3_green)

# Lambda to Secrets
create_arrow(ax, 9.5, 4.7, 10.8, 3.7, '#DC2626')

# Lambda to External APIs
create_arrow(ax, 8, 4.7, 8, 2.5, '#6366F1')
create_arrow(ax, 9, 4.6, 10.5, 2.4, '#059669')

# Response flow
create_arrow(ax, 6.75, 5.5, 6.1, 5.5, aws_orange)
create_arrow(ax, 3.9, 5.5, 3.1, 5.5, aws_orange)

# Metrics box (top right)
metrics_box = FancyBboxPatch((16.5, 8), 3, 2,
                            boxstyle="round,pad=0.15",
                            facecolor='white', edgecolor=aws_orange, 
                            linewidth=3)
ax.add_patch(metrics_box)

ax.text(18, 9.6, '✅ Verified Metrics', fontsize=13, weight='bold', 
        ha='center', color=aws_blue)
ax.text(18, 9.2, '100% Routing Accuracy', fontsize=11, 
        ha='center', color='#059669', weight='bold')
ax.text(18, 8.85, '92.86% Extraction', fontsize=11, 
        ha='center', color='#059669', weight='bold')
ax.text(18, 8.5, '2.96s Avg Response', fontsize=11, 
        ha='center', color='#059669', weight='bold')

# Tech stack box (bottom right)
tech_box = FancyBboxPatch((16.5, 0.3), 3, 1.8,
                         boxstyle="round,pad=0.15",
                         facecolor='white', edgecolor=aws_blue, 
                         linewidth=2)
ax.add_patch(tech_box)

ax.text(18, 1.9, 'Technology Stack', fontsize=12, weight='bold', 
        ha='center', color=aws_blue)
ax.text(18, 1.55, 'Python 3.14 | Lambda', fontsize=10, 
        ha='center', color=text_color)
ax.text(18, 1.25, 'Bedrock Nova Pro', fontsize=10, 
        ha='center', color=text_color)
ax.text(18, 0.95, 'DynamoDB | S3', fontsize=10, 
        ha='center', color=text_color)
ax.text(18, 0.65, 'Region: ap-south-1', fontsize=10, 
        ha='center', color=text_color)

# Footer
ax.text(10, 0.3, 'Updated: March 7, 2026 | Status: Production Ready ✅', 
        fontsize=11, ha='center', color=text_color, style='italic')

plt.tight_layout()
plt.savefig('assets/generated-diagrams/kisaanmitra-architecture-updated.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Architecture diagram created: assets/generated-diagrams/kisaanmitra-architecture-updated.png")
