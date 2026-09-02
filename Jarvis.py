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
from PIL import Image

# 1. PAGE CONFIG
st.set_page_config(
    page_title="F.R.I.D.A.Y. // Tactical OS (v3.5 Lite)",
    page_icon="🟠",
    layout="wide"
)

# 2. SESSION STATE DEFAULTS
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "F.R.I.D.A.Y."
if "build_version" not in st.session_state:
    st.session_state.build_version = "v3.5-lite"
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = True
if "processing_query" not in st.session_state:
    st.session_state.processing_query = None

# DYNAMIC THEME ENGINE (Changes based on active protocol)
persona_colors = {
    "F.R.I.D.A.Y.": {"primary": "#ff9800", "border": "#e65100", "glow": "rgba(255, 152, 0, 0.6)", "bg": "#070402"},
    "J.A.R.V.I.S.": {"primary": "#00e5ff", "border": "#0091ea", "glow": "rgba(0, 229, 255, 0.6)", "bg": "#02060a"},
    "E.D.I.T.H.":   {"primary": "#ff1744", "border": "#d50000", "glow": "rgba(255, 23, 68, 0.6)", "bg": "#0a0203"},
    "BOTH":         {"primary": "#d500f9", "border": "#aa00ff", "glow": "rgba(213, 0, 249, 0.6)", "bg": "#06020a"}
}

active_theme = persona_colors.get(st.session_state.ai_persona, persona_colors["F.R.I.D.A.Y."])

# DYNAMIC STARK INDUSTRIAL THEME STYLING
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap');
    .stApp {{ background-color: {active_theme['bg']}; color: {active_theme['primary']}; font-family: 'Share Tech Mono', monospace; transition: background-color 0.5s ease; }}
    .cyber-title {{ color: {active_theme['primary']}; font-family: 'Orbitron', sans-serif; text-shadow: 0 0 15px {active_theme['glow']}; font-weight: 900; letter-spacing: 3px; }}
    .stark-card {{ background: linear-gradient(135deg, {active_theme['glow']} 0%, {active_theme['bg']} 90%); border: 1px solid {active_theme['border']}; padding: 20px; border-radius: 12px; box-shadow: 0 0 20px {active_theme['glow']}; margin-bottom: 15px; }}
    .stButton > button {{ background: transparent !important; border: 1.5px solid {active_theme['primary']} !important; color: {active_theme['primary']} !important; font-family: 'Orbitron' !important; font-weight: 700 !important; border-radius: 8px !important; }}
