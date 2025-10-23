from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from agents.router import RouterAgent
from agents.fitness_coach import FitnessCoachAgent
from agents.nutrition_specialist import NutritionAgent
from agents.doctor_avatar import DoctorAgent
from agents.tracking_viz import TrackingAgent
from agents.general_agent import GeneralAgent


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
    # Get the original user message, not the routing decision
    user_msg = None
    for msg in state.messages:
        if msg.get("role") == "user":
            user_msg = msg["content"]
    
    reply = nutrition.respond(user, user_msg)
    state.messages.append({"role": "assistant", "content": reply})
    
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

    graph.add_node("router", router_node)
    graph.add_node("fitness", fitness_node)
    graph.add_node("nutrition", nutrition_node)
    graph.add_node("doctor", doctor_node)
    graph.add_node("tracking", tracking_node)
    graph.add_node("general", general_node)

    # dynamic routing
    def route(state: GraphState):
        for msg in reversed(state.messages):
            if msg.get("role") == "next_node":
                return msg["content"]
        return "tracking"

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

    # terminal edges
    for node in ["fitness", "nutrition", "doctor", "tracking", "general"]:
        graph.add_edge(node, END)

    graph.set_entry_point("router")

    return graph.compile()
