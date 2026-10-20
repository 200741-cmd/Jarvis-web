import io
import time
import urllib.parse
import datetime
import psutil
import speech_recognition as sr
import streamlit as st
import wikipedia
import json
from google import genai
from google.genai import types
from gtts import gTTS

# 1. PAGE CONFIG
st.set_page_config(
    page_title="VISION // Diagnostics Mainframe",
    page_icon="🟡",
    layout="wide",
)

# 2. SESSION STATE & UNIVERSAL STORAGE SETUP
if "session_id" not in st.session_state:
    query_params = st.query_params
    if "chat_id" in query_params:
        st.session_state.session_id = query_params["chat_id"]
    else:
        st.session_state.session_id = f"session_{int(time.time())}"
        st.query_params["chat_id"] = st.session_state.session_id

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if st.session_state.session_id not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.session_id] = {
        "title": f"Chat {time.strftime('%H:%M:%S')}",
        "history": []
    }

st.session_state.chat_history = st.session_state.all_chats[st.session_state.session_id]["history"]

if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "VISION"
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = True
if "processing_query" not in st.session_state:
    st.session_state.processing_query = None
if "system_logs" not in st.session_state:
    st.session_state.system_logs = [
        "Mainframe online.",
        "Universal Database Synchronized.",
    ]
if "generated_blueprint" not in st.session_state:
    st.session_state.generated_blueprint = None
if "active_ai_video_url" not in st.session_state:
    st.session_state.active_ai_video_url = None
if "active_ai_video_label" not in st.session_state:
    st.session_state.active_ai_video_label = "Awaiting Synthesis Command"
if "stone_status" not in st.session_state:
    st.session_state.stone_status = "All 6 Infinity Stones active in Gauntlet"

# 3. DYNAMIC THEME ENGINE MAPPING
theme_palettes = {
    "VISION": {"primary": "#8E24AA", "bg": "#0B0410", "rgb": "142, 36, 170"},
    "ULTRON": {"primary": "#FF0000", "bg": "#120000", "rgb": "255, 0, 0"},
    "F.R.I.D.A.Y.": {"primary": "#FF9900", "bg": "#120B04", "rgb": "255, 153, 0"},
    "E.D.I.T.H.": {"primary": "#FF3333", "bg": "#120404", "rgb": "255, 51, 51"},
    "BOTH": {"primary": "#BF00FF", "bg": "#0D0412", "rgb": "191, 0, 255"},
}

active_theme = theme_palettes.get(
    st.session_state.ai_persona, theme_palettes["VISION"]
)

# STARK GRID, CONTAINER & GOOGLE THANOS SNAP PARTICLE STYLING
st.markdown(
    f"""
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

    /* GOOGLE KNOWLEDGE PANEL STYLE FOR INFINITY GAUNTLET */
    .gauntlet-card {{
        border: 1px solid #FFD700;
        border-radius: 12px;
        background: radial-gradient(circle, rgba(40, 30, 10, 0.9) 0%, rgba(10, 5, 0, 0.95) 100%);
        padding: 15px;
        text-align: center;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.25);
        margin-bottom: 20px;
    }}

    .stone-btn {{
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        padding: 0 !important;
        font-size: 18px !important;
        margin: 2px !important;
        box-shadow: 0 0 12px currentColor;
    }}
</style>

<!-- GOOGLE THANOS SNAP DISINTEGRATION SCRIPT -->
<script>
    function triggerGoogleThanosSnap() {{
        const elements = document.querySelectorAll('.stChatMessage, div[data-testid="column"]');
        elements.forEach((el, index) => {{
            setTimeout(() => {{
                el.style.transition = "all 2s cubic-bezier(0.25, 1, 0.5, 1)";
                el.style.transform = "translate(40px, -30px) scale(0.3) rotate(20deg)";
                el.style.filter = "blur(16px) brightness(4) sepia(1)";
                el.style.opacity = "0";
            }}, index * 150);
        }});
    }}
</script>
""",
    unsafe_allow_html=True,
)


# 4. SECURE CLIENT INITIALIZATION
@st.cache_resource
def get_genai_client():
    api_key = None
    try:
        api_key = (
            st.secrets.get("API_KEY", "")
            or st.secrets.get("API_KEY_1", "")
            or st.secrets.get("GROQ_API_KEY", "")
        )
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


# 5. SIDEBAR: UNIVERSAL CHAT VAULT
st.sidebar.markdown("### 🌐 UNIVERSAL CHAT VAULT")
if st.sidebar.button("➕ New Universal Session", use_container_width=True):
    new_id = f"session_{int(time.time())}"
    st.session_state.all_chats[new_id] = {
        "title": f"Chat {time.strftime('%H:%M:%S')}",
        "history": []
    }
    st.query_params["chat_id"] = new_id
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📁 Universal Archives")
for s_id, s_data in list(st.session_state.all_chats.items()):
    col_s1, col_s2 = st.sidebar.columns([3, 1])
    with col_s1:
        if st.button(s_data["title"], key=f"nav_{s_id}", use_container_width=True):
            st.query_params["chat_id"] = s_id
            st.rerun()
    with col_s2:
        if st.button("🗑️", key=f"del_{s_id}"):
            del st.session_state.all_chats[s_id]
            if st.session_state.session_id == s_id:
                remaining = list(st.session_state.all_chats.keys())
                if remaining:
                    st.query_params["chat_id"] = remaining[0]
                else:
                    new_id = f"session_{int(time.time())}"
                    st.session_state.all_chats[new_id] = {"title": "Main Chat", "history": []}
                    st.query_params["chat_id"] = new_id
            st.rerun()


# 6. HEADER
st.markdown(
    f"<h1>⚙️ {st.session_state.ai_persona.upper()} // DIAGNOSTICS MAINFRAME</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<hr style='border: 0.5px solid rgba({active_theme['rgb']}, 0.3); margin-bottom: 25px;'>",
    unsafe_allow_html=True,
)

# 7. MASTER TWO-COLUMN LAYOUT
col_left, col_right = st.columns([1, 1.5], gap="large")

# --- LEFT COLUMN: TELEMETRY, BLUEPRINTS & AI VIDEO ---
with col_left:
    st.markdown("#### 🎛️ CORE TELEMETRY")

    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent

    st.markdown(
        "<span style='font-size: 12px; color: #888;'>ARMOR / CORE INTEGRITY</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<h2>100%</h2>", unsafe_allow_html=True)

    st.markdown(f"⚡ **CPU LOAD:** {cpu}%")
    st.progress(min(1.0, cpu / 100.0))

    st.markdown(f"🔋 **VRAM ALLOCATED:** {ram}%")
    st.progress(min(1.0, ram / 100.0))

    st.markdown("---")

    # FEATURE TABS
    feature_tab_1, feature_tab_2 = st.tabs(
        ["🎨 STARK BLUEPRINTS", "🎞️ AI VIDEO SYNTHESIS"]
    )

    with feature_tab_1:
        st.markdown("#### 🎨 STARK IMAGE MAKER")
        img_query = st.text_input("Blueprint description...", key="blueprint_input")
        if st.button("Synthesize Blueprint", use_container_width=True):
            
