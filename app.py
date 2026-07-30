import requests
import streamlit as st

st.set_page_config(
    page_title="We Strive Civic Assistant", page_icon="🤖"
)

st.title("We Strive Civic Assistant 🏙️")
st.markdown("Your AI-powered community guide and civic helper.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about your community..."):
    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Replace the URL below with your active LocalTunnel URL
                tunnel_url = "https://upset-frogs-rule.loca.lt/webhook"

                payload = {"message": prompt}
                response = requests.post(tunnel_url, json=payload, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    bot_reply = (
                        data.get("reply")
                        or data.get("response")
                        or str(data)
                    )
                else:
                    bot_reply = f"Error: Received status code {response.status_code}"

            except Exception as e:
                bot_reply = f"Connection error: Could not reach backend engine. ({e})"

            st.markdown(bot_reply)
            st.session_state.messages.append(
                {"role": "assistant", "content": bot_reply}
            )