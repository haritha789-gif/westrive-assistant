import os
import openai
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv(os.path.expanduser("~/.zeroclaw/workspace/.env"))
load_dotenv(".env")

st.set_page_config(page_title="We Strive Civic Assistant", page_icon="🤖")

st.title("We Strive Civic Assistant 🏙️")
st.markdown("Your AI-powered community guide and civic helper.")

# Dynamically locate the workspace directory across local and cloud deployment environments
def find_workspace_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.abspath(os.path.join(current_dir, "..")),  # Repository root (parent folder)
        current_dir,                                       # Same directory as app.py
        os.path.expanduser("~/.zeroclaw/workspace"),      # Local ZeroClaw workspace path
        os.getcwd()                                       # Current working directory
    ]
    
    for candidate in candidates:
        if os.path.exists(candidate):
            # Check if core markdown files exist here
            if any(os.path.exists(os.path.join(candidate, fname)) for fname in ["AGENTS.md", "upcoming_projects.md", "IDENTITY.md"]):
                return candidate
                
    return current_dir

WORKSPACE_DIR = find_workspace_dir()

def build_workspace_context():
    knowledge_parts = []
    target_files = ["SOUL.md", "IDENTITY.md", "AGENTS.md", "upcoming_projects.md", "facility_booking.md", "issue_reporting.md", "council_meetings.md"]
    loaded = set()
    
    if not os.path.exists(WORKSPACE_DIR):
        return f"CRITICAL ERROR: Workspace directory not found at {WORKSPACE_DIR}"
        
    for filename in target_files:
        filepath = os.path.join(WORKSPACE_DIR, filename)
        if os.path.exists(filepath):
            loaded.add(filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    knowledge_parts.append(f"=== {filename} ===\n{f.read()}")
            except Exception as e:
                knowledge_parts.append(f"=== {filename} ===\nERROR READING FILE: {str(e)}")
        else:
            knowledge_parts.append(f"=== {filename} ===\nFILE NOT FOUND AT PATH: {filepath}")
                
    return "\n\n".join(knowledge_parts)

workspace_knowledge = build_workspace_context()

# Sidebar diagnostics
with st.sidebar:
    st.header("🔍 System Diagnostics")
    st.write(f"**Detected Workspace:** `{WORKSPACE_DIR}`")
    with st.expander("View Loaded Workspace Knowledge"):
        st.text(workspace_knowledge)

# Grab OpenRouter API key
api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
model_name = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your community..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing workspace data..."):
            try:
                if not api_key:
                    raise ValueError("API key not found.")
                
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                
                system_prompt = (
                    "Your entire identity, persona, rules, and knowledge base are defined by the workspace files provided below. "
                    "Read, comprehend, and self-direct your responses strictly based on these files.\n\n"
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
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
