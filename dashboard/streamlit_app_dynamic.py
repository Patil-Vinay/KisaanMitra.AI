"""
KisaanMitra.AI - Dynamic Streamlit Dashboard
Real-time analytics with auto-refresh from DynamoDB
"""

import streamlit as st
import boto3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# AWS Configuration
AWS_REGION = "ap-south-1"

# Page config
st.set_page_config(
    page_title="KisaanMitra.AI Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize AWS clients with caching
@st.cache_resource(ttl=60)  # Cache for 60 seconds
def get_aws_clients():
    """Initialize DynamoDB clients with connection pooling"""
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    return {
        'conversations': dynamodb.Table('kisaanmitra-conversations'),
        'profiles': dynamodb.Table('kisaanmitra-farmer-profiles'),
        'onboarding': dynamodb.Table('kisaanmitra-onboarding'),
    }

# Dynamic data loading functions
@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_all_farmers():
    """Load all farmers from DynamoDB - refreshes every 30 seconds"""
    try:
        clients = get_aws_clients()
        response = clients['profiles'].scan()
        farmers = response.get('Items', [])
        
        # Handle pagination if more than 1MB of data
        while 'LastEvaluatedKey' in response:
            response = clients['profiles'].scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            farmers.extend(response.get('Items', []))
        
        return farmers
    except Exception as e:
        st.error(f"Error loading farmers: {e}")
        return []

@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_conversations():
    """Load all conversations from DynamoDB - refreshes every 30 seconds"""
    try:
        clients = get_aws_clients()
        response = clients['conversations'].scan()
        conversations = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = clients['conversations'].scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            conversations.extend(response.get('Items', []))
        
        # Filter out language preferences
        conversations = [c for c in conversations if c.get('timestamp') != 'language_preference']
        return conversations
    except Exception as e:
        st.error(f"Error loading conversations: {e}")
        return []

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_knowledge_graph_data():
    """Load knowledge graph demo data"""
    try:
        with open('../demo/knowledge_graph_dummy_data.json', 'r') as f:
            return json.load(f)
    except:
        return {"farmers": [], "villages": []}

# Auto-refresh functionality
def add_auto_refresh(interval_seconds=30):
    """Add auto-refresh to the page"""
    st.markdown(
        f"""
        <script>
            setTimeout(function(){{
                window.location.reload();
            }}, {interval_seconds * 1000});
        </script>
        """,
        unsafe_allow_html=True
    )

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label {
        font-size: 1rem;
        color: #94a3b8;
        text-transform: uppercase;
    }
    .refresh-indicator {
        position: fixed;
        top: 10px;
        right: 10px;
        background: #10b981;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        z-index: 9999;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🌾 KisaanMitra.AI</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #94a3b8; font-size: 1.2rem; margin-bottom: 2rem;">Real-time Analytics & Farmer Intelligence Dashboard</div>', unsafe_allow_html=True)

# Add refresh indicator
current_time = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="refresh-indicator">🔄 Live • Updated: {current_time}</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🌾 KisaanMitra.AI")
    st.markdown("*Empowering Farmers with AI*")
    st.markdown("---")
    
    page = st.radio(
        "📍 Navigation",
        ["📊 Overview", "👥 Farmers", "💬 Conversations", "🌐 Knowledge Graph"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=True)
    
    if auto_refresh:
        add_auto_refresh(30)
    
    # Manual refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚡ Live Stats")
    
    # Load real-time data
    farmers = load_all_farmers()
    conversations = load_conversations()
    
    st.metric("🌾 Farmers", len(farmers))
    st.metric("💬 Messages", len(conversations))
    st.metric("🕐 Last Update", current_time)
    
    st.markdown("---")
    st.success("✅ All Systems Operational")

# Main content
if page == "📊 Overview":
    # Load dynamic data
    farmers = load_all_farmers()
    conversations = load_conversations()
    kg_data = load_knowledge_graph_data()
    
    # Calculate metrics
    total_farmers = len(farmers) + len(kg_data.get('farmers', []))
    unique_villages = len(set(f.get('village', '') for f in farmers))
    total_conversations = len(conversations)
    unique_users = len(set(c.get('user_id', '') for c in conversations))
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">👥</div>
            <div class="stat-number">{total_farmers}</div>
            <div class="stat-label">Total Farmers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🏘️</div>
            <div class="stat-number">{unique_villages}</div>
            <div class="stat-label">Villages</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">💬</div>
            <div class="stat-number">{total_conversations}</div>
            <div class="stat-label">Total Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">👤</div>
            <div class="stat-number">{unique_users}</div>
            <div class="stat-label">Active Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Crop Distribution
    st.markdown("### 🌾 Crop Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Calculate crop distribution from real data
        crop_counts = {}
        for farmer in farmers:
            crops = farmer.get('current_crops', '')
            if crops:
                for crop in crops.split(','):
                    crop = crop.strip()
                    if crop:
                        crop_counts[crop] = crop_counts.get(crop, 0) + 1
        
        if crop_counts:
            crop_df = pd.DataFrame(list(crop_counts.items()), columns=['Crop', 'Farmers'])
            crop_df = crop_df.sort_values('Farmers', ascending=False).head(6)
            
            fig = px.pie(crop_df, values='Farmers', names='Crop', hole=0.4,
                         color_discrete_sequence=['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5', '#f0fdfa'])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9', size=14),
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No crop data available yet")
    
    with col2:
        # Land distribution
        land_by_crop = {}
        for farmer in farmers:
            crops = farmer.get('current_crops', '')
            land = float(farmer.get('land_acres', 0))
            if crops and land > 0:
                crops_list = [c.strip() for c in crops.split(',')]
                land_per_crop = land / len(crops_list)
                for crop in crops_list:
                    land_by_crop[crop] = land_by_crop.get(crop, 0) + land_per_crop
        
        if land_by_crop:
            land_df = pd.DataFrame(list(land_by_crop.items()), columns=['Crop', 'Land (acres)'])
            land_df = land_df.sort_values('Land (acres)', ascending=False).head(6)
            
            fig = px.bar(land_df, x='Crop', y='Land (acres)',
                         color='Land (acres)',
                         color_continuous_scale=['#0f172a', '#10b981', '#34d399'])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9', size=14),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#334155'),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No land data available yet")

elif page == "👥 Farmers":
    st.markdown("### 👥 All Registered Farmers (Live Data)")
    
    # Load dynamic data
    farmers = load_all_farmers()
    
    if farmers:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_land = sum(float(f.get('land_acres', 0)) for f in farmers)
        avg_land = total_land / len(farmers) if farmers else 0
        unique_villages = len(set(f.get('village', '') for f in farmers))
        unique_districts = len(set(f.get('district', '') for f in farmers))
        
        with col1:
            st.metric("👥 Total Farmers", len(farmers))
        with col2:
            st.metric("📏 Total Land", f"{total_land:.0f} acres")
        with col3:
            st.metric("📊 Avg Land", f"{avg_land:.1f} acres")
        with col4:
            st.metric("🏘️ Villages", unique_villages)
        
        st.markdown("---")
        
        # Create dataframe
        df_data = []
        for farmer in farmers:
            phone = farmer.get('user_id', 'N/A')
            if phone != 'N/A' and not phone.startswith('+'):
                phone = f'+{phone}'
            
            df_data.append({
                'Name': farmer.get('name', 'Unknown'),
                'Phone': phone,
                'Village': farmer.get('village', 'N/A'),
                'District': farmer.get('district', 'N/A'),
                'Crops': farmer.get('current_crops', 'N/A'),
                'Land (acres)': float(farmer.get('land_acres', 0)),
                'Experience': farmer.get('experience', 'N/A'),
                'Registered': farmer.get('registered_at', 'N/A')[:10] if farmer.get('registered_at') else 'N/A'
            })
        
        df = pd.DataFrame(df_data)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            villages = sorted(df['Village'].unique())
            filter_village = st.selectbox("Filter by Village", ["All"] + list(villages))
        with col2:
            districts = sorted(df['District'].unique())
            filter_district = st.selectbox("Filter by District", ["All"] + list(districts))
        
        # Apply filters
        filtered_df = df
        if filter_village != "All":
            filtered_df = filtered_df[filtered_df['Village'] == filter_village]
        if filter_district != "All":
            filtered_df = filtered_df[filtered_df['District'] == filter_district]
        
        st.markdown(f"**Showing {len(filtered_df)} farmers**")
        
        # Display table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=500,
            column_config={
                "Land (acres)": st.column_config.NumberColumn("Land (acres)", format="%.1f")
            }
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"farmers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("🌾 No farmers registered yet. Farmers will appear here after completing onboarding.")

elif page == "💬 Conversations":
    st.markdown("### 💬 Live Conversations")
    
    # Load dynamic data
    conversations = load_conversations()
    
    if conversations:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        unique_users = len(set(c.get('user_id', '') for c in conversations))
        avg_per_user = len(conversations) / unique_users if unique_users > 0 else 0
        
        # Count recent (last hour)
        one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        recent_count = len([c for c in conversations if c.get('timestamp', '') > one_hour_ago])
        
        with col1:
            st.metric("💬 Total Messages", len(conversations))
        with col2:
            st.metric("👥 Unique Users", unique_users)
        with col3:
            st.metric("📊 Avg/User", f"{avg_per_user:.1f}")
        with col4:
            st.metric("🕐 Last Hour", recent_count)
        
        st.markdown("---")
        
        # Show recent conversations
        sorted_convs = sorted(conversations, key=lambda x: x.get('timestamp', ''), reverse=True)[:20]
        
        for conv in sorted_convs:
            timestamp = conv.get('timestamp', '')[:19].replace('T', ' ')
            user_id_short = conv.get('user_id', 'Unknown')[-10:]
            
            with st.expander(f"🗨️ {user_id_short} • {timestamp} • {conv.get('agent', 'unknown')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**👤 User:**")
                    st.info(conv.get('message', 'N/A'))
                with col2:
                    st.markdown("**🤖 Bot:**")
                    response = conv.get('response', 'N/A')
                    if len(response) > 300:
                        response = response[:300] + "..."
                    st.success(response)
    else:
        st.info("💬 No conversations yet. Start chatting with the bot to see conversations here!")

elif page == "🌐 Knowledge Graph":
    st.markdown("### 🌐 Hyperlocal Knowledge Graph")
    
    kg_data = load_knowledge_graph_data()
    farmers = kg_data.get('farmers', [])
    
    if farmers:
        col1, col2, col3, col4 = st.columns(4)
        
        districts = len(set(f.get('district', '') for f in farmers))
        villages = len(set(f.get('village_name', '') for f in farmers))
        total_land = sum(float(f.get('land_size_acres', 0)) for f in farmers)
        
        with col1:
            st.metric("👥 Farmers", len(farmers))
        with col2:
            st.metric("🏛️ Districts", districts)
        with col3:
            st.metric("🏘️ Villages", villages)
        with col4:
            st.metric("📏 Total Land", f"{total_land:.0f} acres")
        
        st.markdown("---")
        st.info("🌐 **Live Dashboard:** http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com")
    else:
        st.info("No knowledge graph data available")

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #64748b; font-size: 0.9rem;'>Last refreshed: {current_time} • Auto-refresh: {'ON' if auto_refresh else 'OFF'}</div>", unsafe_allow_html=True)
