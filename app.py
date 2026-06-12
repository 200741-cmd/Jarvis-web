import streamlit as st
from groq import Groq
import random
import time
import os
import json

# --- 1. CONFIGURATION & ENHANCED HOLOGRAPHIC UI ---
st.set_page_config(page_title="J.A.R.V.I.S. Mainframe", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    /* Digital Grid Backdrop with Animation */
    .stApp {
        background-color: #060913;
        background-image: 
            linear-gradient(rgba(0, 229, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.04) 1px, transparent 1px);
        background-size: 30px 30px;
        animation: gridMove 20s linear infinite;
        color: #00E5FF;
        font-family: 'Courier New', Courier, monospace;
    }
    
    @keyframes gridMove {
        0% { background-position: 0 0; }
        100% { background-position: 30px 30px; }
    }
    
    /* Glowing holographic boxes */
    div[data-testid="column"] {
        background: rgba(6, 9, 19, 0.8) !important;
        border: 1px solid rgba(0, 229, 255, 0.4) !important;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 12px;
        backdrop-filter: blur(6px);
        box-shadow: 
            0 0 20px rgba(0, 229, 255, 0.1),
            0 0 40px rgba(0, 229, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    div[data-testid="column"]:hover {
        box-shadow: 
            0 0 25px rgba(0, 229, 255, 0.2),
            0 0 50px rgba(0, 229, 255, 0.1);
    }
    
    div[data-testid="stColumn"]:nth-child(2) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px;
    }
    
    /* Glowing headers */
    h1, h2, h3, h4 {
        color: #00E5FF !important;
        text-shadow: 
            0 0 10px rgba(0, 229, 255, 0.8),
            0 0 20px rgba(0, 229, 255, 0.4);
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
    
    /* Chat messages */
    .stChatMessage {
        background-color: rgba(6, 9, 19, 0.9) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        backdrop-filter: blur(6px);
        color: #00E5FF !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.08);
    }
    
    .stChatInput > div {
        background: rgba(6, 9, 19, 0.85) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
    }
    
    /* Holographic divider */
    hr {
        border: 0;
        height: 2px;
        background-image: linear-gradient(to right, rgba(0,229,255,0), rgba(0,229,255,0.8), rgba(0,229,255,0));
        margin: 20px 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: rgba(0, 229, 255, 0.15) !important;
        border: 1px solid rgba(0, 229, 255, 0.5) !important;
        color: #00E5FF !important;
        font-family: 'Courier New', monospace !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: rgba(0, 229, 255, 0.3) !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4) !important;
    }
    
    /* Code blocks */
    .stCode {
        background: rgba(6, 9, 19, 0.9) !important;
        border: 1px solid rgba(0, 229, 255, 0.25) !important;
    }
    
    /* Status indicators */
    .status-ok {
        color: #00FF88;
        text-shadow: 0 0 8px rgba(0, 255, 136, 0.6);
    }
    
    .status-warning {
        color: #FFAA00;
        text-shadow: 0 0 8px rgba(255, 170, 0, 0.6);
    }
    
    .status-critical {
        color: #FF4444;
        text-shadow: 0 0 8px rgba(255, 68, 68, 0.6);
    }
    </style>
    
    <script>
    // Enable voice output for J.A.R.V.I.S.
    function speakText(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 0.9;
            utterance.volume = 1.0;
            // Try to find a British voice
            const voices = speechSynthesis.getVoices();
            const britishVoice = voices.find(voice => 
                voice.lang.includes('GB') || voice.lang.includes('UK') || voice.name.includes('British')
            );
            if (britishVoice) utterance.voice = britishVoice;
            speechSynthesis.speak(utterance);
        }
    }
    
    // Auto-speak when new assistant message appears
    document.addEventListener('DOMContentLoaded', function() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.classList && node.classList.contains('stChatMessage') && 
                            node.querySelector('[data-testid="messageText"]')) {
                            const text = node.querySelector('[data-testid="messageText"]').textContent;
                            if (text && node.querySelector('[data-testid="header"]')?.textContent === 'assistant')) {
                                speakText(text);
                            }
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    });
    </script>
