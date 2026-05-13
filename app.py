import streamlit as st
from groq import Groq

# J.A.R.V.I.S. Interface Settings
st.set_page_config(page_title="J.A.R.V.I.S. Terminal", page_icon="🛡️")
st.title("🛡️ J.A.R.V.I.S. Online")

# Securely pull your Groq API Key
client = Groq(api_key=st.secrets["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"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What are your orders, Sir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # J.A.R.V.I.S. Logic
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are J.A.R.V.I.S., witty, British, and call the user Sir."},
                *st.session_state.messages
            ]
        )
        msg = response.choices[0].message.content
        st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
