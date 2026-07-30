import os
import openai
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env
load_dotenv(os.path.expanduser("~/.zeroclaw/workspace/.env"))
load_dotenv(".env")

st.set_page_config(
    page_title="We Strive Civic Assistant", page_icon="🤖"
)

st.title("We Strive Civic Assistant 🏙️")
st.markdown("Your AI-powered community guide and civic helper.")

# Load workspace paths
WORKSPACE_DIR = os.path.expanduser("~/.zeroclaw/workspace")

# Helper function to read all markdown files in the workspace directory
def load_all_workspace_knowledge():
    knowledge_parts = []
    if os.path.exists(WORKSPACE_DIR):
        for filename in sorted(os.listdir(WORKSPACE_DIR)):
            if filename.endswith(".md"):
                filepath = os.path.join(WORKSPACE_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        knowledge_parts.append(f"--- FILE: {filename} ---\n{content}")
                except Exception:
                    pass
    return "\n\n".join(knowledge_parts)

# Gather all markdown system prompts and data files dynamically
workspace_knowledge = load_all_workspace_knowledge()
system_instruction = f"""You are the We Strive Civic Assistant orchestrator. 
You have strict local-only access using ONLY the official town data and agent markdown files provided below. 
Do not hallucinate or access external web searches.

OFFICIAL TOWN DATA & WORKSPACE FILES:
{workspace_knowledge}
"""

# Grab OpenRouter API key from environment
api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
model_name = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input using standard Streamlit chat input loop
if prompt := st.chat_input("Ask a question about your community..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("We Strive agents analyzing workspace data..."):
            try:
                if not api_key:
                    raise ValueError("API key not found. Please verify your .env file contains your OpenRouter key.")
                
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                
                # Construct full message payload including system prompt and full history
                messages_payload = [{"role": "system", "content": system_instruction}]
                for msg in st.session_state.messages:
                    messages_payload.append({"role": msg["role"], "content": msg["content"]})

                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages_payload,
                    temperature=0.3, # Low temperature for strict factual grounding
                )
                
                bot_reply = response.choices[0].message.content
            except Exception as e:
                bot_reply = f"Error generating response: {e}"

            st.markdown(bot_reply)
            st.session_state.messages.append(
                {"role": "assistant", "content": bot_reply}
            )
