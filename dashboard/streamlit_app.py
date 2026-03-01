"""
KisaanMitra.AI - Streamlit Dashboard
Real-time analytics and monitoring dashboard
"""

import streamlit as st
import boto3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# AWS Configuration
AWS_REGION = "ap-south-1"

# Initialize AWS clients
@st.cache_resource
def get_aws_clients():
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    return {
        'conversations': dynamodb.Table('kisaanmitra-conversations'),
        'profiles': dynamodb.Table('kisaanmitra-farmer-profiles'),
        'onboarding': dynamodb.Table('kisaanmitra-onboarding'),
    }

def load_knowledge_graph_data():
    """Load knowledge graph demo data"""
    try:
        with open('../demo/knowledge_graph_dummy_data.json', 'r') as f:
            return json.load(f)
    except:
        return {"nodes": [], "edges": []}

# Page config
st.set_page_config(
    page_title="KisaanMitra.AI Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🌾 KisaanMitra.AI Dashboard</div>', unsafe_allow_html=True)
st.markdown("### Real-time Analytics & Monitoring")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/2E7D32/FFFFFF?text=KisaanMitra.AI", use_container_width=True)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📊 Overview", "👥 Users", "💬 Conversations", "🌐 Knowledge Graph", "📈 Analytics"]
    )
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    
    # Load data
    clients = get_aws_clients()
    kg_data = load_knowledge_graph_data()
    
    # Count farmers in KG
    farmers_count = len([n for n in kg_data.get('nodes', []) if n.get('type') == 'farmer'])
    villages_count = len([n for n in kg_data.get('nodes', []) if n.get('type') == 'village'])
    
    st.metric("Total Farmers", farmers_count)
    st.metric("Villages", villages_count)
    st.metric("Active Users", "Loading...")
    
    st.markdown("---")
    st.markdown("**Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Main content based on page selection
if page == "📊 Overview":
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="stat-number">50</div>
            <div class="stat-label">Total Farmers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="stat-number">10</div>
            <div class="stat-label">Villages</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="stat-number">15</div>
            <div class="stat-label">Crops</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="stat-number">₹4.15Cr</div>
            <div class="stat-label">Total Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Crop Distribution")
        
        # Sample data
        crop_data = pd.DataFrame({
            'Crop': ['Sugarcane', 'Wheat', 'Rice', 'Soybean', 'Cotton'],
            'Farmers': [15, 12, 10, 8, 5]
        })
        
        fig = px.pie(crop_data, values='Farmers', names='Crop', 
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 User Growth")
        
        # Sample data
        dates = pd.date_range(start='2026-02-01', end='2026-03-01', freq='D')
        growth_data = pd.DataFrame({
            'Date': dates,
            'Users': range(10, 10 + len(dates))
        })
        
        fig = px.line(growth_data, x='Date', y='Users', 
                      markers=True, line_shape='spline')
        fig.update_traces(line_color='#2E7D32', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Village Stats
    st.subheader("🏘️ Top Villages by Farmers")
    
    village_data = pd.DataFrame({
        'Village': ['Kolhapur', 'Pune', 'Nashik', 'Satara', 'Sangli'],
        'Farmers': [15, 10, 8, 7, 5],
        'Total Land (acres)': [625, 420, 350, 280, 200]
    })
    
    fig = px.bar(village_data, x='Village', y='Farmers', 
                 color='Total Land (acres)',
                 color_continuous_scale='Greens')
    st.plotly_chart(fig, use_container_width=True)

elif page == "👥 Users":
    st.subheader("👥 Registered Farmers")
    
    # Load real user data
    try:
        clients = get_aws_clients()
        response = clients['profiles'].scan(Limit=50)
        users = response.get('Items', [])
        
        if users:
            df = pd.DataFrame(users)
            df = df[['name', 'village', 'crops', 'land_acres', 'registered_at']]
            df.columns = ['Name', 'Village', 'Crops', 'Land (acres)', 'Registered']
            
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="farmers_data.csv",
                mime="text/csv"
            )
        else:
            st.info("No registered farmers yet. Start onboarding on WhatsApp!")
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        st.info("Make sure AWS credentials are configured correctly.")

elif page == "💬 Conversations":
    st.subheader("💬 Recent Conversations")
    
    try:
        clients = get_aws_clients()
        response = clients['conversations'].scan(Limit=20)
        conversations = response.get('Items', [])
        
        if conversations:
            # Filter out language preferences
            conversations = [c for c in conversations if c.get('timestamp') != 'language_preference']
            
            for conv in sorted(conversations, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]:
                with st.expander(f"🗨️ {conv.get('user_id', 'Unknown')} - {conv.get('timestamp', '')[:19]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**User Message:**")
                        st.info(conv.get('message', 'N/A'))
                    with col2:
                        st.markdown("**Bot Response:**")
                        st.success(conv.get('response', 'N/A')[:200] + "...")
                    st.caption(f"Agent: {conv.get('agent', 'unknown')}")
        else:
            st.info("No conversations yet.")
    except Exception as e:
        st.error(f"Error loading conversations: {e}")

elif page == "🌐 Knowledge Graph":
    st.subheader("🌐 Village Knowledge Graph")
    
    kg_data = load_knowledge_graph_data()
    
    col1, col2, col3 = st.columns(3)
    
    farmers = [n for n in kg_data.get('nodes', []) if n.get('type') == 'farmer']
    villages = [n for n in kg_data.get('nodes', []) if n.get('type') == 'village']
    crops = [n for n in kg_data.get('nodes', []) if n.get('type') == 'crop']
    
    with col1:
        st.metric("👥 Farmers", len(farmers))
    with col2:
        st.metric("🏘️ Villages", len(villages))
    with col3:
        st.metric("🌾 Crops", len(crops))
    
    st.markdown("---")
    
    # Village selector
    village_names = [v.get('label', 'Unknown') for v in villages]
    selected_village = st.selectbox("Select Village", village_names)
    
    if selected_village:
        # Filter farmers by village
        village_farmers = [f for f in farmers if f.get('data', {}).get('village') == selected_village]
        
        st.subheader(f"📊 {selected_village} Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Farmers", len(village_farmers))
            total_land = sum(float(f.get('data', {}).get('land_acres', 0)) for f in village_farmers)
            st.metric("Total Land", f"{total_land:.1f} acres")
        
        with col2:
            # Crop distribution
            crop_counts = {}
            for f in village_farmers:
                crops_str = f.get('data', {}).get('crops', '')
                for crop in crops_str.split(','):
                    crop = crop.strip()
                    if crop:
                        crop_counts[crop] = crop_counts.get(crop, 0) + 1
            
            if crop_counts:
                st.markdown("**Top Crops:**")
                for crop, count in sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.write(f"• {crop}: {count} farmers")
        
        st.markdown("---")
        
        # Farmers table
        st.subheader(f"👥 Farmers in {selected_village}")
        
        if village_farmers:
            farmers_df = pd.DataFrame([
                {
                    'Name': f.get('data', {}).get('name', 'Unknown'),
                    'Crops': f.get('data', {}).get('crops', 'N/A'),
                    'Land (acres)': f.get('data', {}).get('land_acres', 'N/A'),
                }
                for f in village_farmers
            ])
            st.dataframe(farmers_df, use_container_width=True)
    
    st.markdown("---")
    st.info("🌐 **Live Dashboard:** http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com")

elif page == "📈 Analytics":
    st.subheader("📈 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Performance", "💰 Revenue", "🌾 Crop Insights"])
    
    with tab1:
        st.markdown("### System Performance Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avg Response Time", "2.3s", "-0.5s")
        with col2:
            st.metric("Success Rate", "98.5%", "+1.2%")
        with col3:
            st.metric("User Satisfaction", "4.7/5", "+0.3")
        
        # Response time chart
        st.markdown("#### Response Time Trend")
        time_data = pd.DataFrame({
            'Hour': range(24),
            'Response Time (s)': [2.1, 2.0, 1.9, 2.2, 2.3, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0, 2.1]
        })
        
        fig = px.area(time_data, x='Hour', y='Response Time (s)', 
                      color_discrete_sequence=['#2E7D32'])
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Revenue Analytics")
        
        # Revenue by crop
        revenue_data = pd.DataFrame({
            'Crop': ['Sugarcane', 'Wheat', 'Rice', 'Soybean', 'Cotton'],
            'Revenue (Cr)': [1.8, 1.2, 0.8, 0.25, 0.1]
        })
        
        fig = px.bar(revenue_data, x='Crop', y='Revenue (Cr)', 
                     color='Revenue (Cr)',
                     color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Crop Performance Insights")
        
        # Yield comparison
        yield_data = pd.DataFrame({
            'Crop': ['Sugarcane', 'Wheat', 'Rice', 'Soybean', 'Cotton'],
            'Avg Yield (quintals/acre)': [461, 35, 28, 15, 12],
            'Success Rate (%)': [85, 78, 82, 75, 70]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Avg Yield', x=yield_data['Crop'], y=yield_data['Avg Yield (quintals/acre)']))
        fig.add_trace(go.Scatter(name='Success Rate', x=yield_data['Crop'], y=yield_data['Success Rate (%)'], 
                                 yaxis='y2', mode='lines+markers', line=dict(color='red', width=3)))
        
        fig.update_layout(
            yaxis=dict(title='Avg Yield (quintals/acre)'),
            yaxis2=dict(title='Success Rate (%)', overlaying='y', side='right'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>KisaanMitra.AI</strong> - Empowering Farmers with AI</p>
    <p>Built with ❤️ for Indian Farmers | © 2026</p>
</div>
""", unsafe_allow_html=True)
