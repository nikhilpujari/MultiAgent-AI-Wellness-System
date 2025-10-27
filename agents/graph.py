from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from agents.router import RouterAgent
from agents.fitness_coach import FitnessCoachAgent
from agents.nutrition_specialist import NutritionAgent
from agents.doctor_avatar import DoctorAgent
from agents.tracking_viz import TrackingAgent
from agents.general_agent import GeneralAgent
from agents.api_tool_agent import APIToolAgent


# 🧠 Shared state definition
class GraphState(BaseModel):
    user: str = Field(default="")
    messages: list = Field(default_factory=list)


# 🧩 Instantiate agents
router = RouterAgent()
fitness = FitnessCoachAgent()
nutrition = NutritionAgent()
doctor = DoctorAgent()
tracking = TrackingAgent()
general = GeneralAgent()
api_tool = APIToolAgent()


# 🧠 Helper functions
def get_user_message(state: GraphState) -> str:
    """Extract the original user message from state"""
    for msg in state.messages:
        if msg.get("role") == "user":
            return msg["content"]
    return ""

def get_next_node(state: GraphState) -> str:
    """Determine next node from state messages"""
    for msg in reversed(state.messages):
        if msg.get("role") == "next_node":
            return msg["content"]
    return "__end__"

# 🧠 Node wrappers — each node must be callable
def router_node(state: GraphState) -> GraphState:
    user_message = state.messages[-1]["content"]
    import streamlit as st
    st.write(f"📍 GRAPH: Processing message")
    
    intent = router.route(user_message)
    st.write(f"➡️ GRAPH: Routing to '{intent}' agent")
    
    state.messages.append({"role": "system", "content": f"Intent detected: {intent}"})
    state.messages.append({"role": "next_node", "content": intent})
    
    return state


def fitness_node(state: GraphState) -> GraphState:
    user = state.user
    # Get the original user message, not the routing decision
    user_msg = None
    for msg in state.messages:
        if msg.get("role") == "user":
            user_msg = msg["content"]
    
    reply = fitness.respond(user, user_msg)
    state.messages.append({"role": "assistant", "content": reply})
    
    return state


def nutrition_node(state: GraphState) -> GraphState:
    user = state.user
    user_msg = get_user_message(state)
    
    import streamlit as st
    st.write(f"🍎 NUTRITION: Processing message")
    
    # Check if this needs food database lookup
    if api_tool.needs_food_lookup(user_msg):
        st.write(f"🍎 NUTRITION: Requesting API food lookup")
        
        # Extract food items for lookup
        food_items = api_tool.extract_food_items(user_msg)
        
        # Request API lookup
        state.messages.append({"role": "food_lookup_request", "content": food_items})
        state.messages.append({"role": "next_node", "content": "api_tool"})
        
        return state
    else:
        # Regular nutrition response without API lookup
        st.write(f"🍎 NUTRITION: Providing standard response")
        reply = nutrition.respond(user, user_msg)
        state.messages.append({"role": "assistant", "content": reply})
        # Explicitly set next_node to END for proper routing
        state.messages.append({"role": "next_node", "content": "__end__"})
        
        return state


def doctor_node(state: GraphState) -> GraphState:
    # Get the original user message, not the routing decision
    user_msg = None
    for msg in state.messages:
        if msg.get("role") == "user":
            user_msg = msg["content"]
    
    reply = doctor.respond(user_msg, state.user)
    state.messages.append({"role": "assistant", "content": reply})
    
    return state


def tracking_node(state: GraphState) -> GraphState:
    user = state.user
    reply = tracking.summarize(user)
    state.messages.append({"role": "assistant", "content": reply})
    return state


def api_tool_node(state: GraphState) -> GraphState:
    import streamlit as st
    st.write(f"🔍 API TOOL: Processing food lookup request")
    
    # Get the food query from nutrition agent
    food_query = None
    for msg in reversed(state.messages):
        if msg.get("role") == "food_lookup_request":
            food_query = msg["content"]
            break
    
    if food_query:
        # Look up food data
        food_data = api_tool.lookup_food(food_query)
        state.messages.append({"role": "food_data", "content": food_data})
        state.messages.append({"role": "next_node", "content": "nutrition_with_data"})
        
        st.write(f"🔍 API TOOL: Lookup complete, returning to nutrition agent")
    else:
        st.write(f"❌ API TOOL: No food query found")
        state.messages.append({"role": "next_node", "content": "nutrition_with_data"})
    
    return state


