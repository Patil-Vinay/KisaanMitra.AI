"""
Knowledge Graph Visualization Script v2
Generates HTML dashboard for 575 farmers with hyperlocal data
"""

import json
from datetime import datetime

def load_data():
    """Load the knowledge graph data"""
    with open('knowledge_graph_dummy_data.json', 'r') as f:
        return json.load(f)

def generate_stats(data):
    """Generate statistics from the data"""
    farmers = data.get('farmers', [])
    
    # Basic counts
    districts = set(f.get('district', '') for f in farmers if f.get('district'))
    villages = set(f.get('village_name', '') for f in farmers if f.get('village_name'))
    
    # Crop counts
    all_crops = set()
    for f in farmers:
        crops = f.get('crops_grown', [])
        if isinstance(crops, list):
            all_crops.update(crops)
    
    # Soil types
    soil_types = set(f.get('soil_type', '') for f in farmers if f.get('soil_type'))
    
    # Calculate averages
    total_land = sum(float(f.get('land_size_acres', 0)) for f in farmers)
    avg_land = total_land / len(farmers) if farmers else 0
    avg_experience = sum(f.get('experience_years', 0) for f in farmers) / len(farmers) if farmers else 0
    avg_success = sum(f.get('success_rate', 0) for f in farmers) / len(farmers) if farmers else 0
    
    return {
        'total_farmers': len(farmers),
        'total_districts': len(districts),
        'total_villages': len(villages),
        'total_crops': len(all_crops),
        'total_soil_types': len(soil_types),
        'total_land_acres': total_land,
        'avg_land_per_farmer': avg_land,
        'avg_experience_years': avg_experience,
        'avg_success_rate': avg_success * 100,
        'districts': sorted(list(districts)),
        'villages': sorted(list(villages)),
        'crops': sorted(list(all_crops)),
        'soil_types': sorted(list(soil_types))
    }

def get_district_stats(data):
    """Get farmer count per district"""
    farmers = data.get('farmers', [])
    district_counts = {}
    
    for f in farmers:
        district = f.get('district', 'Unknown')
        district_counts[district] = district_counts.get(district, 0) + 1
    
    return sorted(district_counts.items(), key=lambda x: x[1], reverse=True)

def get_crop_stats(data):
    """Get farmer count per crop"""
    farmers = data.get('farmers', [])
    crop_counts = {}
    
    for f in farmers:
        crops = f.get('crops_grown', [])
        if isinstance(crops, list):
            for crop in crops:
                crop_counts[crop] = crop_counts.get(crop, 0) + 1
    
    return sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:15]

def get_soil_stats(data):
    """Get farmer count per soil type"""
    farmers = data.get('farmers', [])
    soil_counts = {}
    
    for f in farmers:
        soil = f.get('soil_type', 'Unknown')
        soil_counts[soil] = soil_counts.get(soil, 0) + 1
    
    return sorted(soil_counts.items(), key=lambda x: x[1], reverse=True)

