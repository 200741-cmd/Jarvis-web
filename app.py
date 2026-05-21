import streamlit as st
from groq import Groq
import os

# 1. Page Configuration
st.set_page_config(page_title="JARVIS // HUD", page_icon="🤖", layout="centered")

# 2. Futuristic Stark-Tech UI Styling (Custom CSS)
st.markdown("""
    <style>
    /* Dark Sci-Fi Background */
    .stApp {
        background: radial-gradient(circle, #0d1117 0%, #07090e 100%);
        color: #00f0ff;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Glowing Titles & Headers */
    h1 {
        color: #00f0ff !important;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.6), 0 0 20px rgba(0, 240, 255, 0.4);
        font-weight: bold;
        letter-spacing: 2px;
        text-align: center;
    }
    
    .stCaption {
        color: #8a99ad !important;
        text-align: center;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 3px;
    }

    /* Holographic Custom Chat Containers */
    div[data-testid="stChatMessage"] {
        background: rgba(6, 18, 36, 0.6) !important;
        border: 1px solid #00f0ff !important;
        box-shadow: 0 0 8px rgba(0, 240, 255, 0.2);
        border-radius: 10px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
    }

    /* System Status Bar Styling */
    .status-bar {
        border-left: 3px solid #ff0055;
        background: rgba(255, 0, 85, 0.05);
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allowed_html=True)

# 3. Secure API Key Initialization
api_key = None
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
elif os.path.exists("key.txt"):
    with open("key.txt", "r") as f:
        api_key = f.read().strip()

# Main Header Interface
st.title("🤖 JARVIS : AI USER INTERFACE")
st.caption("SYSTEM STATUS: ONLINE // SECURE NODE LINKED")

if api_key:
    client = Groq(api_key=api_key)
else:
    st.markdown('<div class="status-bar">❌ <b>CRITICAL ERROR:</b> ACCESS DENIED. GROQ_API_KEY CORE IS MISSING. PLUG KEY INTO STREAMLIT SECRETS OVERRIDE.</div>', unsafe_allowed_html=True)
    st.stop()

# 4. Memory / Chat History Setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are JARVIS, a highly advanced, intelligent, slightly sarcastic, and deeply loyal AI framework designed by Tony Stark. Speak like JARVIS, addressing the user as sir."}
    ]

# Display Holographic Conversation History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(f"**{message['role'].upper()}:** {message['content']}")

# 5. Command Input Terminal
if user_prompt := st.chat_input("ENTER COMMAND OR INSTRUCTION..."):
    with st.chat_message("user"):
        st.markdown(f"**USER:** {user_prompt}")
    
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Jarvis Processing Output
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                stream=True,
            )
            for chunk in completion:
                chunk_text = chunk.choices[0].delta.content or ""
                full_response += chunk_text
                response_placeholder.markdown(f"**JARVIS:** {full_response}▌")
                
            response_placeholder.markdown(f"**JARVIS:** {full_response}")
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"// TERMINAL CORE INTERRUPT: {e}")
