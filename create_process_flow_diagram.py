import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Create figure with 16:9 aspect ratio
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)
ax.axis('off')

# Colors
aws_orange = '#FF9900'
aws_blue = '#232F3E'
whatsapp_green = '#25D366'
bedrock_purple = '#8B5CF6'
dynamodb_blue = '#3B82F6'
s3_green = '#10B981'
light_gray = '#F3F4F6'
text_gray = '#6B7280'

# Box dimensions
box_width = 1.8
box_height = 1.2
y_center = 4.5

# Positions (x, y)
positions = {
    'farmer1': (1, y_center),
    'whatsapp1': (3.2, y_center),
    'lambda': (5.4, y_center),
    'bedrock': (7.6, y_center),
    'dynamodb': (10, y_center + 1),
    's3': (10, y_center - 1),
    'whatsapp2': (12.2, y_center),
    'farmer2': (14.4, y_center)
}

def create_box(ax, x, y, width, height, color, label, sublabel, icon=''):
    """Create a rounded rectangle box with text"""
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.1", 
                         facecolor=color, edgecolor='white', linewidth=2)
    ax.add_patch(box)
    
    # Icon (emoji)
    if icon:
        ax.text(x, y + 0.3, icon, fontsize=32, ha='center', va='center')
    
    # Main label
    ax.text(x, y - 0.1, label, fontsize=14, weight='bold', 
            ha='center', va='center', color='white')
    
    # Sublabel
    ax.text(x, y - 0.4, sublabel, fontsize=10, 
            ha='center', va='center', color='white', alpha=0.9)

def create_arrow(ax, x1, y1, x2, y2, color=aws_orange):
    """Create an arrow between two points"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=30,
                           color=color, linewidth=3)
    ax.add_patch(arrow)

# Create boxes
create_box(ax, positions['farmer1'][0], positions['farmer1'][1], 
           box_width, box_height, aws_blue, 'Farmer', 'WhatsApp Query', '👨‍🌾')

create_box(ax, positions['whatsapp1'][0], positions['whatsapp1'][1], 
           box_width, box_height, whatsapp_green, 'WhatsApp API', 'Message Received', '📱')

create_box(ax, positions['lambda'][0], positions['lambda'][1], 
           box_width, box_height, aws_orange, 'Lambda', 'Orchestrator', '⚡')

create_box(ax, positions['bedrock'][0], positions['bedrock'][1], 
           box_width, box_height, bedrock_purple, 'Amazon Bedrock', 'Nova Pro AI', '🤖')

# AWS Services container
container = FancyBboxPatch((9, 2.5), 2.5, 4,
                          boxstyle="round,pad=0.15",
                          facecolor=light_gray, edgecolor=text_gray, 
                          linewidth=2, linestyle='--', alpha=0.3)
ax.add_patch(container)
ax.text(10.25, 6.8, 'AWS Services', fontsize=11, weight='bold', 
        ha='center', color=text_gray)

create_box(ax, positions['dynamodb'][0], positions['dynamodb'][1], 
           1.6, 1.0, dynamodb_blue, 'DynamoDB', 'User Profiles', '🗄️')

create_box(ax, positions['s3'][0], positions['s3'][1], 
           1.6, 1.0, s3_green, 'S3', 'Images', '📦')

create_box(ax, positions['whatsapp2'][0], positions['whatsapp2'][1], 
           box_width, box_height, whatsapp_green, 'WhatsApp', 'Response', '📱')

create_box(ax, positions['farmer2'][0], positions['farmer2'][1], 
           box_width, box_height, s3_green, 'Farmer', 'Insights Delivered', '✅')

# Create arrows
create_arrow(ax, positions['farmer1'][0] + box_width/2, positions['farmer1'][1],
             positions['whatsapp1'][0] - box_width/2, positions['whatsapp1'][1])

create_arrow(ax, positions['whatsapp1'][0] + box_width/2, positions['whatsapp1'][1],
             positions['lambda'][0] - box_width/2, positions['lambda'][1])

create_arrow(ax, positions['lambda'][0] + box_width/2, positions['lambda'][1],
             positions['bedrock'][0] - box_width/2, positions['bedrock'][1])

# Split arrows from Bedrock
create_arrow(ax, positions['bedrock'][0] + box_width/2, positions['bedrock'][1] + 0.3,
             positions['dynamodb'][0] - 0.8, positions['dynamodb'][1])

create_arrow(ax, positions['bedrock'][0] + box_width/2, positions['bedrock'][1] - 0.3,
             positions['s3'][0] - 0.8, positions['s3'][1])

# Converge arrows to WhatsApp
create_arrow(ax, positions['dynamodb'][0] + 0.8, positions['dynamodb'][1],
             positions['whatsapp2'][0] - box_width/2, positions['whatsapp2'][1] + 0.3)

create_arrow(ax, positions['s3'][0] + 0.8, positions['s3'][1],
             positions['whatsapp2'][0] - box_width/2, positions['whatsapp2'][1] - 0.3)

create_arrow(ax, positions['whatsapp2'][0] + box_width/2, positions['whatsapp2'][1],
             positions['farmer2'][0] - box_width/2, positions['farmer2'][1])

# Title
ax.text(8, 8.2, 'KisaanMitra.AI - Process Flow', 
        fontsize=20, weight='bold', ha='center', color=aws_blue)

# Subtitle
ax.text(8, 7.7, 'WhatsApp-Based Multi-Agent AI System', 
        fontsize=12, ha='center', color=text_gray)

# Footer
ax.text(8, 0.5, 'Powered by AWS Bedrock | Lambda | DynamoDB | S3', 
        fontsize=10, ha='center', color=text_gray, style='italic')

plt.tight_layout()
plt.savefig('generated-diagrams/kisaanmitra_process_flow_ppt.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Diagram created: generated-diagrams/kisaanmitra_process_flow_ppt.png")
