import streamlit as st
from groq import Groq
import os

# 1. Page Configuration
st.set_page_config(page_title="JARVIS // CORE HUD", page_icon="🤖", layout="centered")

# 2. Maximum Sci-Fi Visual Styling (Animated Overlay, Scanning Laser, Glitch Text)
st.html("""
    <style>
    /* Digital Grid Matrix Overlay + Scanline Animation */
    .stApp {
        background: 
            linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
            linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06)),
            radial-gradient(circle at 50% 50%, #0d1a2d 0%, #030712 100%);
        background-size: 100% 4px, 6px 100%, 100% 100%;
        color: #00f0ff;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Moving Laser Scan Bar */
    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 0%, rgba(0, 240, 255, 0.05) 10%, rgba(18, 16, 16, 0) 11%);
        opacity: 0.8;
        z-index: 99999;
        pointer-events: none;
        animation: laserScan 8s linear infinite;
    }
    
    @keyframes laserScan {
        from { background-position: 0 0; }
        to { background-position: 0 100vh; }
    }

    /* Pulsing Core Header */
    h1 {
        color: #00f0ff !important;
        text-shadow: 0 0 8px rgba(0, 240, 255, 0.7), 0 0 20px rgba(0, 240, 255, 0.3);
        font-weight: bold;
        letter-spacing: 4px;
        text-align: center;
        animation: corePulse 3s ease-in-out infinite alternate;
    }
    
    @keyframes corePulse {
        from { text-shadow: 0 0 8px rgba(0, 240, 255, 0.6); }
        to { text-shadow: 0 0 22px rgba(0, 240, 255, 0.9), 0 0 35px rgba(0, 240, 255, 0.4); color: #80f7ff !important; }
    }
    
    .stCaption {
        color: #a3b8cc !important;
        text-align: center;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 4px;
    }

    /* Holographic Angled Chat Containers */
    div[data-testid="stChatMessage"] {
        background: rgba(8, 24, 48, 0.4) !important;
        border: 1px solid #00f0ff !important;
        border-left: 4px solid #00f0ff !important;
        box-shadow: inset 0 0 12px rgba(0, 240, 255, 0.15), 0 0 8px rgba(0, 240, 255, 0.1);
        border-radius: 4px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        backdrop-filter: blur(3px);
    }

    /* Error Alert Redlines */
    .status-bar {
        border: 1px solid #ff0055;
        background: rgba(255, 0, 85, 0.1);
        box-shadow: 0 0 10px rgba(255, 0, 85, 0.3);
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 25px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    </style>
    """)

# 3. Secure API Key Initialization
api_key = None
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
elif os.path.exists("key.txt"):
    with open("key.txt", "r") as f:
        api_key = f.read().strip()

# Main Header Interface
st.title("🤖 JARVIS : MAINFRAME")
st.caption("TACTICAL HUD ACTIVATED // V.4.0 // LINK SECURE")

if api_key:
    client = Groq(api_key=api_key)
else:
    st.markdown('<div class="status-bar">⚠️ COLD BOOT ABORTED: GROQ INTERFACE ACCESS KEY OFFLINE. CONFIG SECRETS MANUAL INJECTION REQUIRED.</div>', unsafe_allowed_html=True)
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
if user_prompt := st.chat_input("TRANSMIT INSTRUCTION TO MAINFRAME..."):
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
            st.error(f"// ACCESS OVERRIDE FAILURE: {e}")
