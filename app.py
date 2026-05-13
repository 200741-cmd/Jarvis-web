import streamlit as st
from groq import Groq

# J.A.R.V.I.S. Interface Settings
st.set_page_config(page_title="J.A.R.V.I.S. Terminal", page_icon="🛡️")
st.title("🛡️ J.A.R.V.I.S. Online")

# --- THE KEY IS NOW EMBEDDED DIRECTLY ---
# Note: In a professional app, we'd use secrets, but this ensures it works for you right now!
client = Groq(api_key="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")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input area
if prompt := st.chat_input("What are your orders, Sir?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # J.A.R.V.I.S. Response Logic
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are J.A.R.V.I.S., a witty, British AI assistant. Call the user Sir. You are an expert in geometry, Prisma3D, and iron man suit projects."
                    },
                    *st.session_state.messages
                ]
            )
            msg = response.choices[0].message.content
            st.markdown(msg)
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": msg})
        except Exception as e:
            st.error(f"Sir, I've encountered an error: {e}")
