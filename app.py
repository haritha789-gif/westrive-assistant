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

def load_all_workspace_knowledge():
    knowledge_parts = []
    # Explicit list of your core workspace files to guarantee they are loaded
    target_files = [
        "SOUL.md", 
        "IDENTITY.md", 
        "AGENTS.md", 
        "upcoming_projects.md", 
        "facility_booking.md", 
        "issue_reporting.md"
    ]
    
    if os.path.exists(WORKSPACE_DIR):
        for filename in target_files:
            filepath = os.path.join(WORKSPACE_DIR, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        knowledge_parts.append(f"=== FILE: {filename} ===\n{content}")
                except Exception as e:
                    knowledge_parts.append(f"=== FILE: {filename} (Error reading: {e}) ===")
            else:
                knowledge_parts.append(f"=== FILE: {filename} (Not Found) ===")
                
        # Also grab any other markdown files just in case
        for filename in sorted(os.listdir(WORKSPACE_DIR)):
            if filename.endswith(".md") and filename not in target_files:
                filepath = os.path.join(WORKSPACE_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        knowledge_parts.append(f"=== FILE: {filename} ===\n{content}")
                except Exception:
                    pass
                    
    return "\n\n".join(knowledge_parts)

workspace_knowledge = load_all_workspace_knowledge()

# Strict system instruction embedding your actual workspace files
system_instruction = f"""system_instruction = f"""You are an AI assistant whose exact persona, rules, and knowledge base are defined entirely by the workspace files provided below. Read, comprehend, and strictly follow the instructions, identity, and data found within these files for all responses.

OFFICIAL WORKSPACE FILES & KNOWLEDGE:
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
                    raise ValueError("API key not found. Please verify your environment or secrets contain your OpenRouter key.")
                
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                
                messages_payload = [{"role": "system", "content": system_instruction}]
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
