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

def build_system_instruction():
    instruction_parts = []
    
    # 1. Load core persona files first as primary system rules
    core_persona_files = ["SOUL.md", "IDENTITY.md", "AGENTS.md"]
    data_files = ["upcoming_projects.md", "facility_booking.md", "issue_reporting.md", "community_events.md"]
    
    loaded = set()
    
    instruction_parts.append("=== SYSTEM PERSONA & RULES ===")
    for filename in core_persona_files:
        filepath = os.path.join(WORKSPACE_DIR, filename)
        if os.path.exists(filepath):
            loaded.add(filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    instruction_parts.append(f.read())
            except Exception:
                pass
                
    instruction_parts.append("\n=== OFFICIAL TOWN DATA FILES ===")
    for filename in data_files:
        filepath = os.path.join(WORKSPACE_DIR, filename)
        if os.path.exists(filepath):
            loaded.add(filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    instruction_parts.append(f"--- {filename} ---\n{f.read()}")
            except Exception:
                pass
                
    # Load any remaining markdown files just in case
    if os.path.exists(WORKSPACE_DIR):
        for filename in sorted(os.listdir(WORKSPACE_DIR)):
            if filename.endswith(".md") and filename not in loaded:
                filepath = os.path.join(WORKSPACE_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        instruction_parts.append(f"--- {filename} ---\n{f.read()}")
                except Exception:
                    pass
                    
    return "\n\n".join(instruction_parts)

system_instruction = build_system_instruction()

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
