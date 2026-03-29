import streamlit as st
import sys
import os

# Ensure Python can find our agent folder
sys.path.append(os.path.join(os.path.dirname(__file__), "retrieval_agent"))
from agent import ask_ecommerce_agent

# UI Configuration
st.set_page_config(page_title="E-Commerce AI Agent", layout="centered")
st.title("Agentic GraphRAG Assistant")
st.markdown("Ask questions about **products** (Graph DB) or **company policies** (Vector DB).")

# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input("For example: I want a Logitech mouse, what is the refund policy for it?"):
    
    # Show the user's message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call the LangGraph Agent with a loading spinner
    with st.chat_message("assistant"):
        with st.spinner("Agent is reasoning and querying databases..."):
            response_text = ask_ecommerce_agent(prompt)
            st.markdown(response_text)
            
    # Save the response to history
    st.session_state.messages.append({"role": "assistant", "content": response_text})