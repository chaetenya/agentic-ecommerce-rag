import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from tools import ecommerce_tools

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
agent_executor = create_agent(llm, ecommerce_tools)

def ask_ecommerce_agent(query: str) -> str:
    """Takes a user query, runs the agent, and returns a clean text string."""
    inputs = {"messages": [("user", query)]}
    
    # Run the agent and get the final state
    final_state = agent_executor.invoke(inputs)
    final_message = final_state["messages"][-1].content
    
    if isinstance(final_message, list):
        return final_message[0].get("text", "I could not generate a text response.")
    
    return final_message
