"""
Advanced Knowledge Graph Dashboard with D3.js Network Visualization
Creates an interactive force-directed graph showing connections between districts, villages, and crops
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
    
    for f in farmers:
        district = f.get('district', 'Unknown')
        districts[district] = districts.get(district, 0) + 1
        
        village = f.get('village_name', 'Unknown')
        if village not in villages:
            villages[village] = {'count': 0, 'district': district, 'land': 0}
        villages[village]['count'] += 1
        villages[village]['land'] += float(f.get('land_size_acres', 0))
        
        for crop in f.get('crops_grown', []):
            if crop not in crops:
                crops[crop] = {'count': 0, 'land': 0}
            crops[crop]['count'] += 1
            crops[crop]['land'] += float(f.get('land_size_acres', 0)) / len(f.get('crops_grown', []))
        
        soil = f.get('soil_type', 'Unknown')
        if soil not in soil_types:
            soil_types[soil] = {'count': 0}
        soil_types[soil]['count'] += 1
    
    return {
        'total_farmers': len(farmers),
        'districts': districts,
        'villages': villages,
        'crops': crops,
        'soil_types': soil_types,
        'total_land': sum(float(f.get('land_size_acres', 0)) for f in farmers),
        'avg_success': sum(f.get('success_rate', 0) for f in farmers) / len(farmers) * 100
    }

def generate_network_data(data):
    """Generate nodes and links for D3.js force-directed graph"""
    farmers = data.get('farmers', [])
    
    nodes = []
    links = []
    node_map = {}
    
    # Add district nodes
    districts = {}
    for f in farmers:
        district = f.get('district')
        if district not in districts:
            districts[district] = {'count': 0}
        districts[district]['count'] += 1
    
    for district, info in districts.items():
        node_id = f"d_{district}"
        nodes.append({
            'id': node_id,
            'name': district,
            'type': 'district',
            'count': info['count'],
            'group': 1
        })
        node_map[district] = node_id
    
    # Add top 40 villages by farmer count
    village_data = {}
    for f in farmers:
        village = f.get('village_name')
        district = f.get('district')
        key = f"{village}|{district}"
        if key not in village_data:
            village_data[key] = {'village': village, 'district': district, 'count': 0}
        village_data[key]['count'] += 1
    
    top_villages = sorted(village_data.items(), key=lambda x: x[1]['count'], reverse=True)[:40]
    
    for key, info in top_villages:
        node_id = f"v_{key}"
        nodes.append({
            'id': node_id,
            'name': info['village'],
            'type': 'village',
            'count': info['count'],
            'group': 2
        })
        node_map[key] = node_id
        
        # Link village to district
        if info['district'] in node_map:
            links.append({
                'source': node_map[info['district']],
                'target': node_id,
                'value': info['count']
            })
    
    # Add top 20 crops
    crop_counts = {}
    for f in farmers:
        for crop in f.get('crops_grown', []):
            crop_counts[crop] = crop_counts.get(crop, 0) + 1
    
    top_crops = sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    for crop, count in top_crops:
        node_id = f"c_{crop}"
        nodes.append({
            'id': node_id,
            'name': crop,
            'type': 'crop',
            'count': count,
            'group': 3
        })
        node_map[crop] = node_id
    
    # Link crops to villages (sample connections from first 150 farmers)
    for f in farmers[:150]:
        village_key = f"{f.get('village_name')}|{f.get('district')}"
        if village_key in node_map:
            for crop in f.get('crops_grown', []):
                if crop in node_map:
                    links.append({
                        'source': node_map[village_key],
                        'target': node_map[crop],
                        'value': 1
                    })
    
    return {'nodes': nodes, 'links': links}

def create_html(data, stats, network):
    top_crops = sorted(stats['crops'].items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    top_villages = sorted(stats['villages'].items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    district_list = sorted(stats['districts'].items(), key=lambda x: x[1], reverse=True)
    soil_list = sorted(stats['soil_types'].items(), key=lambda x: x[1]['count'], reverse=True)
    
    html_part1 = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KisaanMitra.AI - Advanced Knowledge Graph</title>
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
            background: #0a0e27;
            color: #fff;
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            margin-bottom: 40px;
            border: 1px solid rgba(16, 185, 129, 0.2);
            box-shadow: 0 20px 60px rgba(16, 185, 129, 0.1);
        }}
        
        .header h1 {{
            font-size: 4rem;
            font-weight: 900;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #10b981 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -2px;
        }}
        
        .header p {{
            font-size: 1.4rem;
            opacity: 0.9;
            margin: 10px 0;
            color: #10b981;
        }}
        
        .header .subtitle {{
            font-size: 1rem;
            opacity: 0.6;
            margin-top: 15px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(16, 185, 129, 0.2);
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            opacity: 0;
            transition: opacity 0.4s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3);
            border-color: #10b981;
        }}
        
        .stat-card:hover::before {{
            opacity: 1;
        }}
        
        .stat-icon {{
            font-size: 3rem;
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
        }}
        
        .stat-number {{
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(135deg, #10b981 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }}
        
        .stat-label {{
            font-size: 0.95rem;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 2px;
            position: relative;
            z-index: 1;
        }}
        
        .section {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            backdrop-filter: blur(10px);
            padding: 40px;
            border-radius: 30px;
            margin-bottom: 40px;
            border: 1px solid rgba(16, 185, 129, 0.2);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }}
        
        .section h2 {{
            font-size: 2.5rem;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #10b981 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }}
        
        .section-desc {{
            opacity: 0.7;
            margin-bottom: 30px;
            font-size: 1.1rem;
        }}
        
        #network {{
            width: 100%;
            height: 700px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 20px;
            border: 2px solid rgba(16, 185, 129, 0.3);
            position: relative;
        }}
        
        .legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(16, 185, 129, 0.3);
            z-index: 10;
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
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .chart-container {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}
        
        .chart-container h3 {{
            color: #10b981;
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: 700;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
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
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .node:hover {{
            stroke: #10b981;
            stroke-width: 4px;
        }}
        
        .link {{
            stroke: rgba(16, 185, 129, 0.2);
            stroke-opacity: 0.6;
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
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
            z-index: 1000;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2.5rem;
            }}
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            #network {{
                height: 500px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 KisaanMitra.AI</h1>
            <p>Advanced Knowledge Graph Dashboard</p>
            <p class="subtitle">
                Hyperlocal Farmer Network Intelligence • Maharashtra
            </p>
            <p class="subtitle">
                {stats['total_farmers']} Farmers • {len(stats['districts'])} Districts • {len(stats['villages'])} Villages • {len(stats['crops'])} Crops
            </p>
            <p class="subtitle" style="margin-top: 10px; font-size: 0.85rem;">
                Last Updated: {datetime.now().strftime('%B %d, %Y at %H:%M IST')}
            </p>
        </div>
'''
    
    return html_part1

def create_html_part2(stats, network, top_crops, top_villages, district_list, soil_list):
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
        
        <div class="section">
            <h2>🕸️ Interactive Network Graph</h2>
            <p class="section-desc">
                Explore the connections between districts (purple), villages (blue), and crops (green). 
                Drag nodes to rearrange. Hover for details. Zoom with scroll wheel.
            </p>
            <div id="network">
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #8b5cf6;"></div>
                        <span>Districts</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #3b82f6;"></div>
                        <span>Villages</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #10b981;"></div>
                        <span>Crops</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <h3>📊 District Distribution</h3>
                <canvas id="districtChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>🌾 Top 10 Crops</h3>
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
                    <h3>🏘️ Top 10 Villages by Farmers</h3>
                    <ul>
                        {''.join(f'<li><span>{village}</span><span class="badge">{info["count"]} farmers</span></li>' for village, info in top_villages)}
                    </ul>
                </div>
                
                <div class="info-card">
                    <h3>🌾 Top 10 Crops by Farmers</h3>
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
'''
    
    return html_part2

def create_html_part3(stats, network, district_list, top_crops, soil_list):
    district_labels = [d[0] for d in district_list]
    district_values = [d[1] for d in district_list]
    crop_labels = [c[0] for c in top_crops]
    crop_values = [c[1]['count'] for c in top_crops]
    soil_labels = [s[0] for s in soil_list]
    soil_values = [s[1]['count'] for s in soil_list]
    
    html_part3 = f'''
    <script>
        // Network Graph with D3.js
        const networkData = {json.dumps(network)};
        
        const networkDiv = document.getElementById('network');
        const width = networkDiv.clientWidth;
        const height = 700;
        
        const svg = d3.select('#network')
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .call(d3.zoom()
                .scaleExtent([0.5, 3])
                .on('zoom', (event) => {{
                    g.attr('transform', event.transform);
                }}));
        
        const g = svg.append('g');
        
        const simulation = d3.forceSimulation(networkData.nodes)
            .force('link', d3.forceLink(networkData.links).id(d => d.id).distance(120))
            .force('charge', d3.forceManyBody().strength(-400))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(35));
        
        const link = g.append('g')
            .selectAll('line')
            .data(networkData.links)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke-width', d => Math.sqrt(d.value) * 0.5);
        
        const node = g.append('g')
            .selectAll('circle')
            .data(networkData.nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', d => {{
                if (d.type === 'district') return 25;
                if (d.type === 'village') return 15;
                return 12;
            }})
            .attr('fill', d => {{
                if (d.type === 'district') return '#8b5cf6';
                if (d.type === 'village') return '#3b82f6';
                return '#10b981';
            }})
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        const tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);
        
        node.on('mouseover', function(event, d) {{
            tooltip.transition().duration(200).style('opacity', 1);
            let html = `<strong>${{d.name}}</strong><br/>`;
            html += `Type: ${{d.type.charAt(0).toUpperCase() + d.type.slice(1)}}<br/>`;
            html += `Farmers: ${{d.count || 'N/A'}}`;
            tooltip.html(html)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 28) + 'px');
            
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', d => {{
                    if (d.type === 'district') return 30;
                    if (d.type === 'village') return 18;
                    return 15;
                }});
        }})
        .on('mouseout', function(event, d) {{
            tooltip.transition().duration(500).style('opacity', 0);
            
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', d => {{
                    if (d.type === 'district') return 25;
                    if (d.type === 'village') return 15;
                    return 12;
                }});
        }});
        
        const label = g.append('g')
            .selectAll('text')
            .data(networkData.nodes.filter(d => d.type === 'district'))
            .enter().append('text')
            .text(d => d.name)
            .attr('font-size', '12px')
            .attr('fill', '#fff')
            .attr('text-anchor', 'middle')
            .attr('dy', 35);
        
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
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
                    borderColor: '#0a0e27'
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
    
    print("📊 Generating statistics...")
    stats = generate_stats(data)
    
    print("🕸️ Generating network data...")
    network = generate_network_data(data)
    
    print(f"✅ Found {stats['total_farmers']} farmers, {len(network['nodes'])} nodes, {len(network['links'])} connections")
    
    print("🎨 Creating advanced HTML dashboard...")
    top_crops = sorted(stats['crops'].items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    top_villages = sorted(stats['villages'].items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    district_list = sorted(stats['districts'].items(), key=lambda x: x[1], reverse=True)
    soil_list = sorted(stats['soil_types'].items(), key=lambda x: x[1]['count'], reverse=True)
    
    html = create_html(data, stats, network)
    html += create_html_part2(stats, network, top_crops, top_villages, district_list, soil_list)
    html += create_html_part3(stats, network, district_list, top_crops, soil_list)
    
    print("💾 Saving to knowledge_graph_dashboard.html...")
    with open('knowledge_graph_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ Advanced dashboard generated successfully!")
    print(f"📊 Statistics:")
    print(f"   - Total Farmers: {stats['total_farmers']}")
    print(f"   - Districts: {len(stats['districts'])}")
    print(f"   - Villages: {len(stats['villages'])}")
    print(f"   - Crops: {len(stats['crops'])}")
    print(f"   - Network Nodes: {len(network['nodes'])}")
    print(f"   - Network Links: {len(network['links'])}")
    print(f"   - Total Land: {stats['total_land']:,.0f} acres")

if __name__ == "__main__":
    main()
