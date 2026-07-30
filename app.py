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
ALT_WORKSPACE_DIR = os.path.expanduser("~/.zeroclaw/workspace/westrive-deploy")

# Helper function to read all markdown files with data prioritization
def load_all_workspace_knowledge():
    knowledge_parts = []
    paths_to_check = [WORKSPACE_DIR, ALT_WORKSPACE_DIR]
    
    # Target specific data files first so they are processed properly
    priority_files = ["AGENTS.md", "upcoming_projects.md", "facility_booking.md", "issue_reporting.md"]
    loaded_files = set()
    
    for base_path in paths_to_check:
        if os.path.exists(base_path):
            # Load priority files first
            for filename in priority_files:
                filepath = os.path.join(base_path, filename)
                if os.path.exists(filepath) and filename not in loaded_files:
                    loaded_files.add(filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                            knowledge_parts.append(f"=== FILE: {filename} ===\n{content}")
                    except Exception:
                        pass
            
            # Load any remaining markdown files
            for filename in sorted(os.listdir(base_path)):
                if filename.endswith(".md") and filename not in loaded_files:
                    loaded_files.add(filename)
                    filepath = os.path.join(base_path, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                            knowledge_parts.append(f"=== FILE: {filename} ===\n{content}")
                    except Exception:
                        pass
                        
    return "\n\n".join(knowledge_parts)

# Gather all markdown system prompts and data files dynamically
workspace_knowledge = load_all_workspace_knowledge()

# Keep system instruction clean and let AGENTS.md guide the orchestrator behavior
system_instruction = f"""You are the We Strive Civic Assistant orchestrator. Follow all operational guidelines, domain routing, and formatting rules specified in AGENTS.md using ONLY the official town data files provided below.

OFFICIAL TOWN KNOWLEDGE & FILES:
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
                
                # Construct full message payload including system prompt and full history
                messages_payload = [{"role": "system", "content": system_instruction}]
                for msg in st.session_state.messages:
                    messages_payload.append({"role": msg["role"], "content": msg["content"]})

                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages_payload,
                    temperature=0.1, # Slight flexibility for keyword/semantic matching without hallucinations
                )
                
                bot_reply = response.choices[0].message.content
            except Exception as e:
                bot_reply = f"Error generating response: {e}"

            st.markdown(bot_reply)
            st.session_state.messages.append(
                {"role": "assistant", "content": bot_reply}
            )
