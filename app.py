import streamlit as st
from groq import Groq
import random
import time
import os

st.set_page_config(page_title="J.A.R.V.I.S. Mainframe", page_icon="🤖", layout="wide")

css_style = """
<style>
.stApp {
    background-color: #030508;
    background-image: linear-gradient(rgba(0, 229, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 229, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    color: #00E5FF;
    font-family: Courier New, Courier, monospace;
}
div[data-testid='column'] {
    background: rgba(3, 5, 8, 0.85);
    border: 1px solid rgba(0, 229, 255, 0.3);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.08);
}
div[data-testid='stColumn']:nth-child(2) {
    background: transparent;
    border: none;
    padding: 0px;
}
h1, h2, h3, h4 {
    color: #00E5FF;
    text-shadow: 0 0 10px rgba(0, 229, 255, 0.8);
    letter-spacing: 4px;
    font-weight: 700;
}
h1 { font-size: 3em; }
.stChatMessage {
    background-color: rgba(3, 5, 8, 0.95);
    border: 1px solid rgba(0, 229, 255, 0.25);
    color: #00E5FF;
}
.stChatInput div {
    background: rgba(3, 5, 8, 0.9);
    border: 1px solid rgba(0, 229, 255, 0.3);
}
.stButton button {
    background: rgba(0, 229, 255, 0.1);
    border: 1px solid rgba(0, 229, 255, 0.5);
    color: #00E5FF;
    font-family: Courier New, monospace;
    font-weight: 600;
}
.stButton button:hover {
    background: rgba(0, 229, 255, 0.25);
    box-shadow: 0 0 30px rgba(0, 229, 255, 0.4);
}
.stCode {
    background: rgba(3, 5, 8, 0.95);
    border: 1px solid rgba(0, 229, 255, 0.2);
}
hr {
    border: 0;
    height: 2px;
    background: linear-gradient(to right, rgba(0,229,255,0), rgba(0,229,255,0.8), rgba(0,229,255,0));
    margin: 25px 0;
}
.status-ok { color: #00FF88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.6); }
.status-warning { color: #FFAA00; text-shadow: 0 0 10px rgba(255, 170, 0, 0.6); }
.status-critical { color: #FF4444; text-shadow: 0 0 10px rgba(255, 68, 68, 0.6); }
.stProgress div div {
    background: linear-gradient(90deg, rgba(0,229,255,0.4), rgba(0,229,255,1));
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.8);
}
.suit-hologram { text-align: center; margin: 30px 0; }
.hud-circle {
    width: 150px;
    height: 150px;
    border: 3px solid rgba(0, 229, 255, 0.3);
    border-radius: 50%;
    margin: 20px auto;
    animation: hudRotate 4s linear infinite;
}
.hud-circle:before {
    content: "";
    position: absolute;
    top: -5px;
    left: 50%;
    width: 10px;
    height: 10px;
    background: #00E5FF;
    border-radius: 50%;
    box-shadow: 0 0 20px #00E5FF;
}
@keyframes hudRotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
"""

st.markdown(css_style, unsafe_allow_html=True)

SECRET_KEY = None
if "GROQ_API_KEY" in st.secrets:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
elif "groq_api_key" in st.secrets:
    SECRET_KEY = st.secrets["groq_api_key"]
elif os.environ.get("GROQ_API_KEY"):
    SECRET_KEY = os.environ.get("GROQ_API_KEY")

if "armor_durability" not in st.session_state:
    st.session_state.armor_durability = 100
if "reactor_temp" not in st.session_state:
    st.session_state.reactor_temp = 42
if "system_logs" not in st.session_state:
    st.session_state.system_logs = ["[12:00:00] Mainframe online.", "[12:00:01] Grid projected."]
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Good day, sir. J.A.R.V.I.S. operational. Ready, sir."}]

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, "[" + timestamp + "] " + message)

st.session_state.reactor_temp = random.randint(39, 45)

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

st.title("⚙️ J.A.R.V.I.S. // DIAGNOSTICS MAINFRAME")
st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("""
<div class="suit-hologram">
<div style="text-align: center; font-size: 100px; color: #00E5FF; text-shadow: 0 0 30px rgba(0,229,255,0.8);">🤖</div>
<div style="text-align: center; color: #00E5FF; margin-top: 10px; font-size: 14px;">⚡ ARC REACTOR ACTIVE ⚡</div>
<div class="hud-circle"></div>
</div>
""", unsafe_allow_html=True)

master_left, master_right = st.columns([5, 7])

with master_left:
    st.write("### 🎛️ CORE TELEMETRY")
    
    box_col1, box_col2 = st.columns(2)
    with box_col1:
        st.markdown("#### 🛡️ SUIT INTEGRITY")
        st.write("Armor: **" + armor_status + ">" + str(st.session_state.armor_durability) + "%</" + armor_status + "** (" + armor_level + ")")
        st.progress(st.session_state.armor_durability / 100)
        if st.session_state.armor_durability < 50:
            st.error("⚠️ CRITICAL: Integrity compromised, sir")
        
    with box_col2:
        st.markdown("#### 🌡️ ARC REACTOR")
        st.write("Temp: **" + reactor_status + ">" + str(st.session_state.reactor_temp) + "°C</" + reactor_status + "** (" + reactor_level + ")")
        st.progress(min(1.0, st.session_state.reactor_temp / 100))
        if st.session_state.reactor_temp > 50:
            st.error("⚠️ WARNING: Temperature rising, sir")
            
    box_col3, box_col4 = st.columns(2)
    with box_col3:
        st.markdown("#### 🔧 UTILITIES")
        if st.button("♻️ Optimize Cache", use_container_width=True):
            log_event("CLEAN: Memory flushed.")
            st.rerun()
        if st.button("🛠️ Run Calibration", use_container_width=True):
            st.session_state.armor_durability = 100
            log_event("REPAIR: Reset.")
            st.rerun()
        if st.button("🔄 Refresh Metrics", use_container_width=True):
            st.session_state.reactor_temp = random.randint(39, 45)
            log_event("UPDATE: Refreshed.")
            st.rerun()
        if st.button("⚡ Engage Cloak", use_container_width=True):
            log_event("CLOAK: Stealth active.")
            st.rerun()
            
    with box_col4:
        st.markdown("#### 💾 LOG STREAM")
        log_box = ""
        for log in st.session_state.system_logs[:5]:
            log_box = log_box + log + chr(10)
        st.code(log_box, language="bash")

with master_right:
    st.write("### 📡 SECURE COMM-LINK")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_prompt = st.chat_input("Enter command...")
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)
            
        if not SECRET_KEY:
            with st.chat_message("assistant"):
                st.error("🚨 No API key")
            st.session_state.messages.append({"role": "assistant", "content": "Link dropped, sir. Missing key."})
            log_event("REJECT: Key missing.")
            st.rerun()
        
        system_prompt = "You are J.A.R.V.I.S., Tony Stark AI from Marvel MCU. Address user as sir. British precision, formal tone, dry wit. No contractions. METRICS: Suit=" + str(st.session_state.armor_durability) + "% (" + armor_level + "), Reactor=" + str(st.session_state.reactor_temp) + "C (" + reactor_level + "). Warn if armor<50% or reactor>50C. End with Further assistance, sir? Stay in character."
        
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
                    temperature=0.75
                )
                ai_reply = chat_completion.choices[0].message.content
                response_placeholder.write(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                log_event("COMM: Processed.")
            except Exception as api_err:
                response_placeholder.write("🚨 Error: " + str(api_err))
                log_event("ERROR: Stream broken.")
                
        st.rerun()
