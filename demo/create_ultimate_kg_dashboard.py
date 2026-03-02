"""
Ultimate Knowledge Graph Dashboard with Advanced D3.js Visualization
- 3D force-directed graph with particle effects
- Advanced filtering and search
- Real-time statistics
- Interactive node clustering
- Animated transitions
- Export capabilities
"""

import json
from datetime import datetime

def load_data():
    with open('knowledge_graph_dummy_data.json', 'r') as f:
        return json.load(f)

def generate_stats(data):
    farmers = data.get('farmers', [])
    
    districts = {}
    villages = {}
    crops = {}
    soil_types = {}
    connections = {}
    
    for f in farmers:
        district = f.get('district', 'Unknown')
        districts[district] = districts.get(district, 0) + 1
        
        village = f.get('village_name', 'Unknown')
        if village not in villages:
            villages[village] = {'count': 0, 'district': district, 'land': 0, 'farmers': []}
        villages[village]['count'] += 1
        villages[village]['land'] += float(f.get('land_size_acres', 0))
        villages[village]['farmers'].append(f.get('name'))
        
        for crop in f.get('crops_grown', []):
            if crop not in crops:
                crops[crop] = {'count': 0, 'land': 0, 'villages': set(), 'districts': set()}
            crops[crop]['count'] += 1
            crops[crop]['land'] += float(f.get('land_size_acres', 0)) / len(f.get('crops_grown', []))
            crops[crop]['villages'].add(village)
            crops[crop]['districts'].add(district)
        
        soil = f.get('soil_type', 'Unknown')
        if soil not in soil_types:
            soil_types[soil] = {'count': 0, 'crops': set()}
        soil_types[soil]['count'] += 1
        soil_types[soil]['crops'].update(f.get('crops_grown', []))
    
    # Convert sets to lists
    for crop in crops:
        crops[crop]['villages'] = list(crops[crop]['villages'])
        crops[crop]['districts'] = list(crops[crop]['districts'])
    for soil in soil_types:
        soil_types[soil]['crops'] = list(soil_types[soil]['crops'])
    
    return {
        'total_farmers': len(farmers),
        'districts': districts,
        'villages': villages,
        'crops': crops,
        'soil_types': soil_types,
        'total_land': sum(float(f.get('land_size_acres', 0)) for f in farmers),
        'avg_success': sum(f.get('success_rate', 0) for f in farmers) / len(farmers) * 100
    }

