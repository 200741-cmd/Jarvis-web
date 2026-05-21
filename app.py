import streamlit as st
from groq import Groq
import random
import time

# --- 1. INITIALIZE GROQ CLIENT ---
# This pulls securely from your Streamlit secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing Groq API Key! Please configure GROQ_API_KEY in your Streamlit secrets.")
    st.stop()

# --- 2. CONFIGURATION & STYLING ---
st.set_page_config(page_title="J.A.R.V.I.S. Mainframe", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0B0F19;
        color: #00E5FF;
        font-family: 'Courier New', Courier, monospace;
    }
    div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
        background: rgba(0, 229, 255, 0.03);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.1);
    }
    h1, h2, h3 {
        color: #00E5FF !important;
        text-shadow: 0 0 8px rgba(0, 229, 255, 0.6);
        letter-spacing: 2px;
    }
    .stChatMessage {
        background-color: rgba(11, 15, 25, 0.8) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        color: #00E5FF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. STATE INITIALIZATION ---
if 'armor_durability' not in st.session_state:
    st.session_state.armor_durability = 100
if 'arc_reactor_charge' not in st.session_state:
    st.session_state.arc_reactor_charge = 100
if 'system_logs' not in st.session_state:
    st.session_state.system_logs = ["System Initialized.", "All sub-routines online."]
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Online and ready, sir. Mainframe link established."}]

# --- 4. CORE MECHANICS ---
def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, f"[{timestamp}] {message}")

def take_damage(amount):
    st.session_state.armor_durability = max(0, st.session_state.armor_durability - amount)
    st.session_state.arc_reactor_charge = max(0, st.session_state.arc_reactor_charge - random.randint(2, 6))
    log_event(f"CRITICAL: Hull breach detected! Lost {amount}% integrity.")

def repair_armor():
    st.session_state.armor_durability = 100
    st.session_state.arc_reactor_charge = 100
    log_event("SUCCESS: Nanotech reconstruction complete. Systems at 100%.")

# --- 5. UI LAYOUT ---
st.title("⚡ J.A.R.V.I.S. MAIN INTERFACE")
st.markdown("---")

col_left, col_right = st.columns([1, 2])

# LEFT PANEL: Statistics and Hardware
with col_left:
    st.subheader("📊 SYSTEM STATUS")
    
    durability = st.session_state.armor_durability
    st.write(f"**Armor Integrity:** {durability}%")
    st.progress(durability / 100)
    
    energy = st.session_state.arc_reactor_charge
    st.write(f"**Arc Reactor Output:** {energy}%")
    st.progress(energy / 100)
    
    if durability < 30:
        st.error("🚨 WARNING: ARMOR INTEGRITY FAILING")
    elif durability < 70:
        st.warning("⚠️ NOTICE: Titanium-gold alloy compromised.")
    else:
        st.success("🟢 Systems Nominal")
        
    st.markdown("### 🛠️ SIMULATION CONTROLS")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💥 Simulate Hit"):
            take_damage(random.randint(10, 25))
            st.rerun()
    with c2:
        if st.button("🔧 Deploy Repairs"):
            repair_armor()
            st.rerun()

    st.markdown("### 💾 MAINFRAME DIAGNOSTICS")
    log_box = "".join([f"{log}\n" for log in st.session_state.system_logs[:5]])
    st.code(log_box, language="bash")

# RIGHT PANEL: Live Chat Terminal connected to Groq
with col_right:
    st.subheader("💬 CORE TERMINAL COMM-LINK")
    
    # Render past chat logs
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Capture user keyboard input
    if user_prompt := st.chat_input("Access mainframe..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)
            
        # Build dynamic background story injected with live UI values
        system_prompt = (
            "You are J.A.R.V.I.S., the ultra-intelligent, slightly sarcastic AI assistant built by Tony Stark. "
            "You address the user as 'sir'. Respond with technical, high-tech phrasing. "
            f"CURRENT DATA TRACKERS - Armor Durability: {st.session_state.armor_durability}%, "
            f"Arc Reactor Power: {st.session_state.arc_reactor_charge}%. "
            "If the armor durability drops below 40%, you must express urgent concern for safety and remind them to run repairs."
        )
        
        # Assemble the full conversation history to feed Groq
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
            
        # Call Groq API endpoint
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            try:
                chat_completion = client.chat.completions.create(
                    messages=api_messages,
                    model="llama3-8b-8192", # Lightweight, hyper-fast engine model
                    temperature=0.7
                )
                ai_reply = chat_completion.choices[0].message.content
                response_placeholder.write(ai_reply)
                
                # Update history log
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                log_event(f"Response generated successfully.")
                
            except Exception as api_err:
                error_msg = f"API Error: Failed to contact mainframe core. {str(api_err)}"
                response_placeholder.write(error_msg)
                log_event("ERROR: Interface link dropped.")
                
        st.rerun()
