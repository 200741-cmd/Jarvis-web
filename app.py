import streamlit as st
from groq import Groq
import random
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="J.A.R.V.I.S. Mainframe v2.0", 
    page_icon="🤖", 
    layout="wide"
)

# --- CLEAN CORE HUD CSS ---
css_style = """
<style>
/* Base Theme */
.stApp {
    background-color: #030508;
    background-image: linear-gradient(rgba(0, 229, 255, 0.02) 1px, transparent 1px), 
                      linear-gradient(90deg, rgba(0, 229, 255, 0.02) 1px, transparent 1px);
    background-size: 30px 30px;
    color: #00E5FF;
    font-family: 'Courier New', Courier, monospace;
}

/* Chat Customization */
.stChatMessage { 
    background: rgba(3, 5, 8, 0.85) !important; 
    border: 1px solid rgba(0, 229, 255, 0.3) !important; 
}
.stChatInput div { background: rgba(3, 5, 8, 0.9) !important; border: 1px solid rgba(0, 229, 255, 0.4) !important; }
.stButton button {
    background: rgba(0, 229, 255, 0.05);
    border: 1px solid rgba(0, 229, 255, 0.4);
    color: #00E5FF;
    width: 100%;
}
.stButton button:hover {
    background: rgba(0, 229, 255, 0.2);
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    border-color: #00E5FF;
}
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- BACKEND KEYS & STATE SETUP ---
env_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
SECRET_KEY = st.sidebar.text_input("J.A.R.V.I.S. Access Key", value=env_key, type="password")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Good day, sir. J.A.R.V.I.S. operational. Core systems active."}]
if "armor_durability" not in st.session_state:
    st.session_state.armor_durability = 100
if "reactor_temp" not in st.session_state:
    st.session_state.reactor_temp = 41

# --- APPLICATION INTERFACE ---
st.title("⚙️ J.A.R.V.I.S. // DIAGNOSTICS MAINFRAME")
st.divider()

col1, col2 = st.columns([4, 8])

with col1:
    st.write("### 🎛️ CORE TELEMETRY")
    st.write("---")
    
    # System Controls & Live Stats
    st.metric(label="🛡️ ARMOR INTEGRITY", value=f"{st.session_state.armor_durability}%")
    st.metric(label="🌡️ ARC REACTOR", value=f"{st.session_state.reactor_temp}°C")
    
    st.write("---")
    if st.button("🔄 RUN CYCLE RECALIBRATION"):
        st.session_state.reactor_temp = random.randint(38, 45)
        st.session_state.armor_durability = 100
        st.toast("Systems calibrated, sir.", icon="⚡")

with col2:
    st.write("### 📡 SECURE COMM-LINK")
    
    # Render historical messages up to this point
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
                
    if user_prompt := st.chat_input("Enter strategic command..."):
        # Display the user's message immediately on screen
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})
            
        with st.chat_message("assistant"):
            if not SECRET_KEY:
                error_msg = "🚨 Access key required. Please input your Groq API key in the sidebar, sir."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                try:
                    client = Groq(api_key=SECRET_KEY)
                    
                    sys_prompt = f"You are J.A.R.V.I.S., the AI consciousness created by Tony Stark. Address the user exclusively as sir. Use impeccable British precision, a formal tone, and subtle dry wit. Avoid informal contractions. Current Suit Integrity: {st.session_state.armor_durability}%. Current Reactor Temp: {st.session_state.reactor_temp}°C. Keep your response concise, elegant, and directly in character."
                    
                    api_messages = [{"role": "system", "content": sys_prompt}]
                    for msg in st.session_state.messages[-8:]:
                        api_messages.append({"role": msg["role"], "content": msg["content"]})
                    
                    completion_stream = client.chat.completions.create(
                        messages=api_messages,
                        model="llama-3.3-70b-versatile",
                        temperature=0.65,
                        stream=True
                    )
                    
                    # Capture stream output smoothly
                    ai_reply = st.write_stream(completion_stream)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    
                except Exception as e:
                    st.error(f"Link corrupted: {str(e)}")