def nutrition_with_data_node(state: GraphState) -> GraphState:
    user = state.user
    user_msg = get_user_message(state)
    
    import streamlit as st
    st.write(f"🍎 NUTRITION: Generating response with API data")
    
    # Get the API data
    food_data = None
    for msg in reversed(state.messages):
        if msg.get("role") == "food_data":
            food_data = msg["content"]
            break
    
    # Generate response with real data
    if food_data:
        reply = nutrition.respond_with_api_data(user, user_msg, food_data)
    else:
        # Fallback to regular response
        reply = nutrition.respond(user, user_msg)
    
    state.messages.append({"role": "assistant", "content": reply})
    
    return state


def general_node(state: GraphState) -> GraphState:
    msg = state.messages[-1]["content"]
    
    # Check if this should be re-routed
    analysis_prompt = (
        f"Analyze this user message: '{msg}'\n\n"
        "Could this message be related to:\n"
        "- FITNESS (workouts, exercise, physical activity, sports, training)\n"
        "- NUTRITION (food, meals, eating, diet, calories, hunger)\n" 
        "- HEALTH (medical concerns, symptoms, mental health, anxiety, stress, sleep)\n\n"
        "If YES, respond with just: fitness, nutrition, or health\n"
        "If NO, respond with: out_of_domain"
    )
    
    from openai import OpenAI
    from app.config import settings
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    analysis = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[{"role": "user", "content": analysis_prompt}]
    ).choices[0].message.content.strip().lower()

    if analysis in ["fitness", "nutrition", "health"]:
        # Re-route to the correct agent
        if analysis == "fitness":
            reply = fitness.respond(state.user, msg)
        elif analysis == "nutrition":
            reply = nutrition.respond(state.user, msg)
        elif analysis == "health":
            reply = doctor.respond(msg)
        
        # Add a note about the re-routing
        reply = f"🔄 *[Re-routed to {analysis.title()}]*\n{reply}"
    else:
        # Handle out-of-domain queries
        reply = (
            f"🤖 *[Domain Helper]*\n"
            f"I'm specialized in fitness 🏋️, nutrition 🍎, and health 🩺 topics. "
            f"Your question seems to be outside these areas. "
            f"Could you ask me something related to workouts, meals, or health instead?"
        )
    
    state.messages.append({"role": "assistant", "content": reply})
    return state


# 🕸 Build the graph
def build_graph():
    graph = StateGraph(GraphState)

    # Add all nodes
    graph.add_node("router", router_node)
    graph.add_node("fitness", fitness_node)
    graph.add_node("nutrition", nutrition_node)
    graph.add_node("doctor", doctor_node)
    graph.add_node("tracking", tracking_node)
    graph.add_node("general", general_node)
    graph.add_node("api_tool", api_tool_node)
    graph.add_node("nutrition_with_data", nutrition_with_data_node)

    # Router dynamic routing
    def route(state: GraphState):
        for msg in reversed(state.messages):
            if msg.get("role") == "next_node":
                return msg["content"]
        return "tracking"

    # Router edges
    graph.add_conditional_edges(
        "router",
        route,
        {
            "fitness": "fitness",
            "nutrition": "nutrition",
            "health": "doctor",
            "tracking": "tracking",
            "misc": "general",
        },
    )

    # 🔄 LOOP: Nutrition can go to API tool or end
    graph.add_conditional_edges(
        "nutrition",
        get_next_node,
        {
            "api_tool": "api_tool",
            "__end__": "__end__"
        }
    )

    # 🔄 LOOP: API tool goes back to nutrition with data
    graph.add_edge("api_tool", "nutrition_with_data")

    # Terminal edges
    for node in ["fitness", "doctor", "tracking", "general", "nutrition_with_data"]:
        graph.add_edge(node, END)

    graph.set_entry_point("router")

    return graph.compile()
