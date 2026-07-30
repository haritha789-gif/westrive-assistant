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

# Explicit absolute paths pointing directly to your workspace files
WORKSPACE_DIR = os.path.expanduser("~/.zeroclaw/workspace")

def build_workspace_context():
    knowledge_parts = []
    target_files = ["SOUL.md", "IDENTITY.md", "AGENTS.md", "upcoming_projects.md", "facility_booking.md", "issue_reporting.md", "community_events.md"]
    loaded = set()
    
    if os.path.exists(WORKSPACE_DIR):
        for filename in target_files:
            filepath = os.path.join(WORKSPACE_DIR, filename)
            if os.path.exists(filepath):
                loaded.add(filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        knowledge_parts.append(f"=== {filename} ===\n{f.read()}")
                except Exception:
                    pass
                    
        for filename in sorted(os.listdir(WORKSPACE_DIR)):
            if filename.endswith(".md") and filename not in loaded:
                filepath = os.path.join(WORKSPACE_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        knowledge_parts.append(f"=== {filename} ===\n{f.read()}")
                except Exception:
                    pass
                    
    return "\n\n".join(knowledge_parts)

workspace_knowledge = build_workspace_context()

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
                    raise ValueError("API key not found. Please verify your environment or secrets contain your OpenRouter key.")
                
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                
                # Force-inject the workspace context and identity into the system payload securely
                system_prompt = (
                    "You are the We Strive Civic Assistant, an official community guide for Fuquay-Varina. "
                    "You must NEVER state that you are a generic AI model. You derive your entire identity, purpose, "
                    "and knowledge strictly from the workspace files provided below:\n\n"
                    f"{workspace_knowledge}"
                )
                
                messages_payload = [{"role": "system", "content": system_prompt}]
                for msg in st.session_state.messages:
                    messages_payload.append({"role": msg["role"], "content": msg["content"]})

                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages_payload,
                    temperature=0.1,
                )
                
                bot_reply = response.choices[0].message.content
            except Exception as e:
                bot_reply = f"Error generating response: {e}"

            st.markdown(bot_reply)
            st.session_state.messages.append(
                {"role": "assistant", "content": bot_reply}
            )