</style>
""", unsafe_allow_html=True)

# 3. SECURE CLIENT INITIALIZATION
@st.cache_resource
def get_genai_client():
    api_key = None
    try:
        api_key = st.secrets.get("API_KEY", "") or st.secrets.get("API_KEY_1", "")
    except Exception:
        pass
    
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

client = get_genai_client()

# 4. INTEGRATED MOVING ARC REACTOR & TELEMETRY DASHBOARD HEADER
cpu = psutil.cpu_percent(interval=None)
ram = psutil.virtual_memory().percent
link_status = "ONLINE" if client else "OFFLINE"
engine_title = f"EDITH SATELLITE DEFENSE (gemini-3.5-flash-lite)" if st.session_state.build_version == "EDITH-v1" else f"{st.session_state.ai_persona} // TACTICAL COMMAND (gemini-3.5-flash-lite)"

hud_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Share Tech Mono', monospace; }}
        body {{ background-color: transparent; color: {active_theme['primary']}; }}
        .hud-container {{
            background: linear-gradient(135deg, {active_theme['glow']} 0%, {active_theme['bg']} 95%);
            border: 2px solid {active_theme['border']};
            border-radius: 16px;
            padding: 20px;
            box-shadow: inset 0 0 25px {active_theme['border']}, 0 0 30px {active_theme['glow']};
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 220px;
            position: relative;
            overflow: hidden;
        }}
        .hud-left, .hud-right {{
            width: 28%;
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 12px;
            background: rgba(5, 10, 15, 0.7);
            padding: 12px;
            border: 1px solid {active_theme['border']};
            border-radius: 10px;
            box-shadow: 0 0 10px {active_theme['glow']};
        }}
        .hud-center {{
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
        }}
        .title-glow {{
            font-family: 'Orbitron', sans-serif;
            color: {active_theme['primary']};
            font-size: 15px;
            font-weight: 900;
            letter-spacing: 2px;
            text-shadow: 0 0 12px {active_theme['glow']};
            margin-bottom: 4px;
            text-align: center;
        }}
        .subtitle {{
            font-size: 10px;
            color: rgba(255, 255, 255, 0.7);
            letter-spacing: 1px;
            margin-bottom: 10px;
            text-align: center;
        }}
        .arc-rings {{
            width: 90px;
            height: 90px;
            border-radius: 50%;
            border: 2px dashed {active_theme['border']};
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            box-shadow: 0 0 20px {active_theme['glow']};
            animation: rotateCW 12s linear infinite;
        }}
        .arc-rings::before {{
            content: '';
            position: absolute;
            width: 70px;
            height: 70px;
            border-radius: 50%;
            border: 2px dotted {active_theme['primary']};
            animation: rotateCCW 8s linear infinite;
        }}
        .core-glow-dot {{
            width: 12px;
            height: 12px;
            background-color: {active_theme['primary']};
            border-radius: 50%;
            box-shadow: 0 0 25px 8px {active_theme['border']};
            animation: pulseGlow 2s ease-in-out infinite alternate;
        }}
        .bar-bg {{ background: {active_theme['border']}; opacity: 0.4; height: 6px; border-radius: 3px; overflow: hidden; margin-top: 2px; }}
        .bar-fill {{ height: 100%; background: {active_theme['primary']}; box-shadow: 0 0 8px {active_theme['primary']}; }}
        @keyframes rotateCW {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes rotateCCW {{ 100% {{ transform: rotate(-360deg); }} }}
        @keyframes pulseGlow {{ 0% {{ opacity: 0.7; transform: scale(0.95); }} 100% {{ opacity: 1; transform: scale(1.05); }} }}
    </style>
</head>
<body>
    <div class="hud-container">
        <div class="hud-left">
            <div><b>SYSTEM STATUS:</b> OPERATIONAL</div>
            <div><b>PROTOCOL:</b> {st.session_state.ai_persona}</div>
            <div><b>MAINFRAME LINK:</b> {link_status}</div>
            <div><b>LOG ENTRIES:</b> {len(st.session_state.chat_history)}</div>
        </div>
        
        <div class="hud-center">
            <div class="title-glow">{engine_title}</div>
            <div class="subtitle">STARK INDUSTRIES SECURE MAINFRAME (gemini-3.5-flash-lite)</div>
            <div class="arc-rings">
                <div class="core-glow-dot"></div>
            </div>
        </div>

        <div class="hud-right">
            <div><b>CPU LOAD:</b> {cpu}%</div>
            <div class="bar-bg"><div class="bar-fill" style="width: {cpu}%;"></div></div>
            <div><b>VRAM ALLOCATED:</b> {ram}%</div>
            <div class="bar-bg"><div class="bar-fill" style="width: {ram}%;"></div></div>
        </div>
    </div>
</body>
</html>
"""

st.components.v1.html(hud_html, height=240)
st.write("---")

# 5. MAIN CONTENT LAYOUT (Command Deck & Live Stream)
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.markdown("<div class='stark-card'>", unsafe_allow_html=True)
    st.subheader("🖥️ Command Deck")
    
    recorded_audio = st.audio_input("Open Microscopic Frequency Receiver")
    st.write("")
    
    text_override = st.chat_input("Feed manual string command line interface...", key="chat_input_field")
    st.markdown("</div>", unsafe_allow_html=True)

active_query = None
if recorded_audio:
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(recorded_audio.read())) as source:
            audio_data = recognizer.record(source)
        active_query = recognizer.recognize_google(audio_data, language='en-US')
    except Exception:
        active_query = "Error decoding audio waveform stream."

if text_override:
    active_query = text_override

