#!/usr/bin/env python3
"""
Embed actual KG data into the dashboard HTML
"""
import json
import re

# Read the current S3 data
with open('/tmp/kg_latest_data.json', 'r') as f:
    kg_data = json.load(f)

# Read the original HTML
with open('demo/knowledge_graph_dashboard.html', 'r') as f:
    html_content = f.read()

# Create the new data line (without the 'farmers' array to keep it smaller)
kg_data_for_viz = {
    'nodes': kg_data['nodes'],
    'links': kg_data['links'],
    'metadata': kg_data['metadata']
}

new_data_line = f"const networkData = {json.dumps(kg_data_for_viz)};"

# Replace the old networkData line
pattern = r'const networkData = \{.*?\};'
html_content = re.sub(pattern, new_data_line, html_content, flags=re.DOTALL)

# Update hardcoded stats with IDs so they can be updated dynamically
metadata = kg_data['metadata']

# Replace hardcoded stat values with dynamic ones
replacements = [
    (r'<div class="stat-number">10000</div>', f'<div class="stat-number" id="total-farmers">{metadata["total_farmers"]:,}</div>'),
    (r'<div class="stat-number">8</div>', f'<div class="stat-number" id="total-districts">{metadata["total_districts"]}</div>'),
    (r'<div class="stat-number">187</div>', f'<div class="stat-number" id="total-villages">{metadata["total_villages"]}</div>'),
    (r'<div class="stat-number">30</div>', f'<div class="stat-number" id="total-crops">{metadata["total_crops"]}</div>'),
    (r'<div class="stat-number">184,409</div>', f'<div class="stat-number" id="total-land">{metadata["total_land"]:,.0f}</div>'),
]

for pattern, replacement in replacements:
    html_content = re.sub(pattern, replacement, html_content)

# Write the new HTML
with open('demo/knowledge_graph_dashboard_embedded.html', 'w') as f:
    f.write(html_content)

print(f"✅ Created embedded dashboard with {len(kg_data['nodes'])} nodes and {len(kg_data['links'])} links")
print(f"✅ Total farmers in metadata: {kg_data['metadata']['total_farmers']}")
print(f"✅ Stats updated:")
print(f"   - Farmers: {metadata['total_farmers']:,}")
print(f"   - Districts: {metadata['total_districts']}")
print(f"   - Villages: {metadata['total_villages']}")
print(f"   - Crops: {metadata['total_crops']}")
print(f"   - Land: {metadata['total_land']:,.0f} acres")
print(f"✅ Output: demo/knowledge_graph_dashboard_embedded.html")
