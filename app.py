
import streamlit as st
from groq import Groq
import random
import time
import os

st.set_page_config(page_title="J.A.R.V.I.S. Mainframe", page_icon="🤖", layout="wide")

# Simple CSS without problematic quotes
css_style = """
<style>
.stApp {
    background-color: #060913;
    color: #00E5FF;
    font-family: Courier New, Courier, monospace;
}
div[data-testid="column"] {
    background: rgba(6, 9, 19, 0.8);
    border: 1px solid rgba(0, 229, 255, 0.4);
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 12px;
}
div[data-testid="stColumn"]:nth-child(2) {
    background: transparent;
    border: none;
    padding: 0px;
}
h1, h2, h3, h4 {
    color: #00E5FF;
    letter-spacing: 3px;
    font-weight: 600;
}
.stChatMessage {
    background-color: rgba(6, 9, 19, 0.9);
    border: 1px solid rgba(0, 229, 255, 0.3);
    color: #00E5FF;
}
.stButton button {
    background: rgba(0, 229, 255, 0.15);
    border: 1px solid rgba(0, 229, 255, 0.5);
    color: #00E5FF;
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

if 'armor_durability' not in st.session_state:
    st.session_state.armor_durability = 100
if 'reactor_temp' not in st.session_state:
    st.session_state.reactor_temp = 42
if 'system_logs' not in st.session_state:
    st.session_state.system_logs = ["Mainframe online.", "Grid projected."]
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Good day, sir. J.A.R.V.I.S. operational. Ready, sir."}]

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, "[" + timestamp + "] " + message)

st.session_state.reactor_temp = random.randint(39, 45)

st.title("J.A.R.V.I.S. // DIAGNOSTICS MAINFRAME")

master_left, master_right = st.columns([5, 7])

with master_left:
    st.write("### CORE TELEMETRY")
    
    box_col1, box_col2 = st.columns(2)
    with box_col1:
        st.markdown("#### SUIT INTEGRITY")
        st.write("Armor: " + str(st.session_state.armor_durability) + "%")
        st.progress(st.session_state.armor_durability / 100)
        if st.session_state.armor_durability < 50:
            st.warning("Integrity compromised, sir")
        
    with box_col2:
        st.markdown("#### ARC REACTOR")
        st.write("Temp: " + str(st.session_state.reactor_temp) + "C")
        st.progress(min(1.0, st.session_state.reactor_temp / 100))
        if st.session_state.reactor_temp > 50:
            st.warning("Temperature rising, sir")
            
    box_col3, box_col4 = st.columns(2)
    with box_col3:
        st.markdown("#### UTILITIES")
        if st.button("Optimize Cache", use_container_width=True):
            log_event("CLEAN: Memory flushed.")
            st.rerun()
        if st.button("Run Calibration", use_container_width=True):
            st.session_state.armor_durability = 100
            log_event("REPAIR: Reset.")
            st.rerun()
        if st.button("Refresh Metrics", use_container_width=True):
            st.session_state.reactor_temp = random.randint(39, 45)
            log_event("UPDATE: Refreshed.")
            st.rerun()
            
    with box_col4:
        st.markdown("#### LOG STREAM")
        log_box = ""
        for log in st.session_state.system_logs[:4]:
            log_box = log_box + log + chr(10)
        st.code(log_box, language="bash")

with master_right:
    st.write("### COMM-LINK")
    
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
                st.error("🚨 No API key found.")
            st.session_state.messages.append({"role": "assistant", "content": "Link dropped, sir. Missing key."})
            log_event("REJECT: Key missing.")
            st.rerun()
        
        system_prompt = "You are J.A.R.V.I.S., Tony Starks AI assistant. Address user as sir. Speak formally with British precision and dry wit. METRICS: Suit=" + str(st.session_state.armor_durability) + "%, Reactor=" + str(st.session_state.reactor_temp) + "C. Warn if armor low or reactor high. End with Further assistance, sir?"
        
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
                response_placeholder.write("🚨 Error: " + str(api_err))
                log_event("ERROR: Stream broken.")
                
        st.rerun()
