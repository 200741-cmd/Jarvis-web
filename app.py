import streamlit as st
from groq import Groq
import random
import time
import os

# --- 1. CONFIGURATION & ENHANCED HOLOGRAPHIC UI ---
st.set_page_config(page_title="J.A.R.V.I.S. Mainframe", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #060913;
        background-image: 
            linear-gradient(rgba(0, 229, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.04) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #00E5FF;
        font-family: 'Courier New', Courier, monospace;
    }
    
    div[data-testid="column"] {
        background: rgba(6, 9, 19, 0.8) !important;
        border: 1px solid rgba(0, 229, 255, 0.4) !important;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 12px;
        backdrop-filter: blur(6px);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    div[data-testid="column"]:hover {
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.2);
    }
    
    div[data-testid="stColumn"]:nth-child(2) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px;
    }
    
    h1, h2, h3, h4 {
        color: #00E5FF !important;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.8);
        letter-spacing: 3px;
        margin-top: 0px;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2.8em !important;
        animation: glowPulse 2s ease-in-out infinite;
    }
    
    @keyframes glowPulse {
        0%, 100% { text-shadow: 0 0 10px rgba(0, 229, 255, 0.8); }
        50% { text-shadow: 0 0 20px rgba(0, 229, 255, 1); }
    }
    
    .stChatMessage {
        background-color: rgba(6, 9, 19, 0.9) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        backdrop-filter: blur(6px);
        color: #00E5FF !important;
    }
    
    hr {
        border: 0;
        height: 2px;
        background-image: linear-gradient(to right, rgba(0,229,255,0), rgba(0,229,255,0.8), rgba(0,229,255,0));
        margin: 20px 0;
    }
    
    .stButton > button {
        background: rgba(0, 229, 255, 0.15) !important;
        border: 1px solid rgba(0, 229, 255, 0.5) !important;
        color: #00E5FF !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .status-ok { color: #00FF88; text-shadow: 0 0 8px rgba(0, 255, 136, 0.6); }
    .status-warning { color: #FFAA00; text-shadow: 0 0 8px rgba(255, 170, 0, 0.6); }
    .status-critical { color: #FF4444; text-shadow: 0 0 8px rgba(255, 68, 68, 0.6); }
    </style>
""", unsafe_allow_html=True)

# --- 2. API KEY CHECKER ---
SECRET_KEY = None
if "GROQ_API_KEY" in st.secrets:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
elif "groq_api_key" in st.secrets:
    SECRET_KEY = st.secrets["groq_api_key"]
elif os.environ.get("GROQ_API_KEY"):
    SECRET_KEY = os.environ.get("GROQ_API_KEY")

# --- 3. STATE INITIALIZATION ---
if 'armor_durability' not in st.session_state:
    st.session_state.armor_durability = 100
if 'reactor_temp' not in st.session_state:
    st.session_state.reactor_temp = 42
if 'system_logs' not in st.session_state:
    st.session_state.system_logs = ["Mainframe online.", "Holographic grid projected."]
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Good day, sir. J.A.R.V.I.S. systems fully operational. Ready for your command, sir."}]

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, f"[{timestamp}] {message}")

st.session_state.reactor_temp = random.randint(39, 45)

# --- 4. STATUS COLORS ---
def get_armor_status(durability):
    if durability >= 80: return "status-ok", "OPTIMAL"
    elif durability >= 50: return "status-warning", "DEGRADED"
    else: return "status-critical", "CRITICAL"

def get_reactor_status(temp):
    if temp <= 45: return "status-ok", "STABLE"
    elif temp <= 55: return "status-warning", "RISING"
    else: return "status-critical", "OVERHEAT"

armor_status, armor_level = get_armor_status(st.session_state.armor_durability)
reactor_status, reactor_level = get_reactor_status(st.session_state.reactor_temp)

# --- 5. MAIN UI ---
st.title("⚙️ J.A.R.V.I.S. // DIAGNOSTICS MAINFRAME")
st.markdown("<hr>", unsafe_allow_html=True)

master_left, master_right = st.columns([5, 7])

with master_left:
    st.write("### 🎛️ CORE TELEMETRY")
    
    box_col1, box_col2 = st.columns(2)
    with box_col1:
        st.markdown("#### 🛡️ SUIT INTEGRITY")
        st.write(f"Armor: **<span class='{armor_status}'>{st.session_state.armor_durability}%</span>** ({armor_level})")
        st.progress(st.session_state.armor_durability / 100)
        if st.session_state.armor_durability < 50:
            st.markdown("<span class='status-warning'>⚠️ Integrity compromised, sir</span>", unsafe_allow_html=True)
        
    with box_col2:
        st.markdown("#### 🌡️ ARC REACTOR")
        st.write(f"Temp: **<span class='{reactor_status}'>{st.session_state.reactor_temp}°C</span>** ({reactor_level})")
        st.progress(min(1.0, st.session_state.reactor_temp / 100))
        if st.session_state.reactor_temp > 50:
            st.markdown("<span class='status-warning'>⚠️ Temperature rising, sir</span>", unsafe_allow_html=True)
            
    box_col3, box_col4 = st.columns(2)
    with box_col3:
        st.markdown("#### 🔧 UTILITIES")
        if st.button("♻️ Optimize Cache", use_container_width=True):
            log_event("CLEAN: Memory buffers flushed.")
            st.rerun()
        if st.button("🛠️ Run Calibration", use_container_width=True):
            st.session_state.armor_durability = 100
            log_event("REPAIR: Structural reset.")
            st.rerun()
        if st.button("🔄 Refresh Metrics", use_container_width=True):
            st.session_state.reactor_temp = random.randint(39, 45)
            log_event("UPDATE: Telemetry refreshed.")
            st.rerun()
            
    with box_col4:
        st.markdown("#### 💾 LOG STREAM")
        log_box = "".join([f"{log}
" for log in st.session_state.system_logs[:4]])
        st.code(log_box, language="bash")

with master_right:
    st.write("### 📡 SECURE COMM-LINK")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_prompt := st.chat_input("Enter command..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)
            
        if not SECRET_KEY:
            with st.chat_message("assistant"):
                st.error("🚨 No API key found.")
            st.session_state.messages.append({"role": "assistant", "content": "Link dropped, sir. Missing key."})
            log_event("REJECT: Key missing.")
            st.rerun()
        
        system_prompt = (
            "You are J.A.R.V.I.S., Tony Stark's AI assistant. Address user as 'sir'.
"
            "Speak formally with British precision, dry wit, and calm logic.
"
            "Avoid contractions. Be proactive & protective.

"
            f"METRICS: Suit={st.session_state.armor_durability}%, Reactor={st.session_state.reactor_temp}°C

"
            "If armor<50%, warn & suggest calibration. If reactor>50°C, warn of overheating.
"
            "End with 'Further assistance, sir?' Always stay in character."
        )
        
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages[-10:]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
            
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            try:
                client = Groq(api_key=SECRET_KEY)
                chat_completion = client.chat.completions.create(
                    messages=api_messages,
                    model="llama-3.3-70b-versatile", 
                    temperature=0.7
                )
                ai_reply = chat_completion.choices[0].message.content
                response_placeholder.write(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                log_event("COMM: Processed.")
            except Exception as api_err:
                response_placeholder.write(f"🚨 Error: {str(api_err)}")
                log_event("ERROR: Stream broken.")
                
        st.rerun()
