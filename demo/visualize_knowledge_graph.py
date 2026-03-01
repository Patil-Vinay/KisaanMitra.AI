"""
Knowledge Graph Visualization Script
Generates HTML dashboard with interactive graph visualization
"""

import json
import os

def load_dummy_data():
    """Load the dummy knowledge graph data"""
    with open('knowledge_graph_dummy_data.json', 'r') as f:
        return json.load(f)

def generate_stats(data):
    """Generate statistics from the data"""
    stats = {
        'total_farmers': len(data['farmers']),
        'total_villages': len(data['villages']),
        'total_crops': len(data['crops']),
        'total_relationships': len(data['relationships']),
        'total_events': len(data['events']),
        'kolhapur_farmers': len([f for f in data['farmers'] if f['village_name'] == 'Kolhapur']),
        'sugarcane_farmers': len([f for f in data['farmers'] if 'Sugarcane' in f['crops_grown']]),
        'avg_success_rate': sum([f.get('success_rate', 0) for f in data['farmers']]) / len(data['farmers']),
        'total_land_acres': sum([f['land_size_acres'] for f in data['farmers']])
    }
    return stats

def generate_kolhapur_insights(data):
    """Generate specific insights for Kolhapur sugarcane farmers"""
    kolhapur_farmers = [f for f in data['farmers'] if f['village_name'] == 'Kolhapur']
    sugarcane_farmers = [f for f in kolhapur_farmers if 'Sugarcane' in f['crops_grown']]
    
    if not sugarcane_farmers:
        return {}
    
    insights = {
        'total_farmers': len(sugarcane_farmers),
        'avg_land_size': sum([f['land_size_acres'] for f in sugarcane_farmers]) / len(sugarcane_farmers),
        'avg_yield': sum([f.get('avg_yield_sugarcane', 0) for f in sugarcane_farmers]) / len(sugarcane_farmers),
        'avg_success_rate': sum([f['success_rate'] for f in sugarcane_farmers]) / len(sugarcane_farmers),
        'total_revenue': sum([f.get('total_revenue_last_year', 0) for f in sugarcane_farmers]),
        'total_profit': sum([f.get('net_profit_last_year', 0) for f in sugarcane_farmers]),
        'best_farmers': sorted(sugarcane_farmers, key=lambda x: x['success_rate'], reverse=True)[:5],
        'irrigation_methods': {}
    }
    
    # Count irrigation methods
    for farmer in sugarcane_farmers:
        method = farmer.get('irrigation_method', 'Unknown')
        insights['irrigation_methods'][method] = insights['irrigation_methods'].get(method, 0) + 1
    
    return insights

