import streamlit as st
import speech_recognition as sr
import datetime
import wikipedia
import psutil
import io
import time
from gtts import gTTS
from google import genai
from google.genai import types

# 1. PAGE CONFIG
st.set_page_config(
    page_title="J.A.R.V.I.S. // Diagnostics Mainframe",
    page_icon="💠",
    layout="wide"
)

# 2. SESSION STATE DEFAULTS
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "J.A.R.V.I.S."
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = True
if "processing_query" not in st.session_state:
    st.session_state.processing_query = None
if "system_logs" not in st.session_state:
    st.session_state.system_logs = ["Mainframe online.", "Grid projection locked."]

# 3. DYNAMIC THEME ENGINE MAPPING
theme_palettes = {
    "J.A.R.V.I.S.": {"primary": "#00E5FF", "bg": "#060913", "rgb": "0, 229, 255"},
    "F.R.I.D.A.Y.": {"primary": "#FF9900", "bg": "#120B04", "rgb": "255, 153, 0"},
    "E.D.I.T.H.": {"primary": "#FF3333", "bg": "#120404", "rgb": "255, 51, 51"},
    "BOTH": {"primary": "#BF00FF", "bg": "#0D0412", "rgb": "191, 0, 255"}
}

active_theme = theme_palettes.get(st.session_state.ai_persona, theme_palettes["J.A.R.V.I.S."])