with col2:
    st.subheader(f"📡 Live Neural Stream ({st.session_state.ai_persona} Core)")
    
    if active_query and active_query != st.session_state.processing_query:
        st.session_state.processing_query = active_query
        
        if not client:
            ai_response = "Error: Neural core offline. Please configure your 'API_KEY' in Streamlit secrets, Sir."
            audio_bytes = None
        else:
            try:
                query_lower = active_query.lower()
                if "wikipedia" in query_lower:
                    search_target = query_lower.replace("wikipedia", "").strip()
                    ai_response = wikipedia.summary(search_target, sentences=2)
                else:
                    if st.session_state.ai_persona == "E.D.I.T.H." or st.session_state.build_version == "EDITH-v1":
                        sys_inst = "You are E.D.I.T.H., orbital defense satellite system. Address the user as Sir. Focus on surveillance and tactical metrics."
                    elif st.session_state.ai_persona == "J.A.R.V.I.S.":
                        sys_inst = "You are J.A.R.V.I.S., polite, formal, British-accented assistant. Address the user as Sir."
                    elif st.session_state.ai_persona == "BOTH":
                        sys_inst = "Provide a joint perspective combining F.R.I.D.A.Y. and J.A.R.V.I.S. traits. Address the user as Sir."
                    else:
                        sys_inst = "You are F.R.I.D.A.Y., witty and sharp AI. Address the user as Sir."

                    # Using gemini-3.5-flash-lite for fast response generation
                    response = client.models.generate_content(
                        model='gemini-3.5-flash-lite',
                        contents=active_query,
                        config={'system_instruction': sys_inst}
                    )
                    ai_response = response.text

                audio_bytes = None
                if st.session_state.tts_enabled:
                    # Character Voice Accent Mapping
                    tld_mapping = {
                        "F.R.I.D.A.Y.": "ie",    # Irish accent mapping
                        "J.A.R.V.I.S.": "co.uk", # British accent mapping
                        "E.D.I.T.H.": "com",     # American accent mapping
                        "BOTH": "co.uk"
                    }
                    tld_val = tld_mapping.get(st.session_state.ai_persona, "com")
                    
                    tts = gTTS(text=ai_response, lang='en', tld=tld_val)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    audio_bytes = fp.read()

            except Exception as e:
                ai_response = f"Neural transmission error encountered, Sir: `{str(e)}`"
                audio_bytes = None
                
        st.session_state.chat_history.append({"user": active_query, "bot": ai_response, "audio": audio_bytes})
        st.session_state.processing_query = None
        st.rerun()

    if not st.session_state.chat_history:
        st.markdown(f"<div class='stark-card'><em>Awaiting query inputs, Sir. gemini-3.5-flash-lite core online.</em></div>", unsafe_allow_html=True)
    else:
        for chat in reversed(st.session_state.chat_history):
            with st.chat_message("user", avatar="👤"):
                st.write(chat["user"])
            with st.chat_message("assistant", avatar="🟠"):
                st.write(chat["bot"])
                if chat.get("audio") and st.session_state.tts_enabled:
                    st.audio(chat["audio"], format="audio/mp3")

# 6. BOTTOM CONTROL PANEL
st.write("---")
st.markdown("<h3 class='cyber-title' style='font-size: 16px;'>⚙️ BOTTOM PROTOCOL DECK & ARCHIVE VAULT</h3>", unsafe_allow_html=True)

bottom_col1, bottom_col2, bottom_col3, bottom_col4, bottom_col5 = st.columns(5, gap="medium")

with bottom_col1:
    protocols = ["F.R.I.D.A.Y.", "J.A.R.V.I.S.", "E.D.I.T.H.", "BOTH"]
    current_index = protocols.index(st.session_state.ai_persona) if st.session_state.ai_persona in protocols else 0
    selected_persona = st.selectbox("Active AI Protocol Selector", protocols, index=current_index)
    if selected_persona != st.session_state.ai_persona:
        st.session_state.ai_persona = selected_persona
        if selected_persona == "E.D.I.T.H.":
            st.session_state.build_version = "EDITH-v1"
        st.toast(f"Protocol shifted to {selected_persona}, Sir. Theme and voice profiles updated.")
        st.rerun()

with bottom_col2:
    build_options = ["v3.5-lite", "EDITH-v1"]
    current_b_idx = build_options.index(st.session_state.build_version) if st.session_state.build_version in build_options else 0
    selected_build = st.selectbox("Operational Engine", build_options, index=current_b_idx)
    if selected_build != st.session_state.build_version:
        st.session_state.build_version = selected_build
        st.rerun()

with bottom_col3:
    tts_toggle = st.checkbox("Audio Voice Feedback (TTS)", value=st.session_state.tts_enabled)
    if tts_toggle != st.session_state.tts_enabled:
        st.session_state.tts_enabled = tts_toggle
        st.rerun()

with bottom_col4:
    st.write("")
    if st.button("⚡ Boost Mainframe Power", use_container_width=True):
        st.toast("Arc Reactor output surged by 400%, Sir! gemini-3.5-flash-lite throughput optimized.")

with bottom_col5:
    st.write("")
    if st.button("Flush Cache Matrices", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.processing_query = None
        st.toast("Active variable stack cleared, Sir.")
        st.rerun()
