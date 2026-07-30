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
            # Simulated intelligent civic response for public testing demo
            # (You can replace this logic later with a requests.post to your live backend URL)
            prompt_lower = prompt.lower()
            if "pool" in prompt_lower or "water" in prompt_lower:
                bot_reply = "During regional drought conditions in our area, temporary pool water restrictions may apply. Please check local town guidelines regarding outdoor water conservation limits before filling."
            elif "scout" in prompt_lower or "badge" in prompt_lower:
                bot_reply = "For technology merit badges in a short classroom setting, introductory digital safety, basic coding concepts, or civic tech project outlines work best!"
            else:
                bot_reply = f"Thanks for reaching out to 'We Strive'! I've logged your question: '{prompt}'. Our team will use this to improve our community assistance tools."

            st.markdown(bot_reply)
            st.session_state.messages.append(
                {"role": "assistant", "content": bot_reply}
            )
