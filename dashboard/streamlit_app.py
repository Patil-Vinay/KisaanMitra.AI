"""
KisaanMitra Knowledge Graph Dashboard
Streamlit app to visualize village-level farmer data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import subprocess

# Page configuration
st.set_page_config(
    page_title="KisaanMitra Knowledge Graph",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E7D32;
    }
    .village-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0


def load_user_profiles():
    """Load all user profiles from DynamoDB using AWS CLI"""
    try:
        result = subprocess.run(
            ["aws", "dynamodb", "scan", "--table-name", "kisaanmitra-user-profiles", "--region", "ap-south-1"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        
        # Convert DynamoDB format to simple dict
        profiles = []
        for item in data.get("Items", []):
            profile = {}
            for key, value in item.items():
                # Extract value from DynamoDB format
                if "S" in value:
                    profile[key] = value["S"]
                elif "N" in value:
                    profile[key] = float(value["N"])
                elif "BOOL" in value:
                    profile[key] = value["BOOL"]
            profiles.append(profile)
        
        return profiles
    except Exception as e:
        st.error(f"Error loading profiles: {e}")
        return []


def load_graph_data(profiles):
    """Build graph data from user profiles"""
    nodes = []
    edges = []
    villages = set()
    crops = set()
    
    # Create nodes and edges from profiles
    for profile in profiles:
        user_id = profile.get("user_id", "")
        name = profile.get("name", "Unknown")
        village = profile.get("village", "Unknown")
        crops_str = profile.get("crops", "")
        
        # Add farmer node
        nodes.append({
            "id": user_id,
            "label": name,
            "type": "farmer"
        })
        
        # Add village node
        if village and village != "Unknown":
            villages.add(village)
            edges.append({
                "source": user_id,
                "target": f"village_{village}",
                "label": "lives_in"
            })
        
        # Add crop nodes
        if crops_str:
            for crop in crops_str.split(","):
                crop = crop.strip()
                if crop:
                    crops.add(crop)
                    edges.append({
                        "source": user_id,
                        "target": f"crop_{crop}",
                        "label": "grows"
                    })
    
    # Add village nodes
    for village in villages:
        nodes.append({
            "id": f"village_{village}",
            "label": village,
            "type": "village"
        })
    
    # Add crop nodes
    for crop in crops:
        nodes.append({
            "id": f"crop_{crop}",
            "label": crop,
            "type": "crop"
        })
    
    # Build summary
    summary = {
        "total_farmers": len([n for n in nodes if n["type"] == "farmer"]),
        "total_villages": len(villages),
        "total_crops": len(crops),
        "villages": list(villages)
    }
    
    return summary, {"nodes": nodes, "edges": edges}


def get_village_statistics(village, profiles):
    """Get statistics for a specific village"""
    village_profiles = [p for p in profiles if p.get("village") == village]
    
    crops_grown = {}
    total_land = 0
    
    for profile in village_profiles:
        land = float(profile.get("land_acres", 0))
        total_land += land
        
        crops_str = profile.get("crops", "")
        for crop in crops_str.split(","):
            crop = crop.strip()
            if crop:
                crops_grown[crop] = crops_grown.get(crop, 0) + 1
    
    return {
        "farmer_count": len(village_profiles),
        "total_land_acres": total_land,
        "crops_grown": crops_grown
    }


def create_network_graph(graph_data):
    """Create interactive network graph using Plotly"""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    
    if not nodes:
        st.warning("No data in knowledge graph yet. Onboard farmers to see the graph.")
        return None
    
    # Create node positions (simple circular layout)
    import math
    n = len(nodes)
    node_positions = {}
    
    # Separate nodes by type
    farmers = [n for n in nodes if n["type"] == "farmer"]
    villages = [n for n in nodes if n["type"] == "village"]
    crops = [n for n in nodes if n["type"] == "crop"]
    
    # Position villages in center
    for i, node in enumerate(villages):
        angle = 2 * math.pi * i / max(len(villages), 1)
        node_positions[node["id"]] = (math.cos(angle) * 2, math.sin(angle) * 2)
    
    # Position farmers around villages
    for i, node in enumerate(farmers):
        angle = 2 * math.pi * i / max(len(farmers), 1)
        node_positions[node["id"]] = (math.cos(angle) * 5, math.sin(angle) * 5)
    
    # Position crops on outer ring
    for i, node in enumerate(crops):
        angle = 2 * math.pi * i / max(len(crops), 1)
        node_positions[node["id"]] = (math.cos(angle) * 8, math.sin(angle) * 8)
    
    # Create edge traces
    edge_traces = []
    for edge in edges:
        source_id = edge.get("source")
        target_id = edge.get("target")
        
        if source_id in node_positions and target_id in node_positions:
            x0, y0 = node_positions[source_id]
            x1, y1 = node_positions[target_id]
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=1, color='#888'),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
    
    # Create node traces by type
    node_traces = {}
    colors = {"farmer": "#4CAF50", "village": "#2196F3", "crop": "#FF9800"}
    symbols = {"farmer": "circle", "village": "square", "crop": "diamond"}
    
    for node_type in ["farmer", "village", "crop"]:
        type_nodes = [n for n in nodes if n["type"] == node_type]
        
        if type_nodes:
            x_vals = [node_positions[n["id"]][0] for n in type_nodes]
            y_vals = [node_positions[n["id"]][1] for n in type_nodes]
            labels = [n["label"] for n in type_nodes]
            
            node_trace = go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers+text',
                marker=dict(
                    size=20 if node_type == "village" else 15,
                    color=colors[node_type],
                    symbol=symbols[node_type],
                    line=dict(width=2, color='white')
                ),
                text=labels,
                textposition="top center",
                textfont=dict(size=10),
                name=node_type.capitalize(),
                hoverinfo='text',
                hovertext=labels
            )
            node_traces[node_type] = node_trace
    
    # Create figure
    fig = go.Figure(data=edge_traces + list(node_traces.values()))
    
    fig.update_layout(
        title="Village Knowledge Graph",
        showlegend=True,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<div class="main-header">🌾 KisaanMitra Knowledge Graph Dashboard</div>', unsafe_allow_html=True)
    st.markdown("Real-time visualization of village-level farmer data")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.refresh_count += 1
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Dashboard Info")
        st.info(f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}")
        st.info(f"Refresh count: {st.session_state.refresh_count}")
        
        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        st.markdown("- [AWS Console](https://console.aws.amazon.com)")
        st.markdown("- [Neptune Console](https://console.aws.amazon.com/neptune)")
        st.markdown("- [DynamoDB Console](https://console.aws.amazon.com/dynamodb)")
    
    # Load data
    with st.spinner("Loading knowledge graph data..."):
        profiles = load_user_profiles()
        summary, graph_data = load_graph_data(profiles)
    
    # Overview metrics
    st.header("📈 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👨‍🌾 Total Farmers",
            value=summary.get("total_farmers", 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="🏘️ Villages",
            value=summary.get("total_villages", 0),
            delta=None
        )
    
    with col3:
        st.metric(
            label="🌾 Crops",
            value=summary.get("total_crops", 0),
            delta=None
        )
    
    with col4:
        total_land = sum(float(p.get("land_acres", 0)) for p in profiles)
        st.metric(
            label="📏 Total Land (acres)",
            value=f"{total_land:.1f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Two column layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Network graph
        st.header("🕸️ Knowledge Graph Network")
        fig = create_network_graph(graph_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        # Village breakdown
        st.header("🏘️ Villages")
        villages = summary.get("villages", [])
        
        if villages:
            for village in villages:
                with st.expander(f"📍 {village}", expanded=False):
                    village_stats = get_village_statistics(village, profiles)
                    st.metric("Farmers", village_stats.get("farmer_count", 0))
                    st.metric("Total Land", f"{village_stats.get('total_land_acres', 0):.1f} acres")
                    
                    crops = village_stats.get("crops_grown", {})
                    if crops:
                        st.markdown("**Crops:**")
                        for crop, count in crops.items():
                            st.markdown(f"- {crop}: {count} farmers")
        else:
            st.info("No villages registered yet")
    
    st.markdown("---")
    
    # Detailed tables
    tab1, tab2, tab3 = st.tabs(["👨‍🌾 Farmers", "🌾 Crops Analysis", "📊 Statistics"])
    
    with tab1:
        st.header("Farmer Profiles")
        
        if profiles:
            df = pd.DataFrame(profiles)
            
            # Select columns to display
            display_cols = ["name", "village", "crops", "land_acres", "phone", "registered_at"]
            available_cols = [col for col in display_cols if col in df.columns]
            
            if available_cols:
                df_display = df[available_cols].copy()
                df_display.columns = [col.replace("_", " ").title() for col in available_cols]
                
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download button
                csv = df_display.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"farmers_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No farmers registered yet. Start onboarding via WhatsApp!")
    
    with tab2:
        st.header("Crop Distribution")
        
        if profiles:
            # Aggregate crop data
            crop_counts = {}
            crop_land = {}
            
            for profile in profiles:
                crops = profile.get("crops", "").split(",")
                land = float(profile.get("land_acres", 0))
                
                for crop in crops:
                    crop = crop.strip()
                    if crop:
                        crop_counts[crop] = crop_counts.get(crop, 0) + 1
                        crop_land[crop] = crop_land.get(crop, 0) + land
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Crop count pie chart
                if crop_counts:
                    fig_count = px.pie(
                        values=list(crop_counts.values()),
                        names=list(crop_counts.keys()),
                        title="Farmers by Crop"
                    )
                    st.plotly_chart(fig_count, use_container_width=True)
            
            with col2:
                # Crop land bar chart
                if crop_land:
                    fig_land = px.bar(
                        x=list(crop_land.keys()),
                        y=list(crop_land.values()),
                        title="Land Distribution by Crop (acres)",
                        labels={"x": "Crop", "y": "Total Land (acres)"}
                    )
                    st.plotly_chart(fig_land, use_container_width=True)
        else:
            st.info("No crop data available yet")
    
    with tab3:
        st.header("Detailed Statistics")
        
        if profiles:
            # Village-wise statistics
            st.subheader("Village-wise Breakdown")
            
            village_data = []
            for village in summary.get("villages", []):
                stats = get_village_statistics(village, profiles)
                village_data.append({
                    "Village": village,
                    "Farmers": stats.get("farmer_count", 0),
                    "Total Land (acres)": stats.get("total_land_acres", 0),
                    "Crops": len(stats.get("crops_grown", {}))
                })
            
            if village_data:
                df_villages = pd.DataFrame(village_data)
                st.dataframe(df_villages, use_container_width=True, hide_index=True)
            
            # Registration timeline
            st.subheader("Registration Timeline")
            
            df = pd.DataFrame(profiles)
            if "registered_at" in df.columns:
                df["registered_date"] = pd.to_datetime(df["registered_at"]).dt.date
                registrations = df.groupby("registered_date").size().reset_index(name="count")
                
                fig_timeline = px.line(
                    registrations,
                    x="registered_date",
                    y="count",
                    title="Daily Farmer Registrations",
                    labels={"registered_date": "Date", "count": "Farmers"}
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No statistics available yet")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>KisaanMitra.AI - Village Knowledge Graph Dashboard</p>
            <p>Powered by Amazon Neptune & DynamoDB</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
