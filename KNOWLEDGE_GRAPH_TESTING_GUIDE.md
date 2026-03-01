# Knowledge Graph Testing Guide 🌐

## What is the Knowledge Graph?

The Knowledge Graph is a village-level network that connects:
- **Farmers** (users who complete onboarding)
- **Villages** (locations where farmers live)
- **Crops** (what farmers grow)

It automatically builds relationships as farmers register, creating a community intelligence system.

## Current Status

### Live Demo Dashboard
🌐 **URL**: http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com

The dashboard shows:
- 50 farmers across 10 villages
- 15 different crops
- 500+ relationships
- Focus on Kolhapur sugarcane farmers (15 farmers)
- Statistics: 85% success rate, ₹4.15 Cr revenue, 461 quintals/acre avg yield

### How It Works

1. **Automatic Population**: When a user completes onboarding (name, crops, land, village), they're automatically added to the knowledge graph
2. **In-Memory Storage**: Currently uses local storage (no Neptune database needed)
3. **Relationships Created**:
   - Farmer → LIVES_IN → Village
   - Farmer → GROWS → Crop
   - Village ← HAS_FARMER ← Farmer

## WhatsApp Testing Questions

### 1. Complete Onboarding First
Before testing knowledge graph features, complete onboarding:

```
You: hi
Bot: Welcome message + asks for name

You: My name is Vinay Patil
Bot: Asks for crops

You: Sugarcane
Bot: Asks for land size

You: 50 acres
Bot: Asks for village

You: Kolhapur
Bot: Registration complete!
```

### 2. Questions to Test Knowledge Graph Benefits

Currently, the knowledge graph is **passively collecting data** but not actively used in responses. However, here are questions that SHOULD benefit from it (for demo purposes):

#### Village-Level Insights
```
"Who else in Kolhapur grows sugarcane?"
"How many farmers are in my village?"
"What crops do other farmers in Kolhapur grow?"
"Show me successful farmers in my area"
```

#### Crop-Specific Community
```
"Connect me with other sugarcane farmers"
"What's the average yield for sugarcane in my village?"
"Who has the best sugarcane results in Kolhapur?"
"How much land do other sugarcane farmers have?"
```

#### Best Practices Sharing
```
"What fertilizers do successful farmers in my village use?"
"Show me the top performing farmers for wheat"
"What's the average profit for tomato farmers in Maharashtra?"
```

#### Market Intelligence
```
"Where are other farmers selling sugarcane?"
"What prices are farmers in my village getting?"
"Which mandi gives best rates for my crop?"
```

## Current Limitation ⚠️

**IMPORTANT**: The knowledge graph is currently **NOT integrated** into the AI responses. It only:
1. ✅ Collects farmer data during onboarding
2. ✅ Stores relationships in memory
3. ✅ Displays on the demo dashboard
4. ❌ Does NOT provide insights in WhatsApp responses yet

## To Fully Activate Knowledge Graph

To make the knowledge graph actually answer these questions, we need to:

### Option 1: Add Knowledge Graph Query Function
```python
def query_knowledge_graph(user_id, query_type, params):
    """Query knowledge graph for insights"""
    if query_type == "village_farmers":
        return knowledge_graph.get_village_farmers(params['village'])
    elif query_type == "crop_farmers":
        return knowledge_graph.get_crop_farmers(params['crop'])
    elif query_type == "village_stats":
        return knowledge_graph.get_village_statistics(params['village'])
```

### Option 2: Integrate with AI Orchestrator
Add knowledge graph context to AI prompts:
```python
# Get user's village
profile = onboarding_manager.get_user_profile(user_id)
village = profile.get('village')

# Get village insights
village_stats = knowledge_graph.get_village_statistics(village)

# Add to AI context
context = f"""
User is from {village} village.
Village has {village_stats['farmer_count']} farmers.
Common crops: {', '.join(village_stats['crops_grown'].keys())}
Total land: {village_stats['total_land_acres']} acres
"""
```

### Option 3: Create Knowledge Graph Agent
Add a new agent specifically for community insights:
```python
def handle_community_query(user_message, user_id):
    """Handle knowledge graph queries"""
    profile = onboarding_manager.get_user_profile(user_id)
    
    if "farmers in my village" in user_message.lower():
        farmers = knowledge_graph.get_village_farmers(profile['village'])
        return format_farmer_list(farmers)
    
    elif "grows" in user_message.lower():
        crop = extract_crop_with_ai(user_message)
        farmers = knowledge_graph.get_crop_farmers(crop)
        return format_crop_farmers(farmers)
```

## Demo Strategy for Examiners

### Show the Dashboard First
1. Open: http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com
2. Explain: "This is our village-level knowledge graph with 50 farmers"
3. Point out: Kolhapur sugarcane cluster (15 farmers)
4. Highlight: Interactive graph (drag nodes, see connections)

### Then Show WhatsApp Integration
1. Complete onboarding for a new farmer
2. Explain: "This farmer is now automatically added to the knowledge graph"
3. Refresh dashboard to show new farmer (if time permits)
4. Explain future capabilities: "Soon farmers can query this network for insights"

### Key Talking Points
- **Automatic Network Building**: No manual data entry, grows organically
- **Village-Level Intelligence**: Hyperlocal insights, not generic advice
- **Community Learning**: Farmers learn from successful neighbors
- **Scalability**: Can handle thousands of farmers across hundreds of villages
- **Real-Time Updates**: Graph updates as farmers register and share data

## Quick Test Commands

### Check if user is in graph (backend)
```bash
# This would query the knowledge graph
python -c "from src.knowledge_graph.village_graph import knowledge_graph; print(knowledge_graph.get_all_villages())"
```

### View graph summary
```bash
python -c "from src.knowledge_graph.village_graph import knowledge_graph; import json; print(json.dumps(knowledge_graph.get_graph_summary(), indent=2))"
```

## Next Steps to Activate

Would you like me to:
1. **Integrate knowledge graph into AI responses** (add context to all queries)
2. **Create a community insights agent** (dedicated agent for graph queries)
3. **Add graph query commands** (specific commands like "/village" or "/farmers")
4. **Build recommendation engine** (suggest best practices from successful farmers)

Let me know which approach you prefer!

---
**Status**: Knowledge graph is collecting data but not yet providing insights in WhatsApp
**Demo Dashboard**: http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com
