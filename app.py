import streamlit as st
from groq import Groq

# 1. Page Configuration & Styling
st.set_page_config(page_title="Jarvis AI", page_icon="🤖", layout="centered")
st.title("🤖 Jarvis AI")
st.caption("Advanced Assistant powered by Groq")

# 2. Secure API Key Initialization
# This automatically looks for a secret variable named "GROQ_API_KEY"

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("❌ GROQ_API_KEY missing! Please add it to your Streamlit Secrets.")
    st.stop()

# 3. Initialize Conversation History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Jarvis, a highly intelligent, witty, and helpful AI assistant."}
    ]

# 4. Display Existing Chat Messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Handle User Input
if user_prompt := st.chat_input("How can I help you, sir?"):
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    # Append to history
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # 6. Generate AI Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Call Groq API using the reliable llama3-8b-8192 model
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=st.session_state.messages,
                stream=True,
            )
            
            # Stream the response chunk by chunk for a smooth typing effect
            for chunk in completion:
                chunk_text = chunk.choices[0].delta.content or ""
                full_response += chunk_text
                response_placeholder.markdown(full_response + "▌")
                
            response_placeholder.markdown(full_response)
            
            # Append assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