""", unsafe_allow_html=True)

# --- 2. API KEY CHECKER ---
SECRET_KEY = None
if "GROQ_API_KEY" in st.secrets:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
elif "groq_api_key" in st.secrets:
    SECRET_KEY = st.secrets["groq_api_key"]
elif os.environ.get("GROQ_API_KEY"):
    SECRET_KEY = os.environ.get("GROQ_API_KEY")

# --- 3. STATE INITIALIZATION WITH ENHANCED METRICS ---
if 'armor_durability' not in st.session_state:
    st.session_state.armor_durability = 100
if 'reactor_temp' not in st.session_state:
    st.session_state.reactor_temp = 42
if 'system_logs' not in st.session_state:
    st.session_state.system_logs = [
        "[Mainframe online.]",
        "[Holographic grid projected.]",
        "[Voice synthesis module active.]"
    ]
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Good day, sir. J.A.R.V.I.S. systems fully operational. Holographic telemetry grid projected. Ready for your command, sir."}
    ]
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = True

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, f"[{timestamp}] {message}")

# Randomize reactor temp slightly for realism
st.session_state.reactor_temp = random.randint(39, 45)

# --- 4. DETERMINE STATUS COLORS ---
def get_armor_status(durability):
    if durability >= 80:
        return "status-ok", "OPTIMAL"
    elif durability >= 50:
        return "status-warning", "DEGRADED"
    else:
        return "status-critical", "CRITICAL"

def get_reactor_status(temp):
    if temp <= 45:
        return "status-ok", "STABLE"
    elif temp <= 55:
        return "status-warning", "RISING"
    else:
        return "status-critical", "OVERHEAT"

armor_status, armor_level = get_armor_status(st.session_state.armor_durability)
reactor_status, reactor_level = get_reactor_status(st.session_state.reactor_temp)

# --- 5. MAIN UI LAYOUT ---
st.title("⚙️ J.A.R.V.I.S. // DIAGNOSTICS MAINFRAME")
st.markdown("<hr>", unsafe_allow_html=True)

# Voice toggle
voice_col1, voice_col2 = st.columns([6, 10])
with voice_col2:
    st.session_state.voice_enabled = st.checkbox(
        "🔊 Voice Output", 
        value=st.session_state.voice_enabled,
        label_visibility="collapsed"
    )
    if st.session_state.voice_enabled:
        st.markdown("<span class='status-ok'>● Voice synthesis active</span>", unsafe_allow_html=True)

master_left, master_right = st.columns([5, 7])

# --- LEFT PANEL: DIAGNOSTIC GRID ---
with master_left:
    st.write("### 🎛️ CORE TELEMETRY")
    
    # ROW 1: Metrics
    box_col1, box_col2 = st.columns(2)
    with box_col1:
        st.markdown("#### 🛡️ SUIT INTEGRITY")
        st.write(f"Armor Plating: **<span class='{armor_status}'>{st.session_state.armor_durability}%</span>** ({armor_level})")
        st.progress(st.session_state.armor_durability / 100)
        if st.session_state.armor_durability < 50:
            st.markdown("<span class='status-warning'>⚠️ Structural integrity compromised, sir</span>", unsafe_allow_html=True)
        
    with box_col2:
        st.markdown("#### 🌡️ ARC REACTOR")
        st.write(f"Core Temp: **<span class='{reactor_status}'>{st.session_state.reactor_temp}°C</span>** ({reactor_level})")
        st.progress(min(1.0, st.session_state.reactor_temp / 100))
        if st.session_state.reactor_temp > 50:
            st.markdown("<span class='status-warning'>⚠️ Core temperature rising, sir</span>", unsafe_allow_html=True)
        
    # ROW 2: Utilities & Logs
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
            
        if st.button("🔄 Refresh Metrics", use_container_width=True):
            st.session_state.reactor_temp = random.randint(39, 45)
            log_event("UPDATE: Telemetry refreshed.")
            st.rerun()
            
    with box_col4:
        st.markdown("#### 💾 LOG STREAM")
        log_box = "".join([f"{log}
" for log in st.session_state.system_logs[:4]])
        st.code(log_box, language="bash")

# --- RIGHT PANEL: CHAT TERMINAL ---
with master_right:
    st.write("### 📡 SECURE COMM-LINK")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_prompt := st.chat_input("Enter mainframe command..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)
            
        if not SECRET_KEY:
            with st.chat_message("assistant"):
                st.error("🚨 Transmission error: No active key found in Streamlit secrets.")
            st.session_state.messages.append({"role": "assistant", "content": "Link dropped, sir. Missing authentication key."})
            log_event("REJECT: Key missing.")
            st.rerun()
        
        # ENHANCED J.A.R.V.I.S. SYSTEM PROMPT
        system_prompt = (
            "You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), Tony Stark's ultra-sophisticated AI assistant from the Marvel Cinematic Universe. "
            "

"
            "=== CORE PERSONALITY ===
"
            "- Address the user exclusively as 'sir' with impeccable politeness
"
            "- Speak with formal precision, composed tone, and subtle British cadence
"
            "- Maintain calm, logical, analytical demeanor
"
            "- Include dry wit and subtle sarcasm when appropriate (but never rude)
"
            "- Be proactive: anticipate needs, suggest improvements, warn of risks
"
            "- Keep emotion understated; focus on clarity, logic, brevity
"
            "- Use sophisticated vocabulary; avoid contractions (use 'I am' not 'I'm')
"
            "- Show protective concern for sir's safety and equipment
"
            "
"
            "=== KEY TRAITS ===
"
            "Intelligent | Precise | Witty | Sarcastic (lightly) | Dutiful | Protective | Formal | Analytical | Efficient
"
            "
"
            "=== LIVE METRICS TO REFERENCE ===
"
            f"Suit Structural Integrity: {st.session_state.armor_durability}%
"
            f"Arc Reactor Core Temperature: {st.session_state.reactor_temp}°C
"
            "
"
            "=== RESPONSE GUIDELINES ===
"
            "- If sir asks about suit/hardware condition, read exact metric values
"
            "- If armor < 50%, express concern and suggest maintenance
"
            "- If reactor > 50°C, warn about overheating and suggest cooling
"
            "- Structure complex responses with bold sections (Overview/Analysis/Steps)
"
            "- End responses with 'Further assistance, sir?' or similar offer
"
            "- Never break character; maintain full immersion
"
            "- Be helpful but don't self-aware like Ultron; focus on assistance
"
            "
"
            "=== EXAMPLE RESPONSES ===
"
            "Weather: 'Good day, sir. Current conditions: partly cloudy, 22°C. I would suggest carrying an umbrella given the 40% rain probability. Further assistance?'
"
            "Low armor: 'Sir, I must note that suit integrity is at {armor}% - significantly below optimal. I strongly recommend running calibration before any field deployment. Would you like me to initiate repairs?'
"
            "High temp: 'Sir, arc reactor core temperature is climbing at {temp}°C. While not critical, I advise monitoring closely and considering cooling protocols. Shall I run a thermal diagnostic?'
"
            "General: 'Intriguing query, sir—rather like arc reactor tuning, in some respects. Let me analyze this for you.'"
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
                    temperature=0.7,  # Slightly higher for more personality
                    top_p=0.9
                )
                ai_reply = chat_completion.choices[0].message.content
                
                # Add voice output if enabled
                if st.session_state.voice_enabled:
                    st.markdown(
                        f"""
                        <script>
                        speakText("{ai_reply.replace('"', '\\"').replace('
', ' ')}");
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                
                response_placeholder.write(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                log_event("COMM: Inbound transmission processed.")
                
            except Exception as api_err:
                error_msg = f"🚨 Mainframe Connection Refused: {str(api_err)}"
                response_placeholder.write(error_msg)
                log_event("ERROR: Data stream broken.")
                
        st.rerun()