def generate_html(data, stats):
    """Generate HTML dashboard"""
    
    district_stats = get_district_stats(data)
    crop_stats = get_crop_stats(data)
    soil_stats = get_soil_stats(data)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KisaanMitra.AI - Knowledge Graph Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card .icon {{
            font-size: 3rem;
            margin-bottom: 15px;
        }}
        
        .stat-card .number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-card .label {{
            font-size: 1rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .chart-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .chart-card h2 {{
            margin-bottom: 20px;
            color: #667eea;
            font-size: 1.5rem;
        }}
        
        .info-section {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}
        
        .info-section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .info-item {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .info-item h3 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.2rem;
        }}
        
        .info-item ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .info-item li {{
            padding: 5px 0;
            color: #666;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }}
        
        .footer a {{
            color: white;
            text-decoration: none;
            font-weight: bold;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 KisaanMitra.AI Knowledge Graph</h1>
            <p>Hyperlocal Farmer Network - Maharashtra</p>
            <p style="font-size: 0.9rem; margin-top: 10px;">Last Updated: {datetime.now().strftime('%B %d, %Y at %H:%M IST')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">👥</div>
                <div class="number">{stats['total_farmers']}</div>
                <div class="label">Total Farmers</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🏛️</div>
                <div class="number">{stats['total_districts']}</div>
                <div class="label">Districts</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🏘️</div>
                <div class="number">{stats['total_villages']}</div>
                <div class="label">Villages</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🌾</div>
                <div class="number">{stats['total_crops']}</div>
                <div class="label">Crop Types</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">📏</div>
                <div class="number">{stats['total_land_acres']:,.0f}</div>
                <div class="label">Total Land (acres)</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="number">{stats['avg_land_per_farmer']:.1f}</div>
                <div class="label">Avg Land/Farmer</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">⭐</div>
                <div class="number">{stats['avg_success_rate']:.1f}%</div>
                <div class="label">Avg Success Rate</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🌱</div>
                <div class="number">{stats['total_soil_types']}</div>
                <div class="label">Soil Types</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h2>📊 Farmers by District</h2>
                <canvas id="districtChart"></canvas>
            </div>
            
            <div class="chart-card">
                <h2>🌾 Top 15 Crops</h2>
                <canvas id="cropChart"></canvas>
            </div>
            
            <div class="chart-card">
                <h2>🌱 Soil Type Distribution</h2>
                <canvas id="soilChart"></canvas>
            </div>
        </div>
        
        <div class="info-section">
            <h2>🗺️ Coverage Details</h2>
            <div class="info-grid">
                <div class="info-item">
                    <h3>🏛️ Districts ({stats['total_districts']})</h3>
                    <ul>
                        {''.join(f'<li>• {d}</li>' for d in stats['districts'])}
                    </ul>
                </div>
                
                <div class="info-item">
                    <h3>🌱 Soil Types ({stats['total_soil_types']})</h3>
                    <ul>
                        {''.join(f'<li>• {s}</li>' for s in stats['soil_types'])}
                    </ul>
                </div>
                
                <div class="info-item">
                    <h3>🌾 Sample Crops</h3>
                    <ul>
                        {''.join(f'<li>• {c}</li>' for c in stats['crops'][:10])}
                        <li><em>...and {len(stats['crops']) - 10} more</em></li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>KisaanMitra.AI</strong> - Empowering Farmers with AI</p>
            <p style="margin-top: 10px;">
                <a href="https://github.com/parth-nikam/KisaanMitra.AI" target="_blank">View on GitHub</a> | 
                Built with ❤️ for Indian Farmers
            </p>
        </div>
    </div>
    
    <script>
        // District Chart
        const districtCtx = document.getElementById('districtChart').getContext('2d');
        new Chart(districtCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([d[0] for d in district_stats])},
                datasets: [{{
                    label: 'Number of Farmers',
                    data: {json.dumps([d[1] for d in district_stats])},
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Crop Chart
        const cropCtx = document.getElementById('cropChart').getContext('2d');
        new Chart(cropCtx, {{
            type: 'horizontalBar',
            data: {{
                labels: {json.dumps([c[0] for c in crop_stats])},
                datasets: [{{
                    label: 'Number of Farmers',
                    data: {json.dumps([c[1] for c in crop_stats])},
                    backgroundColor: 'rgba(76, 175, 80, 0.8)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                indexAxis: 'y',
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Soil Chart
        const soilCtx = document.getElementById('soilChart').getContext('2d');
        new Chart(soilCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps([s[0] for s in soil_stats])},
                datasets: [{{
                    data: {json.dumps([s[1] for s in soil_stats])},
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)'
                    ],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    return html

def main():
    print("Loading knowledge graph data...")
    data = load_data()
    
    print("Generating statistics...")
    stats = generate_stats(data)
    
    print(f"Found {stats['total_farmers']} farmers across {stats['total_districts']} districts")
    
    print("Generating HTML dashboard...")
    html = generate_html(data, stats)
    
    print("Saving to knowledge_graph_dashboard.html...")
    with open('knowledge_graph_dashboard.html', 'w') as f:
        f.write(html)
    
    print("✅ Dashboard generated successfully!")
    print("📊 Statistics:")
    print(f"   - Total Farmers: {stats['total_farmers']}")
    print(f"   - Districts: {stats['total_districts']}")
    print(f"   - Villages: {stats['total_villages']}")
    print(f"   - Crops: {stats['total_crops']}")
    print(f"   - Total Land: {stats['total_land_acres']:,.0f} acres")
    print(f"   - Avg Success Rate: {stats['avg_success_rate']:.1f}%")

if __name__ == "__main__":
    main()