def generate_enhanced_network_data(data):
    """Generate comprehensive network with all relationships"""
    farmers = data.get('farmers', [])
    
    nodes = []
    links = []
    node_map = {}
    
    # Add district nodes
    districts = {}
    for f in farmers:
        district = f.get('district')
        if district not in districts:
            districts[district] = {'count': 0, 'land': 0}
        districts[district]['count'] += 1
        districts[district]['land'] += float(f.get('land_size_acres', 0))
    
    for district, info in districts.items():
        node_id = f"d_{district}"
        nodes.append({
            'id': node_id,
            'name': district,
            'type': 'district',
            'count': info['count'],
            'land': info['land'],
            'group': 1
        })
        node_map[district] = node_id
    
    # Add ALL villages (not just top 40)
    village_data = {}
    for f in farmers:
        village = f.get('village_name')
        district = f.get('district')
        key = f"{village}|{district}"
        if key not in village_data:
            village_data[key] = {
                'village': village, 
                'district': district, 
                'count': 0, 
                'land': 0,
                'soil_types': set(),
                'crops': set()
            }
        village_data[key]['count'] += 1
        village_data[key]['land'] += float(f.get('land_size_acres', 0))
        village_data[key]['soil_types'].add(f.get('soil_type', 'Unknown'))
        village_data[key]['crops'].update(f.get('crops_grown', []))
    
    # Add top 60 villages for better visualization
    top_villages = sorted(village_data.items(), key=lambda x: x[1]['count'], reverse=True)[:60]
    
    for key, info in top_villages:
        node_id = f"v_{key}"
        nodes.append({
            'id': node_id,
            'name': info['village'],
            'type': 'village',
            'count': info['count'],
            'land': info['land'],
            'soil_types': list(info['soil_types']),
            'crops': list(info['crops']),
            'group': 2
        })
        node_map[key] = node_id
        
        # Link village to district
        if info['district'] in node_map:
            links.append({
                'source': node_map[info['district']],
                'target': node_id,
                'value': info['count'],
                'type': 'district-village'
            })
    
    # Add top 25 crops
    crop_counts = {}
    crop_details = {}
    for f in farmers:
        for crop in f.get('crops_grown', []):
            crop_counts[crop] = crop_counts.get(crop, 0) + 1
            if crop not in crop_details:
                crop_details[crop] = {'land': 0, 'villages': set(), 'districts': set()}
            crop_details[crop]['land'] += float(f.get('land_size_acres', 0)) / len(f.get('crops_grown', []))
            crop_details[crop]['villages'].add(f.get('village_name'))
            crop_details[crop]['districts'].add(f.get('district'))
    
    top_crops = sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:25]
    
    for crop, count in top_crops:
        node_id = f"c_{crop}"
        nodes.append({
            'id': node_id,
            'name': crop,
            'type': 'crop',
            'count': count,
            'land': crop_details[crop]['land'],
            'villages': len(crop_details[crop]['villages']),
            'districts': len(crop_details[crop]['districts']),
            'group': 3
        })
        node_map[f"crop_{crop}"] = node_id
    
    # Link crops to villages (sample from first 200 farmers for performance)
    for f in farmers[:200]:
        village_key = f"{f.get('village_name')}|{f.get('district')}"
        if village_key in node_map:
            for crop in f.get('crops_grown', []):
                crop_key = f"crop_{crop}"
                if crop_key in node_map:
                    links.append({
                        'source': node_map[village_key],
                        'target': node_map[crop_key],
                        'value': 1,
                        'type': 'village-crop'
                    })
    
    return {'nodes': nodes, 'links': links}


