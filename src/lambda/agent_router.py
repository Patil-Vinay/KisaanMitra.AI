"""
LangGraph-based Multi-Agent Router for KisaanMitra
Uses AI to intelligently route messages to appropriate agents
"""

import json
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    """State shared across all agents"""
    user_message: str
    user_id: str
    selected_agent: str
    response: str
    context: dict


def create_router_graph(bedrock_client):
    """Create LangGraph workflow for agent routing"""
    
    # Define the routing node
    def route_to_agent(state: AgentState) -> AgentState:
        """Use AI to determine which agent should handle the message"""
        user_message = state["user_message"]
        
        routing_prompt = f"""You are a routing assistant for a farming chatbot. Analyze the user's message and decide which agent should handle it.

Available agents:
1. GREETING - For greetings like "hi", "hello", "hey"
2. CROP - For crop diseases, pests, plant health issues
3. MARKET - For market prices, mandi rates, selling advice
4. FINANCE - For budgets, loans, government schemes, costs
5. GENERAL - For general farming questions or casual conversation

User message: "{user_message}"

Reply with ONLY ONE WORD - the agent name (GREETING, CROP, MARKET, FINANCE, or GENERAL).
"""
        
        try:
            response = bedrock_client.converse(
                modelId="us.amazon.nova-micro-v1:0",
                messages=[{"role": "user", "content": [{"text": routing_prompt}]}],
                inferenceConfig={"maxTokens": 50, "temperature": 0.3}
            )
            
            agent_choice = response["output"]["message"]["content"][0]["text"].strip().upper()
            
            # Validate agent choice
            valid_agents = ["GREETING", "CROP", "MARKET", "FINANCE", "GENERAL"]
            if agent_choice not in valid_agents:
                agent_choice = "GENERAL"
            
            state["selected_agent"] = agent_choice.lower()
            print(f"AI Router selected: {agent_choice}")
            
        except Exception as e:
            print(f"Routing error: {e}, defaulting to GENERAL")
            state["selected_agent"] = "general"
        
        return state
    
    # Define conditional routing
    def should_route_to_greeting(state: AgentState) -> bool:
        return state["selected_agent"] == "greeting"
    
    def should_route_to_crop(state: AgentState) -> bool:
        return state["selected_agent"] == "crop"
    
    def should_route_to_market(state: AgentState) -> bool:
        return state["selected_agent"] == "market"
    
    def should_route_to_finance(state: AgentState) -> bool:
        return state["selected_agent"] == "finance"
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add the routing node
    workflow.add_node("router", route_to_agent)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional edges based on routing decision
    workflow.add_conditional_edges(
        "router",
        lambda state: state["selected_agent"],
        {
            "greeting": END,
            "crop": END,
            "market": END,
            "finance": END,
            "general": END
        }
    )
    
    return workflow.compile()


def route_message_with_ai(user_message: str, user_id: str, bedrock_client) -> str:
    """
    Use LangGraph to route message to appropriate agent
    
    Args:
        user_message: The user's input message
        user_id: User identifier
        bedrock_client: Boto3 Bedrock client
    
    Returns:
        Agent name (greeting, crop, market, finance, or general)
    """
    
    # Create initial state
    initial_state = AgentState(
        user_message=user_message,
        user_id=user_id,
        selected_agent="",
        response="",
        context={}
    )
    
    # Create and run the graph
    graph = create_router_graph(bedrock_client)
    
    try:
        result = graph.invoke(initial_state)
        return result["selected_agent"]
    except Exception as e:
        print(f"LangGraph routing error: {e}")
        return "general"


# Fallback keyword-based routing (if LangGraph fails)
def fallback_keyword_routing(user_message: str) -> str:
    """Simple keyword-based routing as fallback"""
    msg_lower = user_message.lower()
    
    greetings = ["hi", "hello", "hey", "namaste"]
    if any(greeting == msg_lower.strip() for greeting in greetings):
        return "greeting"
    
    crop_keywords = ["disease", "pest", "leaf", "yellow", "spots", "dying"]
    if any(kw in msg_lower for kw in crop_keywords):
        return "crop"
    
    market_keywords = ["price", "mandi", "rate", "sell", "market"]
    if any(kw in msg_lower for kw in market_keywords):
        return "market"
    
    finance_keywords = ["budget", "loan", "scheme", "money", "cost"]
    if any(kw in msg_lower for kw in finance_keywords):
        return "finance"
    
    return "general"
