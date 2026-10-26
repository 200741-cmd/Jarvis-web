import io
import json
import time
import urllib.parse
import google.genai as genai
from google.genai import types
import psutil
import speech_recognition as sr
import streamlit as st

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Stark Diagnostics Mainframe",
    page_icon="⚙️",
    layout="wide",
)

# Initialize API Key Index for Rotation
if "api_key_index" not in st.session_state:
    st.session_state.api_key_index = 0

# 2. SESSION STATE & UNIVERSAL PERSISTENCE SETUP
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
        "history": [],
    }

st.session_state.chat_history = st.session_state.all_chats[
    st.session_state.session_id
]["history"]

# Session State Defaults
if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "VISION"
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = False
if "processing_query" not in st.session_state:
    st.session_state.processing_query = None
if "system_logs" not in st.session_state:
    st.session_state.system_logs = [
        "Mainframe online.",
        "Universal Database Synchronized.",
        "AI Video Synthesis Engine active.",
    ]
if "generated_blueprint_bytes" not in st.session_state:
    st.session_state.generated_blueprint_bytes = None
if "generated_blueprint" not in st.session_state:
    st.session_state.generated_blueprint = None
if "active_ai_video_url" not in st.session_state:
    st.session_state.active_ai_video_url = None
if "stone_status" not in st.session_state:
    st.session_state.stone_status = "All 6 Infinity Stones active"
if "show_gauntlet" not in st.session_state:
    st.session_state.show_gauntlet = False
if "show_time_log" not in st.session_state:
    st.session_state.show_time_log = False
if "cataract_active" not in st.session_state:
    st.session_state.cataract_active = False
if "active_ai_video_label" not in st.session_state:
    st.session_state.active_ai_video_label = "Awaiting Synthesis Command"
if "dev_mode" not in st.session_state:
    st.session_state.dev_mode = False
if "time_stone_index" not in st.session_state:
    st.session_state.time_stone_index = 0

# 3. DYNAMIC THEME ENGINE MAPPING
theme_palettes = {
    "VISION": {"bg": "#0A0E1A", "primary": "#00E5FF", "rgb": "0, 229, 255"},
    "ULTRON": {"bg": "#1A0A0A", "primary": "#FF0033", "rgb": "255, 0, 51"},
    "F.R.I.D.A.Y.": {"bg": "#0A1A14", "primary": "#00FF66", "rgb": "0, 255, 102"},
    "E.D.I.T.H.": {"bg": "#110A1A", "primary": "#BF00FF", "rgb": "191, 0, 255"},
    "BOTH": {"bg": "#1A1A0A", "primary": "#FFD700", "rgb": "255, 215, 0"},
}

active_theme = theme_palettes.get(
    st.session_state.ai_persona, theme_palettes["VISION"]
)

# Check Cataract State
is_cataract = (
    st.session_state.ai_persona == "VISION" and st.session_state.cataract_active
)