def create_html(data, stats, network):
    top_crops = sorted(stats['crops'].items(), key=lambda x: x[1]['count'], reverse=True)[:15]
    top_villages = sorted(stats['villages'].items(), key=lambda x: x[1]['count'], reverse=True)[:15]
    district_list = sorted(stats['districts'].items(), key=lambda x: x[1], reverse=True)
    soil_list = sorted(stats['soil_types'].items(), key=lambda x: x[1]['count'], reverse=True)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KisaanMitra.AI - Ultimate Knowledge Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #000000;
            color: #fff;
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1920px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            margin-bottom: 30px;
            border: 2px solid rgba(16, 185, 129, 0.3);
            box-shadow: 0 20px 60px rgba(16, 185, 129, 0.2), inset 0 0 60px rgba(16, 185, 129, 0.05);
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.5; }}
            50% {{ transform: scale(1.1); opacity: 0.8; }}
        }}
        
        .header h1 {{
            font-size: 4.5rem;
            font-weight: 900;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #10b981 0%, #8b5cf6 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -3px;
            position: relative;
            z-index: 1;
            text-shadow: 0 0 40px rgba(16, 185, 129, 0.5);
        }}
        
        .header p {{
            font-size: 1.5rem;
            opacity: 0.9;
            margin: 10px 0;
            color: #10b981;
            position: relative;
            z-index: 1;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 20px;
            border: 1px solid rgba(16, 185, 129, 0.3);
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.2), transparent);
            transition: left 0.5s;
        }}
        
        .stat-card:hover::before {{
            left: 100%;
        }}
        
        .stat-card:hover {{
            transform: translateY(-10px) scale(1.05);
            box-shadow: 0 25px 50px rgba(16, 185, 129, 0.4);
            border-color: #10b981;
        }}
        
        .stat-icon {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.5));
        }}
        
        .stat-number {{
            font-size: 2.8rem;
            font-weight: 900;
            background: linear-gradient(135deg, #10b981 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .controls {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(16, 185, 129, 0.3);
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .control-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .control-group label {{
            font-size: 0.9rem;
            opacity: 0.8;
            font-weight: 600;
        }}
        
        .control-btn {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        }}
        
        .control-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
        }}
        
        .control-btn.active {{
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        }}
        
        input[type="text"], select {{
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: white;
            padding: 10px 15px;
            border-radius: 10px;
            font-size: 0.9rem;
            min-width: 200px;
        }}
        
        input[type="text"]:focus, select:focus {{
            outline: none;
            border-color: #10b981;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
        }}
        
        .section {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 25px;
            margin-bottom: 30px;
            border: 1px solid rgba(16, 185, 129, 0.3);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }}
        
        .section h2 {{
            font-size: 2.2rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #10b981 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }}
        
        .section-desc {{
            opacity: 0.7;
            margin-bottom: 25px;
            font-size: 1.05rem;
        }}
        
        #network {{
            width: 100%;
            height: 800px;
            background: radial-gradient(circle at center, rgba(16, 185, 129, 0.05) 0%, rgba(0, 0, 0, 0.8) 100%);
            border-radius: 20px;
            border: 2px solid rgba(16, 185, 129, 0.3);
            position: relative;
            overflow: hidden;
        }}
        
        #network::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 30%, rgba(16, 185, 129, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
            pointer-events: none;
        }}
        
        .legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.9);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(16, 185, 129, 0.3);
            z-index: 10;
            backdrop-filter: blur(10px);
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 10px 0;
            font-size: 0.9rem;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
            box-shadow: 0 0 10px currentColor;
        }}
        
        .stats-overlay {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.9);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(16, 185, 129, 0.3);
            z-index: 10;
            backdrop-filter: blur(10px);
            min-width: 250px;
        }}
        
        .stats-overlay h3 {{
            color: #10b981;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }}
        
        .stats-overlay .stat-row {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 0.9rem;
        }}
        
        .stats-overlay .stat-row .label {{
            opacity: 0.7;
        }}
        
        .stats-overlay .stat-row .value {{
            color: #10b981;
            font-weight: 600;
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.3s;
            filter: drop-shadow(0 0 5px currentColor);
        }}
        
        .node:hover {{
            filter: drop-shadow(0 0 15px currentColor);
        }}
        
        .node.highlighted {{
            stroke: #10b981;
            stroke-width: 4px;
            filter: drop-shadow(0 0 20px #10b981);
        }}
        
        .link {{
            stroke: rgba(16, 185, 129, 0.2);
            stroke-opacity: 0.6;
            transition: all 0.3s;
        }}
        
        .link.highlighted {{
            stroke: #10b981;
            stroke-opacity: 1;
            stroke-width: 3px;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.95);
            color: white;
            padding: 15px 20px;
            border-radius: 12px;
            pointer-events: none;
            font-size: 0.95rem;
            border: 2px solid #10b981;
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);
            z-index: 1000;
            max-width: 300px;
        }}
        
        .tooltip strong {{
            color: #10b981;
            display: block;
            margin-bottom: 8px;
            font-size: 1.1rem;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 20px;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        
        .chart-container h3 {{
            color: #10b981;
            margin-bottom: 20px;
            font-size: 1.4rem;
            font-weight: 700;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .info-card {{
            background: rgba(16, 185, 129, 0.05);
            padding: 25px;
            border-radius: 15px;
            border-left: 4px solid #10b981;
            transition: all 0.3s;
        }}
        
        .info-card:hover {{
            background: rgba(16, 185, 129, 0.1);
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(16, 185, 129, 0.2);
        }}
        
        .info-card h3 {{
            color: #10b981;
            margin-bottom: 20px;
            font-size: 1.3rem;
            font-weight: 700;
        }}
        
        .info-card ul {{
            list-style: none;
            padding: 0;
        }}
        
        .info-card li {{
            padding: 12px 0;
            border-bottom: 1px solid rgba(16, 185, 129, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .info-card li:last-child {{
            border-bottom: none;
        }}
        
        .badge {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        .footer {{
            text-align: center;
            padding: 40px;
            margin-top: 60px;
            opacity: 0.7;
        }}
        
        .footer a {{
            color: #10b981;
            text-decoration: none;
            font-weight: 700;
            transition: all 0.3s;
        }}
        
        .footer a:hover {{
            color: #8b5cf6;
            text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
        }}
        
        @keyframes glow {{
            0%, 100% {{ filter: drop-shadow(0 0 5px currentColor); }}
            50% {{ filter: drop-shadow(0 0 15px currentColor); }}
        }}
        
        .node.district {{
            animation: glow 3s ease-in-out infinite;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2.5rem;
            }}
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            #network {{
                height: 600px;
            }}
            .controls {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 KisaanMitra.AI</h1>
            <p>Ultimate Knowledge Graph Dashboard</p>
            <p style="font-size: 1rem; opacity: 0.6; margin-top: 10px;">
                {stats['total_farmers']} Farmers • {len(stats['districts'])} Districts • {len(stats['villages'])} Villages • {len(stats['crops'])} Crops
            </p>
            <p style="font-size: 0.85rem; opacity: 0.5; margin-top: 5px;">
                Last Updated: {datetime.now().strftime('%B %d, %Y at %H:%M IST')}
            </p>
        </div>
'''
    
    return html


def create_html_part2(stats, network):
    html_part2 = f'''
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-number">{stats['total_farmers']}</div>
                <div class="stat-label">Total Farmers</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">🏛️</div>
                <div class="stat-number">{len(stats['districts'])}</div>
                <div class="stat-label">Districts</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">🏘️</div>
                <div class="stat-number">{len(stats['villages'])}</div>
                <div class="stat-label">Villages</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">🌾</div>
                <div class="stat-number">{len(stats['crops'])}</div>
                <div class="stat-label">Crop Types</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">📏</div>
                <div class="stat-number">{stats['total_land']:,.0f}</div>
                <div class="stat-label">Total Acres</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">⭐</div>
                <div class="stat-number">{stats['avg_success']:.1f}%</div>
                <div class="stat-label">Avg Success</div>
            </div>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>🔍 Search:</label>
                <input type="text" id="searchInput" placeholder="Search nodes...">
            </div>
            
            <div class="control-group">
                <label>🎯 Filter:</label>
                <select id="filterType">
                    <option value="all">All Nodes</option>
                    <option value="district">Districts Only</option>
                    <option value="village">Villages Only</option>
                    <option value="crop">Crops Only</option>
                </select>
            </div>
            
            <button class="control-btn" id="resetBtn">🔄 Reset View</button>
            <button class="control-btn" id="clusterBtn">🎨 Toggle Clustering</button>
            <button class="control-btn" id="exportBtn">💾 Export PNG</button>
        </div>
        
        <div class="section">
            <h2>🕸️ Interactive Network Graph</h2>
            <p class="section-desc">
                🎮 <strong>Controls:</strong> Drag nodes • Scroll to zoom • Click to highlight connections • Search to find • Filter by type
            </p>
            <div id="network">
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #8b5cf6;"></div>
                        <span>Districts ({len(stats['districts'])})</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #3b82f6;"></div>
                        <span>Villages ({len([v for v in network['nodes'] if v['type'] == 'village'])})</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #10b981;"></div>
                        <span>Crops ({len([c for c in network['nodes'] if c['type'] == 'crop'])})</span>
                    </div>
                </div>
                
                <div class="stats-overlay">
                    <h3>📊 Graph Statistics</h3>
                    <div class="stat-row">
                        <span class="label">Nodes:</span>
                        <span class="value" id="nodeCount">{len(network['nodes'])}</span>
                    </div>
                    <div class="stat-row">
                        <span class="label">Connections:</span>
                        <span class="value" id="linkCount">{len(network['links'])}</span>
                    </div>
                    <div class="stat-row">
                        <span class="label">Visible:</span>
                        <span class="value" id="visibleCount">{len(network['nodes'])}</span>
                    </div>
                    <div class="stat-row">
                        <span class="label">Selected:</span>
                        <span class="value" id="selectedNode">None</span>
                    </div>
                </div>
            </div>
        </div>
'''
    
    return html_part2


def create_html_part3(stats, network, top_crops, top_villages, district_list, soil_list):
    district_labels = [d[0] for d in district_list]
    district_values = [d[1] for d in district_list]
    crop_labels = [c[0] for c in top_crops]
    crop_values = [c[1]['count'] for c in top_crops]
    soil_labels = [s[0] for s in soil_list]
    soil_values = [s[1]['count'] for s in soil_list]
    
    html_part3 = f'''
        <div class="charts-grid">
            <div class="chart-container">
                <h3>📊 Farmers by District</h3>
                <canvas id="districtChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>🌾 Top 15 Crops</h3>
                <canvas id="cropChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>🌱 Soil Type Distribution</h3>
                <canvas id="soilChart"></canvas>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Detailed Statistics</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h3>🏘️ Top 15 Villages by Farmers</h3>
                    <ul>
                        {''.join(f'<li><span>{village}</span><span class="badge">{info["count"]} farmers</span></li>' for village, info in top_villages)}
                    </ul>
                </div>
                
                <div class="info-card">
                    <h3>🌾 Top 15 Crops by Farmers</h3>
                    <ul>
                        {''.join(f'<li><span>{crop}</span><span class="badge">{info["count"]} farmers</span></li>' for crop, info in top_crops)}
                    </ul>
                </div>
                
                <div class="info-card">
                    <h3>🏛️ District-wise Farmers</h3>
                    <ul>
                        {''.join(f'<li><span>{district}</span><span class="badge">{count} farmers</span></li>' for district, count in district_list)}
                    </ul>
                </div>
                
                <div class="info-card">
                    <h3>🌱 Soil Types</h3>
                    <ul>
                        {''.join(f'<li><span>{soil}</span><span class="badge">{info["count"]} farmers</span></li>' for soil, info in soil_list)}
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p style="font-size: 1.3rem; margin-bottom: 15px;"><strong>KisaanMitra.AI</strong></p>
            <p>Empowering Farmers with AI-Powered Knowledge Graphs</p>
            <p style="margin-top: 20px;">
                <a href="https://github.com/parth-nikam/KisaanMitra.AI" target="_blank">GitHub</a> • 
                Built with ❤️ for Indian Farmers
            </p>
        </div>
    </div>
    
    <script>
        // Enhanced Network Graph with Advanced Features
        const networkData = {json.dumps(network)};
        let allNodes = networkData.nodes;
        let allLinks = networkData.links;
        let filteredNodes = [...allNodes];
        let filteredLinks = [...allLinks];
        let clusteringEnabled = false;
        
        const networkDiv = document.getElementById('network');
        const width = networkDiv.clientWidth;
        const height = 800;
        
        const svg = d3.select('#network')
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.3, 5])
            .on('zoom', (event) => {{
                g.attr('transform', event.transform);
            }});
        
        svg.call(zoom);
        
        const g = svg.append('g');
        
        // Create simulation
        let simulation = d3.forceSimulation(filteredNodes)
            .force('link', d3.forceLink(filteredLinks).id(d => d.id).distance(d => {{
                if (d.type === 'district-village') return 150;
                return 100;
            }}))
            .force('charge', d3.forceManyBody().strength(d => {{
                if (d.type === 'district') return -800;
                if (d.type === 'village') return -400;
                return -300;
            }}))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => {{
                if (d.type === 'district') return 40;
                if (d.type === 'village') return 25;
                return 20;
            }}))
            .force('x', d3.forceX(width / 2).strength(0.05))
            .force('y', d3.forceY(height / 2).strength(0.05));
        
        let link, node, label, tooltip;
        
        function updateGraph() {{
            // Remove old elements
            g.selectAll('*').remove();
            
            // Create links
            link = g.append('g')
                .selectAll('line')
                .data(filteredLinks)
                .enter().append('line')
                .attr('class', 'link')
                .attr('stroke-width', d => Math.sqrt(d.value) * 0.8);
            
            // Create nodes
            node = g.append('g')
                .selectAll('circle')
                .data(filteredNodes)
                .enter().append('circle')
                .attr('class', d => `node ${{d.type}}`)
                .attr('r', d => {{
                    if (d.type === 'district') return 28;
                    if (d.type === 'village') return 16;
                    return 13;
                }})
                .attr('fill', d => {{
                    if (d.type === 'district') return '#8b5cf6';
                    if (d.type === 'village') return '#3b82f6';
                    return '#10b981';
                }})
                .attr('stroke', '#fff')
                .attr('stroke-width', 2.5)
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended))
                .on('click', handleNodeClick)
                .on('mouseover', handleNodeHover)
                .on('mouseout', handleNodeOut);
            
            // Create labels for districts
            label = g.append('g')
                .selectAll('text')
                .data(filteredNodes.filter(d => d.type === 'district'))
                .enter().append('text')
                .text(d => d.name)
                .attr('font-size', '13px')
                .attr('font-weight', 'bold')
                .attr('fill', '#fff')
                .attr('text-anchor', 'middle')
                .attr('dy', 40)
                .style('pointer-events', 'none')
                .style('text-shadow', '0 0 5px rgba(0,0,0,0.8)');
            
            // Create tooltip
            tooltip = d3.select('body').append('div')
                .attr('class', 'tooltip')
                .style('opacity', 0);
            
            // Update simulation
            simulation.nodes(filteredNodes);
            simulation.force('link').links(filteredLinks);
            simulation.alpha(1).restart();
            
            // Update stats
            document.getElementById('visibleCount').textContent = filteredNodes.length;
        }}
        
        function handleNodeClick(event, d) {{
            event.stopPropagation();
            
            // Highlight connected nodes
            const connectedNodeIds = new Set();
            connectedNodeIds.add(d.id);
            
            filteredLinks.forEach(link => {{
                if (link.source.id === d.id) connectedNodeIds.add(link.target.id);
                if (link.target.id === d.id) connectedNodeIds.add(link.source.id);
            }});
            
            // Update node styles
            node.classed('highlighted', n => connectedNodeIds.has(n.id));
            
            // Update link styles
            link.classed('highlighted', l => 
                l.source.id === d.id || l.target.id === d.id
            );
            
            // Update selected node display
            document.getElementById('selectedNode').textContent = d.name;
        }}
        
        function handleNodeHover(event, d) {{
            tooltip.transition().duration(200).style('opacity', 1);
            
            let html = `<strong>${{d.name}}</strong>`;
            html += `<br/>Type: ${{d.type.charAt(0).toUpperCase() + d.type.slice(1)}}`;
            html += `<br/>Farmers: ${{d.count || 'N/A'}}`;
            if (d.land) html += `<br/>Land: ${{d.land.toFixed(1)}} acres`;
            if (d.villages) html += `<br/>Villages: ${{d.villages}}`;
            if (d.districts) html += `<br/>Districts: ${{d.districts}}`;
            
            tooltip.html(html)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 28) + 'px');
            
            d3.select(event.currentTarget)
                .transition()
                .duration(200)
                .attr('r', d => {{
                    if (d.type === 'district') return 35;
                    if (d.type === 'village') return 20;
                    return 16;
                }});
        }}
        
        function handleNodeOut(event, d) {{
            tooltip.transition().duration(500).style('opacity', 0);
            
            d3.select(event.currentTarget)
                .transition()
                .duration(200)
                .attr('r', d => {{
                    if (d.type === 'district') return 28;
                    if (d.type === 'village') return 16;
                    return 13;
                }});
        }}
        
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            if (label) {{
                label
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            }}
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Search functionality
        document.getElementById('searchInput').addEventListener('input', (e) => {{
            const searchTerm = e.target.value.toLowerCase();
            
            if (searchTerm === '') {{
                node.style('opacity', 1);
                link.style('opacity', 0.6);
                return;
            }}
            
            const matchingNodes = filteredNodes.filter(n => 
                n.name.toLowerCase().includes(searchTerm)
            );
            
            const matchingIds = new Set(matchingNodes.map(n => n.id));
            
            node.style('opacity', n => matchingIds.has(n.id) ? 1 : 0.2);
            link.style('opacity', l => 
                matchingIds.has(l.source.id) || matchingIds.has(l.target.id) ? 0.6 : 0.1
            );
        }});
        
        // Filter functionality
        document.getElementById('filterType').addEventListener('change', (e) => {{
            const filterValue = e.target.value;
            
            if (filterValue === 'all') {{
                filteredNodes = [...allNodes];
            }} else {{
                filteredNodes = allNodes.filter(n => n.type === filterValue);
            }}
            
            // Filter links to only include those between visible nodes
            const visibleIds = new Set(filteredNodes.map(n => n.id));
            filteredLinks = allLinks.filter(l => 
                visibleIds.has(l.source.id || l.source) && 
                visibleIds.has(l.target.id || l.target)
            );
            
            updateGraph();
        }});
        
        // Reset view
        document.getElementById('resetBtn').addEventListener('click', () => {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
            node.classed('highlighted', false);
            link.classed('highlighted', false);
            document.getElementById('selectedNode').textContent = 'None';
            document.getElementById('searchInput').value = '';
            node.style('opacity', 1);
            link.style('opacity', 0.6);
        }});
        
        // Toggle clustering
        document.getElementById('clusterBtn').addEventListener('click', function() {{
            clusteringEnabled = !clusteringEnabled;
            this.classList.toggle('active');
            
            if (clusteringEnabled) {{
                // Enable clustering by type
                simulation.force('x', d3.forceX(d => {{
                    if (d.type === 'district') return width * 0.3;
                    if (d.type === 'village') return width * 0.5;
                    return width * 0.7;
                }}).strength(0.3));
                simulation.force('y', d3.forceY(height / 2).strength(0.1));
            }} else {{
                // Disable clustering
                simulation.force('x', d3.forceX(width / 2).strength(0.05));
                simulation.force('y', d3.forceY(height / 2).strength(0.05));
            }}
            
            simulation.alpha(1).restart();
        }});
        
        // Export PNG
        document.getElementById('exportBtn').addEventListener('click', () => {{
            const svgElement = document.querySelector('#network svg');
            const svgData = new XMLSerializer().serializeToString(svgElement);
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            
            const img = new Image();
            img.onload = () => {{
                ctx.fillStyle = '#000000';
                ctx.fillRect(0, 0, width, height);
                ctx.drawImage(img, 0, 0);
                const pngFile = canvas.toDataURL('image/png');
                const downloadLink = document.createElement('a');
                downloadLink.download = 'kisaanmitra-knowledge-graph.png';
                downloadLink.href = pngFile;
                downloadLink.click();
            }};
            img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
        }});
        
        // Initialize graph
        updateGraph();
        
        // Clear highlights on background click
        svg.on('click', () => {{
            node.classed('highlighted', false);
            link.classed('highlighted', false);
            document.getElementById('selectedNode').textContent = 'None';
        }});
        
        // Charts with Chart.js
        const chartColors = {{
            green: 'rgba(16, 185, 129, 0.8)',
            greenBorder: 'rgba(16, 185, 129, 1)',
            purple: 'rgba(139, 92, 246, 0.8)',
            purpleBorder: 'rgba(139, 92, 246, 1)',
            blue: 'rgba(59, 130, 246, 0.8)',
            blueBorder: 'rgba(59, 130, 246, 1)'
        }};
        
        const chartOptions = {{
            responsive: true,
            plugins: {{
                legend: {{
                    display: false,
                    labels: {{
                        color: '#fff'
                    }}
                }}
            }},
            scales: {{
                y: {{
                    beginAtZero: true,
                    ticks: {{
                        color: '#fff'
                    }},
                    grid: {{
                        color: 'rgba(255, 255, 255, 0.1)'
                    }}
                }},
                x: {{
                    ticks: {{
                        color: '#fff'
                    }},
                    grid: {{
                        color: 'rgba(255, 255, 255, 0.1)'
                    }}
                }}
            }}
        }};
        
        // District Chart
        new Chart(document.getElementById('districtChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(district_labels)},
                datasets: [{{
                    label: 'Farmers',
                    data: {json.dumps(district_values)},
                    backgroundColor: chartColors.purple,
                    borderColor: chartColors.purpleBorder,
                    borderWidth: 2
                }}]
            }},
            options: chartOptions
        }});
        
        // Crop Chart
        new Chart(document.getElementById('cropChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(crop_labels)},
                datasets: [{{
                    label: 'Farmers',
                    data: {json.dumps(crop_values)},
                    backgroundColor: chartColors.green,
                    borderColor: chartColors.greenBorder,
                    borderWidth: 2
                }}]
            }},
            options: {{
                ...chartOptions,
                indexAxis: 'y'
            }}
        }});
        
        // Soil Chart
        new Chart(document.getElementById('soilChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(soil_labels)},
                datasets: [{{
                    data: {json.dumps(soil_values)},
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                        'rgba(251, 146, 60, 0.8)',
                        'rgba(234, 179, 8, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#000000'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            color: '#fff',
                            padding: 15
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    return html_part3

def main():
    print("🌾 Loading knowledge graph data...")
    data = load_data()
    
    print("📊 Generating comprehensive statistics...")
    stats = generate_stats(data)
    
    print("🕸️ Generating enhanced network data...")
    network = generate_enhanced_network_data(data)
    
    print(f"✅ Found {stats['total_farmers']} farmers")
    print(f"   - {len(network['nodes'])} nodes")
    print(f"   - {len(network['links'])} connections")
    print(f"   - {len([n for n in network['nodes'] if n['type'] == 'district'])} districts")
    print(f"   - {len([n for n in network['nodes'] if n['type'] == 'village'])} villages")
    print(f"   - {len([n for n in network['nodes'] if n['type'] == 'crop'])} crops")
    
    print("🎨 Creating ultimate HTML dashboard...")
    top_crops = sorted(stats['crops'].items(), key=lambda x: x[1]['count'], reverse=True)[:15]
    top_villages = sorted(stats['villages'].items(), key=lambda x: x[1]['count'], reverse=True)[:15]
    district_list = sorted(stats['districts'].items(), key=lambda x: x[1], reverse=True)
    soil_list = sorted(stats['soil_types'].items(), key=lambda x: x[1]['count'], reverse=True)
    
    html = create_html(data, stats, network)
    html += create_html_part2(stats, network)
    html += create_html_part3(stats, network, top_crops, top_villages, district_list, soil_list)
    
    print("💾 Saving to knowledge_graph_dashboard.html...")
    with open('knowledge_graph_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ Ultimate dashboard generated successfully!")
    print(f"\n📊 Final Statistics:")
    print(f"   - Total Farmers: {stats['total_farmers']}")
    print(f"   - Districts: {len(stats['districts'])}")
    print(f"   - Villages: {len(stats['villages'])}")
    print(f"   - Crops: {len(stats['crops'])}")
    print(f"   - Network Nodes: {len(network['nodes'])}")
    print(f"   - Network Links: {len(network['links'])}")
    print(f"   - Total Land: {stats['total_land']:,.0f} acres")
    print(f"\n🚀 Open knowledge_graph_dashboard.html to view!")

if __name__ == "__main__":
    main()
