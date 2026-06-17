import streamlit as st
from groq import Groq
import random
import time
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="J.A.R.V.I.S. Mainframe v2.0", 
    page_icon="🤖", 
    layout="wide"
)

# --- COMPLETE HIGH-FIDELITY HUD CSS ---
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

/* 3D Wireframe Hologram */
.field { 
    perspective: 1000px; 
    width: 100%; 
    height: 380px; 
    margin: 20px auto; 
    position: relative;
}
.suit { 
    position: relative; 
    width: 200px; 
    height: 320px; 
    margin: 0 auto;
    transform-style: preserve-3d; 
    animation: spin 15s infinite linear; 
}
@keyframes spin { 
    from { transform: rotateY(0deg); } 
    to { transform: rotateY(360deg); } 
}

/* Hologram Vectors */
.suit div { 
    position: absolute; 
    border: 1px solid rgba(0, 229, 255, 0.6); 
    background: rgba(0, 229, 255, 0.03); 
    box-shadow: inset 0 0 12px rgba(0, 229, 255, 0.2);
}
.head { 
    width: 44px; 
    height: 52px; 
    left: 78px; 
    top: 0px;
    border-radius: 22px 22px 10px 10px; 
}
.chest { 
    width: 90px; 
    height: 110px; 
    top: 58px; 
    left: 55px; 
    clip-path: polygon(15% 0%, 85% 0%, 100% 100%, 0% 100%); 
    transform: translateZ(15px);
}
.arc { 
    width: 24px; 
    height: 24px; 
    top: 90px; 
    left: 88px; 
    border-radius: 50%; 
    background: radial-gradient(circle, #ffffff 0%, #00E5FF 60%, transparent 100%); 
    box-shadow: 0 0 25px #00E5FF, 0 0 10px #00E5FF; 
    transform: translateZ(22px);
    border: 1px solid #ffffff !important;
}
.arm { width: 26px; height: 110px; top: 62px; }
.left { left: 22px; transform: rotate(10deg) translateZ(5px); }
.right { left: 152px; transform: rotate(-10deg) translateZ(5px); }
.legs { 
    width: 76px; 
    height: 120px; 
    top: 174px; 
    left: 62px; 
    clip-path: polygon(0% 0%, 100% 0%, 80% 100%, 20% 100%); 
}

/* HUD Scan Line Overlay */
.scan-line {
    position: absolute;
    width: 100%;
    height: 4px;
    background: rgba(0, 229, 255, 0.4);
    box-shadow: 0 0 12px #00E5FF;
    animation: scanMove 4s infinite linear;
    pointer-events: none;
    z-index: 10;
}
@keyframes scanMove { 0% { top: 0%; } 100% { top: 100%; } }

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
SECRET_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY"))

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Good day, sir. J.A.R.V.I.S. operational. Diagnostic wireframes loaded."}]
if "armor_durability" not in st.session_state:
    st.session_state.armor_durability = 100
if "reactor_temp" not in st.session_state:
    st.session_state.reactor_temp = 41

# --- APPLICATION INTERFACE ---
st.title("⚙️ J.A.R.V.I.S. // DIAGNOSTICS MAINFRAME")
st.divider()

col1, col2 = st.columns([5, 7])

with col1:
    st.write("### 🎛️ CORE TELEMETRY")
    
    # Hologram Window
    st.markdown("""
    <div class="field">
        <div class="scan-line"></div>
        <div class="suit">
            <div class