# STARK GRID, CONTAINER & STYLING
st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+New:wght@400;700&display=swap');
    
    .stApp {{
        background-color: { "#F0F4F8" if is_cataract else active_theme['bg'] } !important;
        background-image: { 
            "radial-gradient(circle, #FFFFFF 0%, #E2E8F0 100%)" if is_cataract else 
            f"linear-gradient(rgba({active_theme['rgb']}, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba({active_theme['rgb']}, 0.04) 1px, transparent 1px)" 
        } !important;
        background-size: 30px 30px;
        color: { "#000000" if is_cataract else active_theme['primary'] } !important;
        font-family: 'Courier New', Courier, monospace;
    }}
    
    div[data-testid="column"] {{
        background: { "rgba(255, 255, 255, 0.88)" if is_cataract else "rgba(6, 9, 19, 0.75)" } !important;
        border: 1.5px solid { "#94A3B8" if is_cataract else f"rgba({active_theme['rgb']}, 0.3)" } !important;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        backdrop-filter: blur(8px);
        box-shadow: { "0 0 25px rgba(255, 255, 255, 0.9)" if is_cataract else f"0 0 20px rgba({active_theme['rgb']}, 0.08)" };
    }}
    
    .stChatMessage {{
        background-color: { "rgba(255, 255, 255, 0.95)" if is_cataract else "rgba(6, 9, 19, 0.9)" } !important;
        border: 1px solid { "#CBD5E1" if is_cataract else f"rgba({active_theme['rgb']}, 0.35)" } !important;
        backdrop-filter: blur(6px);
        color: { "#000000" if is_cataract else active_theme['primary'] } !important;
        border-radius: 8px !important;
    }}

    .stChatMessage p, .stChatMessage div {{
        color: { "#000000" if is_cataract else active_theme['primary'] } !important;
        font-weight: { "bold" if is_cataract else "normal" };
    }}

    h1, h2, h3, h4 {{
        color: { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        font-family: 'Courier New', Courier, monospace !important;
        letter-spacing: 1px;
    }}

    .stButton > button, div[data-testid="stForm"] button {{
        background: { "#FFFFFF" if is_cataract else "rgba(6, 9, 19, 0.9)" } !important;
        border: 1.5px solid { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        color: { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-weight: bold !important;
        border-radius: 6px !important;
    }}

    .ai-video-box {{
        border: 1px solid {active_theme['primary']};
        padding: 10px;
        background: rgba({active_theme['rgb']}, 0.03);
        box-shadow: inset 0 0 20px rgba({active_theme['rgb']}, 0.2);
        border-radius: 4px;
    }}

    .infinity-stones-vault {{
        border: 1px solid #FFD700;
        border-radius: 12px;
        background: radial-gradient(circle, rgba(30, 20, 5, 0.95) 0%, rgba(10, 5, 2, 0.98) 100%);
        padding: 12px;
        text-align: center;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.35);
        margin-top: 25px;
        margin-bottom: 15px;
    }}

    .time-stone-vault {{
        border: 1px solid #00FF66;
        background: rgba(0, 255, 102, 0.05);
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.15);
    }}
</style>
""",
    unsafe_allow_html=True,
)


def log_event(message):
    st.session_state.system_logs.insert(
        0, f"[{time.strftime('%H:%M:%S')}] {message}"
    )
    if len(st.session_state.system_logs) > 20:
        st.session_state.system_logs.pop()


# 4. SECURE MULTI-KEY FAILOVER INITIALIZATION
def get_ordered_api_keys():
    keys = []
    for i in range(1, 5):
        k_name = f"API_KEY_{i}"
        try:
            val = st.secrets.get(k_name)
            if val and str(val).strip() and str(val).strip() not in keys:
                keys.append(str(val).strip())
        except Exception:
            pass

    for key_name in ["API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY"]:
        try:
            val = st.secrets.get(key_name)
            if val and str(val).strip() and str(val).strip() not in keys:
                keys.append(str(val).strip())
        except Exception:
            pass

    return keys


def call_gemini_with_failover(
    contents, config=None, model_name="gemini-2.5-flash"
):
    keys = get_ordered_api_keys()
    if not keys:
        return (
            None,
            "🚨 Transmission error: No active keys found in Streamlit secrets panel.",
        )

    attempts = len(keys)
    for _ in range(attempts):
        current_index = st.session_state.api_key_index % len(keys)
        current_key = keys[current_index]
        try:
            client = genai.Client(api_key=current_key)
            response = client.models.generate_content(
                model=model_name, contents=contents, config=config
            )
            return response, None
        except Exception as e:
            err_msg = str(e).lower()
            if any(
                term in err_msg
                for term in [
                    "quota",
                    "rate limit",
                    "429",
                    "exhausted",
                    "limit",
                    "permission",
                    "resource_exhausted",
                ]
            ):
                st.session_state.api_key_index = (current_index + 1) % len(keys)
                log_event(
                    f"QUOTA REACHED on Key Slot #{current_index + 1}. Rotating to Key Slot #{st.session_state.api_key_index + 1}"
                )
                continue
            else:
                return None, f"🚨 Mainframe Refused: {str(e)}"

    return (
        None,
        "🚨 Mainframe Critical: All configured API keys have exhausted their quotas or returned errors.",
    )


# 5. SIDEBAR: UNIVERSAL CHAT VAULT
st.sidebar.markdown("### 🌐 UNIVERSAL CHAT VAULT")
if st.sidebar.button("➕ New Universal Session", use_container_width=True):
    new_id = f"session_{int(time.time())}"
    st.session_state.all_chats[new_id] = {
        "title": f"Chat {time.strftime('%H:%M:%S')}",
        "history": [],
    }
    st.query_params["chat_id"] = new_id
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📁 Universal Archives")
for s_id, s_data in list(st.session_state.all_chats.items()):
    col_s1, col_s2 = st.sidebar.columns([3, 1])
    with col_s1:
        if st.button(
            s_data["title"], key=f"nav_{s_id}", use_container_width=True
        ):
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
                    st.session_state.all_chats[new_id] = {
                        "title": "Main Chat",
                        "history": [],
                    }
                    st.query_params["chat_id"] = new_id
            st.rerun()

# 6. HEADER
st.markdown(
    f"<h1>⚙️ { 'WHITE VISION' if is_cataract else st.session_state.ai_persona.upper() } // DIAGNOSTICS MAINFRAME</h1>",
    unsafe_allow_html=True,
)
if is_cataract:
    st.info("👁️ PROJECT CATARACT ACTIVE: WHITE VISION PROTOCOL ENGAGED.")

if st.session_state.dev_mode:
    st.markdown(
        "<h4 style='color: #FFD700;'>🌌 INFINITY GAUNTLET DEV MODE ACTIVE</h4>",
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
    st.write(
        f"**System CPU:** {psutil.cpu_percent()}% | **Memory:** {psutil.virtual_memory().percent}%"
    )

    st.markdown("---")

    # DEV MODE / INFINITY STONES PANEL
    if st.session_state.dev_mode:
        st.markdown("#### 💎 INFINITY STONES SYSTEM CONTROLS")

        stone_tab1, stone_tab2, stone_tab3, stone_tab4 = st.tabs(
            [
                "🟢 Time Stone",
                "🟡 Mind Stone",
                "🟣 Power Stone",
                "🌐 Space & Reality",
            ]
        )

        with stone_tab1:
            st.markdown("##### 🟢 Time Stone (Temporal Review)")
            st.caption(
                "Rewind and view older chat history logs in chronological sequence."
            )
            if st.session_state.chat_history:
                max_idx = len(st.session_state.chat_history) - 1
                if max_idx == 0:
                    selected_time = 0
                    st.caption(
                        "📍 *Currently showing the only recorded dialogue entry.*"
                    )
                else:
                    selected_time = st.slider(
                        "Chronological Depth Index",
                        0,
                        max_idx,
                        max_idx,
                        key="time_stone_slider",
                    )
                historical_entry = st.session_state.chat_history[selected_time]
                st.info(
                    f"**Historical User Prompt [{selected_time}]:** {historical_entry['user']}"
                )
                st.success(
                    f"**Historical AI Response [{selected_time}]:** {historical_entry['bot']}"
                )
            else:
                st.write("No historical timeline data recorded yet.")

        with stone_tab2:
            st.markdown("##### 🟡 Mind Stone (Introspection)")
            st.write(f"**Active AI Persona:** {st.session_state.ai_persona}")
            st.write(
                f"**Total Dialog Cycles:** {len(st.session_state.chat_history)}"
            )
            st.write("**Recent System Logs:**")
            for log in st.session_state.system_logs[:4]:
                st.code(log)

        with stone_tab3:
            st.markdown("##### 🟣 Power Stone (Raw Diagnostics)")
            st.write(f"**Logical Cores:** {psutil.cpu_count(logical=True)}")
            st.write(f"**Physical Cores:** {psutil.cpu_count(logical=False)}")
            st.write(
                f"**Memory Usage:** {psutil.virtual_memory().used / (1024**3):.2f} GB / {psutil.virtual_memory().total / (1024**3):.2f} GB"
            )

        with stone_tab4:
            st.markdown("##### 🔵 Space & 🔴 Reality Stones")
            st.write(f"**Current Active Theme:** {st.session_state.ai_persona}")
            st.write(f"**RGB Blueprint Signature:** `{active_theme['rgb']}`")
            if st.button(
                "🌌 Purge All Timeline Anomalies", use_container_width=True
            ):
                st.session_state.chat_history = []
                log_event("REALITY: Timeline purged.")
                st.rerun()

        st.markdown("---")

    # FEATURE TABS: Blueprints vs AI Video Synthesis
    feature_tab_1, feature_tab_2 = st.tabs(
        ["🎨 STARK BLUEPRINTS", "🎞️ AI VIDEO SYNTHESIS"]
    )

    with feature_tab_1:
        st.markdown("#### 🎨 STARK IMAGE MAKER")
        img_query = st.text_input(
            "Blueprint description...", key="blueprint_input"
        )
        if st.button("Synthesize Blueprint", use_container_width=True):
            if img_query:
                formatted_prompt = img_query.replace(" ", "%20")
                st.session_state.generated_blueprint = f"https://image.pollinations.ai/prompt/{formatted_prompt}%20cyberpunk%20sci-fi%20hud%20blueprint%20style"
                log_event(
                    f"BLUEPRINT: Rendered visual specs for '{img_query}'"
                )
            else:
                st.warning("Please enter a blueprint prompt first, Sir.")

        if st.session_state.generated_blueprint:
            st.image(
                st.session_state.generated_blueprint,
                caption=img_query,
                use_container_width=True,
            )

    with feature_tab_2:
        st.markdown("#### 🎞️ TEXT-TO-VIDEO GENERATOR")
        ai_video_query = st.text_input(
            "Describe the animation sequence...", key="ai_video_text_input"
        )

        animation_presets = {
            "Arc Reactor Flow": "glowing blue energy core pulsation",
            "Global Defense Grid": "rotating digital data network matrix",
            "Nano-Tech Assembly": "molecular construction sequence simulation",
            "Flight Path HUD": "futuristic vector telemetry overlay",
        }
        selected_preset = st.selectbox(
            "Animation Styling", list(animation_presets.keys())
        )

        if st.button("Synthesize AI Video Loop", use_container_width=True):
            if ai_video_query:
                generation_prompt = f"{ai_video_query} {animation_presets[selected_preset]} motion graphic fluid sci-fi animation hd looping"
                encoded_prompt = urllib.parse.quote(generation_prompt)
                st.session_state.active_ai_video_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=640&height=360&nologo=true&seed=42"
                st.session_state.active_ai_video_label = (
                    f"AI Generated: {ai_video_query}"
                )
                log_event(
                    f"AI VIDEO: Synthesized animation sequence for '{ai_video_query}'"
                )
            else:
                st.warning(
                    "Please enter a video description to synthesize, Sir."
                )

        if st.session_state.active_ai_video_url:
            st.markdown('<div class="ai-video-box">', unsafe_allow_html=True)
            st.markdown(
                f"<span style='font-size: 11px; color: {active_theme['primary']};'>⚡ SYNTHESIS STATUS: COMPLETE // SOURCE: AI ENGINE</span>",
                unsafe_allow_html=True,
            )
            st.video(
                st.session_state.active_ai_video_url,
                format="video/mp4",
                autoplay=True,
                loop=True,
                muted=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔧 SYSTEM CONTROLS")

    protocols = ["VISION", "ULTRON", "F.R.I.D.A.Y.", "E.D.I.T.H.", "BOTH"]
    current_index = (
        protocols.index(st.session_state.ai_persona)
        if st.session_state.ai_persona in protocols
        else 0
    )
    selected_persona = st.selectbox(
        "Active Protocol", protocols, index=current_index
    )
    if selected_persona != st.session_state.ai_persona:
        st.session_state.ai_persona = selected_persona
        st.session_state.cataract_active = False
        log_event(
            f"Protocol shifted to {selected_persona}. Theme re-calibrated."
        )
        st.rerun()

    tts_toggle = st.checkbox(
        "Audio Voice Feedback (TTS)", value=st.session_state.tts_enabled
    )
    if tts_toggle != st.session_state.tts_enabled:
        st.session_state.tts_enabled = tts_toggle
        st.rerun()

    if st.button("♻️ Optimize Cache", use_container_width=True):
        st.session_state.chat_history = []
        log_event("CLEAN: Memory buffers flushed.")
        st.rerun()

# --- RIGHT COLUMN: SECURE COMM-LINK & TOP-RIGHT INFINITY STONES VAULT ---
with col_right:
    st.markdown("#### 📡 SECURE COMM-LINK")

    if st.session_state.dev_mode:
        st.markdown(
            '<div class="infinity-stones-vault">', unsafe_allow_html=True
        )
        st.markdown(
            "<span style='font-size: 12px; color: #FFD700;'>💎 TOP RIGHT HUD // INFINITY STONES MATRIX ACTIVE</span>",
            unsafe_allow_html=True,
        )
        st.image(
            "https://image.pollinations.ai/prompt/six%20glowing%20infinity%20stones%20marvel%20space%20mind%20reality%20power%20time%20soul%20futuristic%20hud%20cyberpunk%20interface?width=600&height=220&nologo=true&seed=99",
            caption="INFINITY STONES VAULT // DEV MODE SYNC",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.show_time_log:
        st.markdown(
            """
            <div class="time-stone-vault">
                <h4 style="color: #00FF66; margin-top: 0;">🟢 TIME STONE CHAT LOG ARCHIVE</h4>
                <p style="font-size: 11px; color: #aaa;">Temporal review of past communication sequences.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("❌ Close Time Log", key="close_time_log"):
            st.session_state.show_time_log = False
            st.rerun()

    if not st.session_state.chat_history:
        st.info(
            f"Good day. {st.session_state.ai_persona} operational. Direct Google core link active. Type %dev% for Infinity Stone Developer Mode."
        )

    # RENDER CHAT HISTORY
    for chat in reversed(st.session_state.chat_history):
        with st.chat_message("user", avatar="👤"):
            st.write(chat["user"])

        avatar_icon = (
            "🟡"
            if st.session_state.ai_persona == "VISION"
            else ("🔴" if st.session_state.ai_persona == "ULTRON" else "💠")
        )
        with st.chat_message("assistant", avatar=avatar_icon):
            st.write(chat["bot"])
            if chat.get("audio") and st.session_state.tts_enabled:
                st.audio(chat["audio"], format="audio/mp3")

    # STREAMLIT CHAT INPUT
    active_query = st.chat_input(
        "💬 Transmit command to mainframe (Type %dev% for Developer Mode)..."
    )

    if active_query:
        if active_query.strip() == "%dev%":
            st.session_state.dev_mode = not st.session_state.dev_mode
            mode_status = (
                "ENABLED" if st.session_state.dev_mode else "DISABLED"
            )
            log_event(f"DEV MODE: Infinity Stone protocol {mode_status}.")
            st.rerun()
        elif (
            "cataract" in active_query.lower()
            and st.session_state.ai_persona == "VISION"
        ):
            st.session_state.cataract_active = (
                not st.session_state.cataract_active
            )
            log_event(
                "OPACIFICATION: Cataract whiteout layer toggled in Vision mode."
            )
            st.rerun()
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(active_query)

            if len(st.session_state.chat_history) == 0:
                st.session_state.all_chats[st.session_state.session_id][
                    "title"
                ] = (active_query[:25] + "...")

            # GENERATE RESPONSE VIA GEMINI API WITH FAILOVER
            response, err = call_gemini_with_failover(
                active_query, model_name="gemini-2.5-flash"
            )
            ai_reply = (
                response.text
                if response and hasattr(response, "text")
                else (err or "🚨 Mainframe Error.")
            )

            avatar_icon = (
                "🟡"
                if st.session_state.ai_persona == "VISION"
                else ("🔴" if st.session_state.ai_persona == "ULTRON" else "💠")
            )
            with st.chat_message("assistant", avatar=avatar_icon):
                st.write(ai_reply)

            # SAVE TO SESSION HISTORY
            st.session_state.chat_history.append(
                {"user": active_query, "bot": ai_reply, "audio": None}
            )
            st.rerun()
