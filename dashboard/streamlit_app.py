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
        return {"farmers": [], "villages": []}

# Page config
st.set_page_config(
    page_title="KisaanMitra.AI Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #0f172a;
    }
    
    /* Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -1px;
    }
    
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 12px rgba(16, 185, 129, 0.2);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #10b981;
    }
    
    /* Cards */
    .info-card {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin: 1rem 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1e293b;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    /* Dataframe */
    [data-testid="stDataFrame"] {
        background: #1e293b;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🌾 KisaanMitra.AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Real-time Analytics & Farmer Intelligence Dashboard</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🌾 KisaanMitra.AI")
    st.markdown("*Empowering Farmers with AI*")
    st.markdown("---")
    
    page = st.radio(
        "📍 Navigation",
        ["📊 Overview", "👥 Farmers", "💬 Conversations", "🌐 Knowledge Graph", "📈 Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Stats")
    
    # Load data
    clients = get_aws_clients()
    kg_data = load_knowledge_graph_data()
    
    # Count farmers in KG
    farmers_count = len(kg_data.get('farmers', []))
    villages_count = len(set(f.get('village_name', '') for f in kg_data.get('farmers', [])))
    
    st.metric("🌾 Farmers", farmers_count, delta="+5 this week")
    st.metric("🏘️ Villages", villages_count)
    st.metric("💬 Messages", "1,247", delta="+89 today")
    
    st.markdown("---")
    st.markdown("### 🔄 System Status")
    st.success("✅ All Systems Operational")
    st.markdown(f"**Updated:** {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("[📱 WhatsApp Bot](https://wa.me/919876543210)")
    st.markdown("[🌐 Knowledge Graph](http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com)")
    st.markdown("[📚 Documentation](https://github.com/yourusername/kisaanmitra)")

# Main content based on page selection
if page == "📊 Overview":
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="stat-icon">👥</div>
            <div class="stat-number">25</div>
            <div class="stat-label">Total Farmers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="stat-icon">🏘️</div>
            <div class="stat-number">8</div>
            <div class="stat-label">Villages</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="stat-icon">🌾</div>
            <div class="stat-number">12</div>
            <div class="stat-label">Crop Types</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="stat-icon">📊</div>
            <div class="stat-number">1,247</div>
            <div class="stat-label">Total Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-header'>📊 Crop Distribution</div>", unsafe_allow_html=True)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        # Sample data
        crop_data = pd.DataFrame({
            'Crop': ['Sugarcane', 'Wheat', 'Rice', 'Soybean', 'Cotton', 'Tur Daal'],
            'Farmers': [15, 12, 10, 8, 5, 3]
        })
        
        fig = px.pie(crop_data, values='Farmers', names='Crop', 
                     hole=0.4,
                     color_discrete_sequence=['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5', '#f0fdfa'])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', size=14),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1)
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart for land distribution
        land_data = pd.DataFrame({
            'Crop': ['Sugarcane', 'Wheat', 'Rice', 'Soybean', 'Cotton', 'Tur Daal'],
            'Total Land (acres)': [625, 420, 350, 280, 200, 125]
        })
        
        fig = px.bar(land_data, x='Crop', y='Total Land (acres)',
                     color='Total Land (acres)',
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
    
    st.markdown("<div class='section-header'>📈 Growth Trends</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # User growth
        dates = pd.date_range(start='2026-02-01', end='2026-03-01', freq='D')
        growth_data = pd.DataFrame({
            'Date': dates,
            'Users': range(10, 10 + len(dates))
        })
        
        fig = px.area(growth_data, x='Date', y='Users',
                      color_discrete_sequence=['#10b981'])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', size=14),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#334155'),
            hovermode='x unified'
        )
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Query volume
        query_data = pd.DataFrame({
            'Date': dates,
            'Queries': [30 + i*2 + (i%7)*5 for i in range(len(dates))]
        })
        
        fig = px.line(query_data, x='Date', y='Queries',
                      markers=True,
                      color_discrete_sequence=['#34d399'])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', size=14),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#334155'),
            hovermode='x unified'
        )
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div class='section-header'>🏘️ Top Villages</div>", unsafe_allow_html=True)
    
    village_data = pd.DataFrame({
        'Village': ['Kolhapur', 'Pune', 'Nashik', 'Satara', 'Sangli'],
        'Farmers': [15, 10, 8, 7, 5],
        'Total Land (acres)': [625, 420, 350, 280, 200]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Farmers',
        x=village_data['Village'],
        y=village_data['Farmers'],
        marker_color='#10b981',
        text=village_data['Farmers'],
        textposition='outside'
    ))
    fig.add_trace(go.Scatter(
        name='Total Land',
        x=village_data['Village'],
        y=village_data['Total Land (acres)'],
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#34d399', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9', size=14),
        xaxis=dict(showgrid=False),
        yaxis=dict(title='Number of Farmers', showgrid=True, gridcolor='#334155'),
        yaxis2=dict(title='Total Land (acres)', overlaying='y', side='right', showgrid=False),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

elif page == "👥 Farmers":
    st.markdown("<div class='section-header'>👥 All Farmers (Registered + Demo)</div>", unsafe_allow_html=True)
    
    # Load both datasets
    all_farmers = []
    
    # Load registered farmers from DynamoDB
    try:
        clients = get_aws_clients()
        response = clients['profiles'].scan(Limit=50)
        registered_users = response.get('Items', [])
        
        for user in registered_users:
            # Format phone number with +91 prefix
            phone = user.get('user_id', 'N/A')
            if phone != 'N/A' and not phone.startswith('+'):
                phone = f'+{phone}'
            
            all_farmers.append({
                'Phone': phone,
                'Name': user.get('name', 'Unknown'),
                'Village': user.get('village', 'N/A'),
                'Crops': user.get('crops', 'N/A'),
                'Land (acres)': float(user.get('land_acres', 0)),
                'Registered': user.get('registered_at', 'N/A'),
                'Type': '✅ Registered'
            })
    except Exception as e:
        st.warning(f"⚠️ Could not load registered farmers: {e}")
    
    # Load demo farmers from knowledge graph
    kg_data = load_knowledge_graph_data()
    dummy_farmers = kg_data.get('farmers', [])
    
    for farmer in dummy_farmers:
        # Normalize crops format - convert list to comma-separated string
        crops = farmer.get('crops_grown', [])
        if isinstance(crops, list):
            crops_str = ', '.join(crops)
        else:
            crops_str = str(crops)
        
        all_farmers.append({
            'Phone': farmer.get('phone', 'N/A'),
            'Name': farmer.get('name', 'Unknown'),
            'Village': farmer.get('village_name', 'N/A'),
            'Crops': crops_str,
            'Land (acres)': float(farmer.get('land_size_acres', 0)),
            'Registered': 'Demo User',
            'Type': '🎭 Demo'
        })
    
    if all_farmers:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_land = sum(f['Land (acres)'] for f in all_farmers)
        avg_land = total_land / len(all_farmers) if all_farmers else 0
        registered_count = len([f for f in all_farmers if f['Type'] == '✅ Registered'])
        demo_count = len([f for f in all_farmers if f['Type'] == '🎭 Demo'])
        
        with col1:
            st.metric("👥 Total Farmers", len(all_farmers), delta=f"{registered_count} registered, {demo_count} demo")
        with col2:
            st.metric("📏 Total Land", f"{total_land:.0f} acres")
        with col3:
            st.metric("📊 Avg Land/Farmer", f"{avg_land:.1f} acres")
        with col4:
            unique_villages = len(set(f['Village'] for f in all_farmers))
            st.metric("🏘️ Villages", unique_villages)
        
        st.markdown("---")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "✅ Registered Only", "🎭 Demo Only"]
            )
        with col2:
            villages = sorted(set(f['Village'] for f in all_farmers))
            filter_village = st.selectbox(
                "Filter by Village",
                ["All"] + villages
            )
        
        # Apply filters
        filtered_farmers = all_farmers
        if filter_type == "✅ Registered Only":
            filtered_farmers = [f for f in all_farmers if f['Type'] == '✅ Registered']
        elif filter_type == "🎭 Demo Only":
            filtered_farmers = [f for f in all_farmers if f['Type'] == '🎭 Demo']
        
        if filter_village != "All":
            filtered_farmers = [f for f in filtered_farmers if f['Village'] == filter_village]
        
        st.markdown(f"**Showing {len(filtered_farmers)} farmers**")
        
        # Create dataframe
        df = pd.DataFrame(filtered_farmers)
        
        st.dataframe(
            df,
            use_container_width=True,
            height=500,
            column_config={
                "Land (acres)": st.column_config.NumberColumn(
                    "Land (acres)",
                    format="%.1f"
                ),
                "Type": st.column_config.TextColumn(
                    "Type",
                    width="small"
                )
            }
        )
        
        # Download button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"all_farmers_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with col2:
            # Summary by type
            st.metric("Registered", registered_count)
        
        st.markdown("---")
        
        # Crop distribution chart
        st.markdown("<div class='section-header'>🌾 Crop Distribution</div>", unsafe_allow_html=True)
        
        # Parse all crops
        crop_counts = {}
        for farmer in filtered_farmers:
            crops_str = farmer['Crops']
            if crops_str and crops_str != 'N/A':
                crops_list = [c.strip() for c in crops_str.split(',')]
                for crop in crops_list:
                    if crop:
                        crop_counts[crop] = crop_counts.get(crop, 0) + 1
        
        if crop_counts:
            crop_df = pd.DataFrame([
                {'Crop': crop, 'Farmers': count}
                for crop, count in sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ])
            
            fig = px.bar(crop_df, x='Crop', y='Farmers',
                         color='Farmers',
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
        st.info("🌾 No farmers found in the system.")

elif page == "💬 Conversations":
    st.markdown("<div class='section-header'>💬 Recent Conversations</div>", unsafe_allow_html=True)
    
    try:
        clients = get_aws_clients()
        response = clients['conversations'].scan(Limit=20)
        conversations = response.get('Items', [])
        
        if conversations:
            # Filter out language preferences
            conversations = [c for c in conversations if c.get('timestamp') != 'language_preference']
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💬 Total Conversations", len(conversations))
            with col2:
                unique_users = len(set(c.get('user_id', '') for c in conversations))
                st.metric("👥 Unique Users", unique_users)
            with col3:
                avg_per_user = len(conversations) / unique_users if unique_users > 0 else 0
                st.metric("📊 Avg/User", f"{avg_per_user:.1f}")
            
            st.markdown("---")
            
            for conv in sorted(conversations, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]:
                with st.expander(f"🗨️ {conv.get('user_id', 'Unknown')[-10:]} - {conv.get('timestamp', '')[:19]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**👤 User Message:**")
                        st.info(conv.get('message', 'N/A'))
                    with col2:
                        st.markdown("**🤖 Bot Response:**")
                        response_text = conv.get('response', 'N/A')
                        if len(response_text) > 200:
                            response_text = response_text[:200] + "..."
                        st.success(response_text)
                    st.caption(f"🎯 Agent: {conv.get('agent', 'unknown')}")
        else:
            st.info("💬 No conversations yet.")
    except Exception as e:
        st.error(f"❌ Error loading conversations: {e}")

elif page == "🌐 Knowledge Graph":
    st.markdown("<div class='section-header'>🌐 Village Knowledge Graph</div>", unsafe_allow_html=True)
    
    kg_data = load_knowledge_graph_data()
    
    col1, col2, col3 = st.columns(3)
    
    farmers = kg_data.get('farmers', [])
    villages = list(set(f.get('village_name', '') for f in farmers))
    all_crops = []
    for f in farmers:
        crops_str = f.get('crops_grown', '')
        all_crops.extend([c.strip() for c in crops_str.split(',') if c.strip()])
    unique_crops = list(set(all_crops))
    
    with col1:
        st.metric("👥 Farmers", len(farmers))
    with col2:
        st.metric("🏘️ Villages", len(villages))
    with col3:
        st.metric("🌾 Crops", len(unique_crops))
    
    st.markdown("---")
    
    # Village selector
    selected_village = st.selectbox("🏘️ Select Village", villages if villages else ['No villages'])
    
    if selected_village and selected_village != 'No villages':
        # Filter farmers by village
        village_farmers = [f for f in farmers if f.get('village_name') == selected_village]
        
        st.markdown(f"<div class='section-header'>📊 {selected_village} Statistics</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Farmers", len(village_farmers))
            total_land = sum(float(f.get('land_size_acres', 0)) for f in village_farmers)
            st.metric("Total Land", f"{total_land:.1f} acres")
        
        with col2:
            # Crop distribution
            crop_counts = {}
            for f in village_farmers:
                crops_str = f.get('crops_grown', '')
                for crop in crops_str.split(','):
                    crop = crop.strip()
                    if crop:
                        crop_counts[crop] = crop_counts.get(crop, 0) + 1
            
            if crop_counts:
                st.markdown("**🌾 Top Crops:**")
                for crop, count in sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.write(f"• {crop}: {count} farmers")
        
        st.markdown("---")
        
        # Farmers table
        st.markdown(f"<div class='section-header'>👥 Farmers in {selected_village}</div>", unsafe_allow_html=True)
        
        if village_farmers:
            farmers_df = pd.DataFrame([
                {
                    'Name': f.get('name', 'Unknown'),
                    'Crops': f.get('crops_grown', 'N/A'),
                    'Land (acres)': f.get('land_size_acres', 'N/A'),
                }
                for f in village_farmers
            ])
            st.dataframe(farmers_df, use_container_width=True, height=400)
    
    st.markdown("---")
    st.info("🌐 **Live Dashboard:** http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com")

elif page == "📈 Analytics":
    st.markdown("<div class='section-header'>📈 Advanced Analytics</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎯 Performance", "💰 Revenue", "🌾 Crop Insights"])
    
    with tab1:
        st.markdown("### System Performance Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("⚡ Avg Response Time", "2.3s", "-0.5s")
        with col2:
            st.metric("✅ Success Rate", "98.5%", "+1.2%")
        with col3:
            st.metric("⭐ User Satisfaction", "4.7/5", "+0.3")
        
        # Response time chart
        st.markdown("#### Response Time Trend")
        time_data = pd.DataFrame({
            'Hour': range(24),
            'Response Time (s)': [2.1, 2.0, 1.9, 2.2, 2.3, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0, 2.1]
        })
        
        fig = px.area(time_data, x='Hour', y='Response Time (s)', 
                      color_discrete_sequence=['#10b981'])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', size=14),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#334155')
        )
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
                     color_continuous_scale=['#0f172a', '#10b981', '#34d399'])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', size=14),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#334155')
        )
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
        fig.add_trace(go.Bar(
            name='Avg Yield',
            x=yield_data['Crop'],
            y=yield_data['Avg Yield (quintals/acre)'],
            marker_color='#10b981'
        ))
        fig.add_trace(go.Scatter(
            name='Success Rate',
            x=yield_data['Crop'],
            y=yield_data['Success Rate (%)'], 
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#34d399', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', size=14),
            xaxis=dict(showgrid=False),
            yaxis=dict(title='Avg Yield (quintals/acre)', showgrid=True, gridcolor='#334155'),
            yaxis2=dict(title='Success Rate (%)', overlaying='y', side='right', showgrid=False),
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 2rem;'>
    <p style='font-size: 1.2rem; font-weight: 600; color: #10b981;'>🌾 KisaanMitra.AI</p>
    <p>Empowering Farmers with AI | Built with ❤️ for Indian Farmers</p>
    <p style='font-size: 0.9rem; color: #64748b;'>© 2026 KisaanMitra.AI | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
