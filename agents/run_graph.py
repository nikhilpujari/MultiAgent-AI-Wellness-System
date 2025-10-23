from agents.graph import build_graph

# Build and compile the graph once
workflow = build_graph()

def run_agent(user: str, msg: str) -> str:
    """
    Executes the LangGraph workflow for a given user and message.
    Returns the final agent response as plain text.
    """
    import streamlit as st
    st.write(f"🚀 WORKFLOW: Starting for user '{user}'")
    
    inputs = {"messages": [{"role": "user", "content": msg}], "user": user}
    result = workflow.invoke(inputs)
    
    final_response = result["messages"][-1]["content"]
    st.write("✅ WORKFLOW: Completed")
    
    return final_response