def generate_html_dashboard(data, stats, kolhapur_insights):
    """Generate interactive HTML dashboard"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KisaanMitra Knowledge Graph - Demo Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.2em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .farmer-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .farmer-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .farmer-name {{
            font-weight: bold;
            font-size: 1.2em;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .farmer-detail {{
            color: #666;
            margin: 5px 0;
            font-size: 0.95em;
        }}
        
        .success-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .success-high {{
            background: #d4edda;
            color: #155724;
        }}
        
        .success-medium {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .insight-box {{
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        
        .insight-title {{
            font-weight: bold;
            color: #2196F3;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .chart-container {{
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        #graph {{
            width: 100%;
            height: 600px;
            border: 2px solid #ddd;
            border-radius: 10px;
            background: white;
        }}
        
        .node {{
            cursor: pointer;
        }}
        
        .node:hover {{
            stroke: #667eea;
            stroke-width: 3px;
        }}
        
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        
        .node-label {{
            font-size: 12px;
            pointer-events: none;
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌾 KisaanMitra Knowledge Graph</h1>
            <p class="subtitle">Village-Level Intelligence for Smart Farming</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Farmers</div>
                <div class="stat-number">{stats['total_farmers']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Villages</div>
                <div class="stat-number">{stats['total_villages']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Crops Tracked</div>
                <div class="stat-number">{stats['total_crops']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Relationships</div>
                <div class="stat-number">{stats['total_relationships']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Land (Acres)</div>
                <div class="stat-number">{stats['total_land_acres']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Success Rate</div>
                <div class="stat-number">{stats['avg_success_rate']:.0%}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Kolhapur Sugarcane Farmers - Key Insights</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Sugarcane Farmers</div>
                    <div class="stat-number">{kolhapur_insights['total_farmers']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Land Size</div>
                    <div class="stat-number">{kolhapur_insights['avg_land_size']:.1f}</div>
                    <div class="stat-label" style="font-size: 0.8em; margin-top: 5px;">acres</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Yield</div>
                    <div class="stat-number">{kolhapur_insights['avg_yield']:.0f}</div>
                    <div class="stat-label" style="font-size: 0.8em; margin-top: 5px;">quintals/acre</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Success Rate</div>
                    <div class="stat-number">{kolhapur_insights['avg_success_rate']:.0%}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Revenue</div>
                    <div class="stat-number">₹{kolhapur_insights['total_revenue']/10000000:.1f}Cr</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Profit</div>
                    <div class="stat-number">₹{kolhapur_insights['total_profit']/10000000:.1f}Cr</div>
                </div>
            </div>
            
            <div class="insight-box">
                <div class="insight-title">💡 Key Pattern Discovered</div>
                <p>Farmers using <strong>Drip Irrigation + Organic Fertilizer</strong> achieve <strong>12-15% higher yields</strong> compared to traditional methods.</p>
                <p style="margin-top: 10px;">Best selling month: <strong>March</strong> (15% price premium)</p>
            </div>
            
            <div class="insight-box">
                <div class="insight-title">⚠️ Risk Alert</div>
                <p><strong>Red Rot disease</strong> affects 25% of sugarcane farms during monsoon season.</p>
                <p style="margin-top: 10px;">Prevention: Use resistant varieties + preventive fungicide spray</p>
            </div>
        </div>
        
        <div class="section">
            <h2>🏆 Top Performing Farmers (Kolhapur Sugarcane)</h2>
            <div class="farmer-list">
"""
    
    # Add top farmers
    for farmer in kolhapur_insights['best_farmers']:
        success_class = 'success-high' if farmer['success_rate'] >= 0.85 else 'success-medium'
        html += f"""
                <div class="farmer-card">
                    <div class="farmer-name">{farmer['name']}</div>
                    <div class="farmer-detail">📍 {farmer['village_name']}</div>
                    <div class="farmer-detail">🌾 {farmer['land_size_acres']} acres</div>
                    <div class="farmer-detail">📊 Yield: {farmer.get('avg_yield_sugarcane', 0)} quintals/acre</div>
                    <div class="farmer-detail">💰 Profit: ₹{farmer.get('net_profit_last_year', 0)/100000:.1f}L</div>
                    <div class="farmer-detail">💧 {farmer.get('irrigation_method', 'N/A')}</div>
                    <span class="success-badge {success_class}">{farmer['success_rate']:.0%} Success</span>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>🔗 Knowledge Graph Visualization</h2>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #4CAF50;"></div>
                    <span>Farmers</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #2196F3;"></div>
                    <span>Villages</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #FF9800;"></div>
                    <span>Crops</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #9C27B0;"></div>
                    <span>Markets</span>
                </div>
            </div>
            <div id="graph"></div>
        </div>
        
        <div class="section">
            <h2>📈 How Knowledge Graph Powers KisaanMitra</h2>
            <div class="insight-box">
                <div class="insight-title">1. Hyper-Local Recommendations</div>
                <p>System analyzes 15 sugarcane farmers in Kolhapur to provide location-specific advice</p>
            </div>
            <div class="insight-box">
                <div class="insight-title">2. Pattern Learning</div>
                <p>Identifies that drip irrigation users achieve 12% higher yields - automatically recommends to similar farmers</p>
            </div>
            <div class="insight-box">
                <div class="insight-title">3. Predictive Intelligence</div>
                <p>Forecasts Red Rot disease risk based on historical patterns and current season</p>
            </div>
            <div class="insight-box">
                <div class="insight-title">4. Profit Optimization</div>
                <p>Recommends March as optimal selling month based on 12 similar farmers' success patterns</p>
            </div>
        </div>
    </div>
    
    <script>
        // Graph visualization using D3.js
        const width = document.getElementById('graph').clientWidth;
        const height = 600;
        
        // Sample graph data (simplified for demo)
        const graphData = {
            nodes: [
                {id: 'kolhapur', type: 'village', label: 'Kolhapur'},
                {id: 'parth', type: 'farmer', label: 'Parth'},
                {id: 'rajesh', type: 'farmer', label: 'Rajesh'},
                {id: 'suresh', type: 'farmer', label: 'Suresh'},
                {id: 'sugarcane', type: 'crop', label: 'Sugarcane'},
                {id: 'market', type: 'market', label: 'Kolhapur APMC'}
            ],
            links: [
                {source: 'parth', target: 'kolhapur'},
                {source: 'rajesh', target: 'kolhapur'},
                {source: 'suresh', target: 'kolhapur'},
                {source: 'parth', target: 'sugarcane'},
                {source: 'rajesh', target: 'sugarcane'},
                {source: 'suresh', target: 'sugarcane'},
                {source: 'kolhapur', target: 'market'},
                {source: 'sugarcane', target: 'market'}
            ]
        };
        
        const svg = d3.select('#graph')
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        const colorScale = {
            farmer: '#4CAF50',
            village: '#2196F3',
            crop: '#FF9800',
            market: '#9C27B0'
        };
        
        const simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(150))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append('g')
            .selectAll('line')
            .data(graphData.links)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke-width', 2);
        
        const node = svg.append('g')
            .selectAll('circle')
            .data(graphData.nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', d => d.type === 'village' ? 25 : d.type === 'market' ? 20 : 15)
            .attr('fill', d => colorScale[d.type])
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        const label = svg.append('g')
            .selectAll('text')
            .data(graphData.nodes)
            .enter().append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', 35)
            .text(d => d.label);
        
        simulation.on('tick', () => {
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
        });
        
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
    </script>
</body>
</html>
"""
    
    return html

