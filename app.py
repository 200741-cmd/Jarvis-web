import streamlit as st
from groq import Groq
import random
import time

# --- 1. INITIALIZE GROQ CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing Groq API Key! Please configure GROQ_API_KEY in your Streamlit secrets.")
    st.stop()

# --- 2. CONFIGURATION & HOLOGRAPHIC GRID BACKGROUND STYLING ---
st.set_page_config(page_title="J.A.R.V.I.S. Mainframe", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    /* Digital Grid Backdrop Engine */
    .stApp {
        background-color: #060913;
        background-image: 
            linear-gradient(rgba(0, 229, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.04) 1px, transparent 1px);
        background-size: 30px 30px; /* Size of the backdrop grid squares */
        color: #00E5FF;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Transparent blur for the metric boxes so the background grid peeks through */
    div[data-testid="column"] {
        background: rgba(6, 9, 19, 0.75) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 10px;
        backdrop-filter: blur(4px); /* Frost effect over background grid */
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.05);
    }
    
    /* Clear outer pane container limits */
    div[data-testid="stColumn"]:nth-child(2) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px;
    }
    
    h1, h2, h3, h4 {
        color: #00E5FF !important;
        text-shadow: 0 0 8px rgba(0, 229, 255, 0.6);
        letter-spacing: 2px;
        margin-top: 0px;
    }
    
    .stChatMessage {
        background-color: rgba(6, 9, 19, 0.85) !important;
        border: 1px solid rgba(0, 229, 255, 0.25) !important;
        backdrop-filter: blur(4px);
        color: #00E5FF !important;
    }
    
    hr {
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0,229,255,0), rgba(0,229,255,0.5), rgba(0,229,255,0));
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. STATE INITIALIZATION ---
if 'armor_durability' not in st.session_state:
    st.session_state.armor_durability = 100
if 'reactor_temp' not in st.session_state:
    st.session_state.reactor_temp = 42
if 'system_logs' not in st.session_state:
    st.session_state.system_logs = ["Mainframe online.", "Holographic backdrop grid projected."]
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Grid telemetry projection complete, sir. Ready for input."}]

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, f"[{timestamp}] {message}")

st.session_state.reactor_temp = random.randint(39, 45)

# --- 4. MAIN UI LAYOUT ---
st.title("⚙️ J.A.R.V.I.S. // DIAGNOSTICS MAINFRAME")
st.markdown("<hr>", unsafe_allow_html=True)

master_left, master_right = st.columns([5, 7])

# --- LEFT PANEL: THE GRID OF DIAGNOSTIC BOXES ---
with master_left:
    st.write("### 🎛️ CORE TELEMETRY")
    
    # ROW 1: Metrics Displays
    box_col1, box_col2 = st.columns(2)
    with box_col1:
        st.markdown("#### 🛡️ SUIT INTEGRITY")
        st.write(f"Armor Plating: **{st.session_state.armor_durability}%**")
        st.progress(st.session_state.armor_durability / 100)
        
    with box_col2:
        st.markdown("#### 🌡️ ARC REACTOR")
        st.write(f"Core Temp: **{st.session_state.reactor_temp}°C**")
        st.progress(min(1.0, st.session_state.reactor_temp / 100))
        
    # ROW 2: Maintenance & Log Readouts
    box_col3, box_col4 = st.columns(2)
    with box_col3:
        st.markdown("#### 🔧 UTILITIES")
        if st.button("♻️ Optimize Cache", use_container_width=True):
            log_event("CLEAN: Memory buffers flushed.")
            st.rerun()
            
        if st.button("🛠️ Run Calibration", use_container_width=True):
            st.session_state.armor_durability = 100
            log_event("REPAIR: Structural parameters reset.")
            st.rerun()
            
    with box_col4:
        st.markdown("#### 💾 LOG STREAM")
        log_box = "".join([f"{log}\n" for log in st.session_state.system_logs[:3]])
        st.code(log_box, language="bash")

# --- RIGHT PANEL: WORKING CHAT TERMINAL ---
with master_right:
    st.write("### 📡 SECURE COMM-LINK")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_prompt := st.chat_input("Enter mainframe command..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)
            
        system_prompt = (
            "You are J.A.R.V.I.S., the ultra-intelligent AI assistant built by Tony Stark. "
            "You always address the user as 'sir'. Respond with scientific, high-tech, and helpful language. "
            f"LIVE METRICS - Suit Structural Integrity: {st.session_state.armor_durability}%, "
            f"Arc Reactor Core Temperature: {st.session_state.reactor_temp} degrees Celsius. "
            "If the user asks about the condition of the suit or hardware, read out these exact values."
        )
        
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages[-10:]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
            
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            try:
                chat_completion = client.chat.completions.create(
                    messages=api_messages,
                    model="llama3-8b-8192", 
                    temperature=0.6
                )
                ai_reply = chat_completion.choices[0].message.content
                response_placeholder.write(ai_reply)
                
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                log_event("COMM: Inbound transmission processed.")
                
            except Exception as api_err:
                error_msg = f"API Link Error: {str(api_err)}"
                response_placeholder.write(error_msg)
                log_event("ERROR: Link drop.")
                
        st.rerun()
