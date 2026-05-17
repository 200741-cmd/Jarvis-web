import streamlit as st
from groq import Groq
import os

# 1. Start the App interface
st.set_page_config(page_title="Jarvis AI", page_icon="🤖", layout="centered")
st.title("🤖 Jarvis AI")
st.caption("Welcome back, sir.")

# 2. Look for your API Key safely
api_key = None

# It will look here when running on the Streamlit web server:
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
# If running on your tablet locally, it looks at key.txt:
elif os.path.exists("key.txt"):
    with open("key.txt", "r") as f:
        api_key = f.read().strip()

# 3. Connect to Groq if the key exists
if api_key:
    client = Groq(api_key=api_key)
else:
    st.error("❌ I can't find your API key. Please make sure it is added to your Streamlit secrets.")
    st.stop()

# 4. Memory / Chat History setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Jarvis, a highly intelligent, witty, and helpful AI assistant."}
    ]

# Display the conversation
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Type to Jarvis
if user_prompt := st.chat_input("How can I help you, sir?"):
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Jarvis responds
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=st.session_state.messages,
                stream=True,
            )
            for chunk in completion:
                chunk_text = chunk.choices[0].delta.content or ""
                full_response += chunk_text
                response_placeholder.markdown(full_response + "▌")
                
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Something went wrong: {e}")