def main():
    """Main function to generate the dashboard"""
    print("Loading knowledge graph data...")
    data = load_dummy_data()
    
    print("Generating statistics...")
    stats = generate_stats(data)
    
    print("Analyzing Kolhapur sugarcane farmers...")
    kolhapur_insights = generate_kolhapur_insights(data)
    
    print("Generating HTML dashboard...")
    html = generate_html_dashboard(data, stats, kolhapur_insights)
    
    output_file = 'knowledge_graph_dashboard.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Dashboard generated: {output_file}")
    print(f"\n📊 Statistics:")
    print(f"   - Total Farmers: {stats['total_farmers']}")
    print(f"   - Kolhapur Farmers: {stats['kolhapur_farmers']}")
    print(f"   - Sugarcane Farmers: {stats['sugarcane_farmers']}")
    print(f"   - Avg Success Rate: {stats['avg_success_rate']:.1%}")
    print(f"   - Total Land: {stats['total_land_acres']} acres")
    print(f"\n🌾 Kolhapur Sugarcane Insights:")
    print(f"   - Farmers: {kolhapur_insights['total_farmers']}")
    print(f"   - Avg Yield: {kolhapur_insights['avg_yield']:.0f} quintals/acre")
    print(f"   - Total Revenue: ₹{kolhapur_insights['total_revenue']/10000000:.2f} Crores")
    print(f"   - Total Profit: ₹{kolhapur_insights['total_profit']/10000000:.2f} Crores")
    print(f"\n🚀 Open {output_file} in your browser to view the dashboard!")

if __name__ == '__main__':
    main()