# EXACT REFERENCE STARK GRID & CONTAINER STYLING
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+New:wght@400;700&display=swap');
    
    .stApp {{
        background-color: {active_theme['bg']};
        background-image: 
            linear-gradient(rgba({active_theme['rgb']}, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba({active_theme['rgb']}, 0.04) 1px, transparent 1px);
        background-size: 30px 30px;
        color: {active_theme['primary']};
        font-family: 'Courier New', Courier, monospace;
    }}
    
    div[data-testid="column"] {{
        background: rgba(6, 9, 19, 0.75) !important;
        border: 1px solid rgba({active_theme['rgb']}, 0.3) !important;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 10px;
        backdrop-filter: blur(4px);
        box-shadow: 0 0 15px rgba({active_theme['rgb']}, 0.05);
    }}
    
    .stChatMessage {{
        background-color: rgba(6, 9, 19, 0.85) !important;
        border: 1px solid rgba({active_theme['rgb']}, 0.25) !important;
        backdrop-filter: blur(4px);
        color: {active_theme['primary']} !important;
        border-radius: 6px !important;
    }}

    h1, h2, h3, h4 {{
        color: {active_theme['primary']} !important;
        font-family: 'Courier New', Courier, monospace !important;
        letter-spacing: 1px;
    }}

    .stButton > button {{
        background: rgba(6, 9, 19, 0.9) !important;
        border: 1px solid {active_theme['primary']} !important;
        color: {active_theme['primary']} !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-weight: bold !important;
        border-radius: 4px !important;
    }}
</style>
""", unsafe_allow_html=True)

# 4. SECURE CLIENT INITIALIZATION
@st.cache_resource
def get_genai_client():
    api_key = None
    try:
        api_key = st.secrets.get("API_KEY", "") or st.secrets.get("API_KEY_1", "") or st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

client = get_genai_client()

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, f"[{timestamp}] {message}")
    if len(st.session_state.system_logs) > 6:
        st.session_state.system_logs.pop()

# 5. HEADER EXACTLY LIKE THE REFERENCE IMAGE
st.markdown(f"<h1>⚙️ {st.session_state.ai_persona.upper()} // DIAGNOSTICS MAINFRAME</h1>", unsafe_allow_html=True)
st.markdown(f"<hr style='border: 0.5px solid rgba({active_theme['rgb']}, 0.3); margin-bottom: 25px;'>", unsafe_allow_html=True)

# 6. MASTER TWO-COLUMN LAYOUT
col_left, col_right = st.columns([1, 1.5], gap="large")

# --- LEFT COLUMN: CORE TELEMETRY ---
with col_left:
    st.markdown("#### 🎛️ CORE TELEMETRY")
    
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    
    st.markdown("<span style='font-size: 12px; color: #888;'>ARMOR INTEGRITY</span>", unsafe_allow_html=True)
    st.markdown("<h2>100%</h2>", unsafe_allow_html=True)
    
    st.markdown(f"⚡ **CPU LOAD:** {cpu}%")
    st.progress(min(1.0, cpu / 100.0))
    
    st.markdown(f"🔋 **VRAM ALLOCATED:** {ram}%")
    st.progress(min(1.0, ram / 100.0))
    
    st.markdown("---")
    st.markdown("#### 🔧 SYSTEM CONTROLS")
    
    protocols = ["F.R.I.D.A.Y.", "J.A.R.V.I.S.", "E.D.I.T.H.", "BOTH"]
    current_index = protocols.index(st.session_state.ai_persona) if st.session_state.ai_persona in protocols else 0
    selected_persona = st.selectbox("Active Protocol", protocols, index=current_index)
    if selected_persona != st.session_state.ai_persona:
        st.session_state.ai_persona = selected_persona
        log_event(f"Protocol shifted to {selected_persona}. Theme re-calibrated.")
        st.rerun()

    tts_toggle = st.checkbox("Audio Voice Feedback (TTS)", value=st.session_state.tts_enabled)
    if tts_toggle != st.session_state.tts_enabled:
        st.session_state.tts_enabled = tts_toggle
        st.rerun()

    if st.button("♻️ Optimize Cache", use_container_width=True):
        st.session_state.chat_history = []
        log_event("CLEAN: Memory buffers flushed.")
        st.rerun()

# --- RIGHT COLUMN: SECURE COMM-LINK ---
with col_right:
    st.markdown("#### 📡 SECURE COMM-LINK")

    # Top Status Message Box matching reference card style
    if not st.session_state.chat_history:
        st.info(f"Good day, sir. {st.session_state.ai_persona} operational. Direct Google core link active via gemini-3.5-flash-lite.")
    
    # Input Command Line matching reference position
    user_prompt = st.chat_input("Enter strategic command...")
    recorded_audio = st.audio_input("Open Audio Frequency Receiver")

    active_query = None
    if recorded_audio:
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(io.BytesIO(recorded_audio.read())) as source:
                audio_data = recognizer.record(source)
            active_query = recognizer.recognize_google(audio_data, language='en-US')
        except Exception:
            active_query = "Error decoding audio waveform stream."

    if user_prompt:
        active_query = user_prompt

    # Render previous chat interactions below the input section
    for chat in reversed(st.session_state.chat_history):
        with st.chat_message("user", avatar="👤"):
            st.write(chat["user"])
        with st.chat_message("assistant", avatar="💠"):
            st.write(chat["bot"])
            if chat.get("audio") and st.session_state.tts_enabled:
                st.audio(chat["audio"], format="audio/mp3")

    # Query Processing Loop
    if active_query and active_query != st.session_state.processing_query:
        st.session_state.processing_query = active_query
        
        with st.chat_message("user", avatar="👤"):
            st.write(active_query)

        if not client:
            with st.chat_message("assistant", avatar="💠"):
                st.error("🚨 Transmission error: No active key found in the Streamlit secrets panel.")
            ai_reply = "Link drop. Missing key."
            log_event("REJECT: Key missing.")
        else:
            try:
                query_lower = active_query.lower()
                if "wikipedia" in query_lower:
                    search_target = query_lower.replace("wikipedia", "").strip()
                    ai_reply = wikipedia.summary(search_target, sentences=2)
                else:
                    if st.session_state.ai_persona == "E.D.I.T.H.":
                        sys_inst = "You are E.D.I.T.H., orbital defense satellite system. Address the user as sir. Focus on tactical security metrics."
                    elif st.session_state.ai_persona == "J.A.R.V.I.S.":
                        sys_inst = "You are J.A.R.V.I.S., the ultra-intelligent AI assistant built by Tony Stark. Address the user as sir."
                    elif st.session_state.ai_persona == "BOTH":
                        sys_inst = "Provide a joint perspective combining F.R.I.D.A.Y. and J.A.R.V.I.S. traits. Address the user as sir."
                    else:
                        sys_inst = "You are F.R.I.D.A.Y., witty and sharp AI built by Tony Stark. Address the user as sir."

                    response = client.models.generate_content(
                        model='gemini-3.5-flash-lite',
                        contents=active_query,
                        config={'system_instruction': sys_inst}
                    )
                    ai_reply = response.text

                audio_bytes = None
                if st.session_state.tts_enabled:
                    tld_mapping = {
                        "F.R.I.D.A.Y.": "ie",
                        "J.A.R.V.I.S.": "co.uk",
                        "E.D.I.T.H.": "com",
                        "BOTH": "co.uk"
                    }
                    tld_val = tld_mapping.get(st.session_state.ai_persona, "com")
                    
                    tts = gTTS(text=ai_reply, lang='en', tld=tld_val)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    audio_bytes = fp.read()

                with st.chat_message("assistant", avatar="💠"):
                    st.write(ai_reply)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")

                log_event("COMM: Inbound transmission processed.")
            except Exception as api_err:
                error_msg = f"🚨 Mainframe Connection Refused: {str(api_err)}"
                with st.chat_message("assistant", avatar="💠"):
                    st.error(error_msg)
                ai_reply = error_msg
                log_event("ERROR: Data stream broken.")

        st.session_state.chat_history.append({"user": active_query, "bot": ai_reply, "audio": audio_bytes if 'audio_bytes' in locals() else None})
        st.session_state.processing_query = None
        st.rerun()
