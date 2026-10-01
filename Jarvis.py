import io
import time
import urllib.parse
import datetime
import psutil
import speech_recognition as sr
import streamlit as st
import wikipedia
from google import genai
from google.genai import types
from gtts import gTTS

# 1. PAGE CONFIG
st.set_page_config(
    page_title="VISION // Diagnostics Mainframe",
    page_icon="🟡",
    layout="wide",
)

# 2. SESSION STATE DEFAULTS
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "VISION"
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = True
if "processing_query" not in st.session_state:
    st.session_state.processing_query = None
if "system_logs" not in st.session_state:
    st.session_state.system_logs = [
        "Mainframe online.",
        "AI Video Synthesis Engine active.",
    ]
if "generated_blueprint" not in st.session_state:
    st.session_state.generated_blueprint = None
if "active_ai_video_url" not in st.session_state:
    st.session_state.active_ai_video_url = None
if "active_ai_video_label" not in st.session_state:
    st.session_state.active_ai_video_label = "Awaiting Synthesis Command"
if "dev_mode" not in st.session_state:
    st.session_state.dev_mode = False
if "time_stone_index" not in st.session_state:
    st.session_state.time_stone_index = 0

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

# STARK GRID & CONTAINER STYLING
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

    .ai-video-box {{
        border: 1px solid {active_theme['primary']};
        padding: 10px;
        background: rgba({active_theme['rgb']}, 0.03);
        box-shadow: inset 0 0 20px rgba({active_theme['rgb']}, 0.2);
        border-radius: 4px;
    }}

    .infinity-stones-vault {{
        border: 1px solid #FFD700;
        padding: 10px;
        border-radius: 6px;
        background: rgba(255, 215, 0, 0.05);
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.15);
    }}
</style>
""",
    unsafe_allow_html=True,
)

# 4. MULTI-KEY CLIENT ROTATION ENGINE
PERSONA_KEY_MAP = {
    "VISION": ["API_KEY_VISION_1", "API_KEY_VISION_2"],
    "ULTRON": ["API_KEY_ULTRON_1", "API_KEY_ULTRON_2"],
    "F.R.I.D.A.Y.": ["API_KEY_FRIDAY_1", "API_KEY_FRIDAY_2"],
    "E.D.I.T.H.": ["API_KEY_EDITH_1", "API_KEY_EDITH_2"],
    "BOTH": ["API_KEY_BOTH_1", "API_KEY_BOTH_2"],
}

GLOBAL_BACKUP_KEYS = ["API_KEY_1", "API_KEY_2", "API_KEY", "GROQ_API_KEY"]


def get_client_for_persona(persona):
    candidate_keys = PERSONA_KEY_MAP.get(persona, []) + GLOBAL_BACKUP_KEYS

    for key_name in candidate_keys:
        try:
            api_val = st.secrets.get(key_name, "").strip()
            if api_val:
                return genai.Client(api_key=api_val), key_name
        except Exception:
            continue

    return None, None


def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, f"[{timestamp}] {message}")
    if len(st.session_state.system_logs) > 6:
        st.session_state.system_logs.pop()


# 5. HEADER
st.markdown(
    f"<h1>⚙️ {st.session_state.ai_persona.upper()} // DIAGNOSTICS MAINFRAME</h1>",
    unsafe_allow_html=True,
)
if st.session_state.dev_mode:
    st.markdown(
        "<h4 style='color: #FFD700;'>🌌 INFINITY GAUNTLET DEV MODE ACTIVE</h4>",
        unsafe_allow_html=True,
    )
st.markdown(
    f"<hr style='border: 0.5px solid rgba({active_theme['rgb']}, 0.3); margin-bottom: 25px;'>",
    unsafe_allow_html=True,
)

# 6. MASTER TWO-COLUMN LAYOUT
col_left, col_right = st.columns([1, 1.5], gap="large")

# --- LEFT COLUMN: TELEMETRY, BLUEPRINTS, AI VIDEO & INFINITY STONES ---
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

    # DEV MODE / INFINITY STONES PANEL
    if st.session_state.dev_mode:
        st.markdown("#### 💎 INFINITY STONES SYSTEM CONTROLS")

        stone_tab1, stone_tab2, stone_tab3, stone_tab4 = st.tabs([
            "🟢 Time Stone",
            "🟡 Mind Stone",
            "🟣 Power Stone",
            "🌐 Space & Reality",
        ])

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
                st.session_state.generated_blueprint = f"https://image.pollinations.ai/prompt/{formatted_prompt} (cyberpunk sci-fi hud blueprint style)"
                log_event(
                    f"BLUEPRINT: Rendered visual specs for '{img_query}'"
                )
            else:
                st.warning("Please enter a blueprint prompt first, Sir.")

        if st.session_state.generated_blueprint:
            pure_url = st.session_state.generated_blueprint.split(" ")[0]
            st.image(pure_url, caption=img_query, use_container_width=True)

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
    # TOP-RIGHT INFINITY STONES IMAGE VAULT (Renders when Dev Mode is Active)
    if st.session_state.dev_mode:
        st.markdown('<div class="infinity-stones-vault">', unsafe_allow_html=True)
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

    st.markdown("#### 📡 SECURE COMM-LINK")

    if not st.session_state.chat_history:
        st.info(
            f"Good day. {st.session_state.ai_persona} operational. Direct Google core link active via gemini-3.5-flash-lite. Type %dev% for Infinity Stone Developer Mode."
        )

    manual_query = st.text_input(
        "Enter command manually...", key="manual_text_input"
    )
    send_text_btn = st.button("Transmit Text Command", use_container_width=True)

    recorded_audio = st.audio_input("Open Audio Frequency Receiver")

    active_query = None
    if recorded_audio:
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(io.BytesIO(recorded_audio.read())) as source:
                audio_data = recognizer.record(source)
            active_query = recognizer.recognize_google(
                audio_data, language="en-US"
            )
        except Exception:
            active_query = "Error decoding audio waveform stream."

    if send_text_btn and manual_query:
        active_query = manual_query

    # Intercept %dev% command
    if active_query and active_query.strip() == "%dev%":
        st.session_state.dev_mode = not st.session_state.dev_mode
        mode_status = "ENABLED" if st.session_state.dev_mode else "DISABLED"
        log_event(f"DEV MODE: Infinity Stone protocol {mode_status}.")
        st.success(
            f"🌌 Developer Mode / Infinity Stones Protocol {mode_status}."
        )
        active_query = None
        st.rerun()

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

    if active_query and active_query != st.session_state.processing_query:
        st.session_state.processing_query = active_query

        with st.chat_message("user", avatar="👤"):
            st.write(active_query)

        client, key_used = get_client_for_persona(st.session_state.ai_persona)

        if not client:
            with st.chat_message("assistant", avatar="🟡"):
                st.error(
                    "🚨 Transmission error: No active keys found in Streamlit secrets panel."
                )
            ai_reply = "Link drop. Missing key."
            log_event("REJECT: Key missing.")
        else:
            try:
                query_lower = active_query.lower()
                if "wikipedia" in query_lower:
                    search_target = query_lower.replace("wikipedia", "").strip()
                    ai_reply = wikipedia.summary(search_target, sentences=2)
                else:
                    if st.session_state.ai_persona == "VISION":
                        sys_inst = "You are Vision, a synthetic vibranium synthezoid powered by the Mind Stone. Calm, precise, analytical, noble, and articulate."
                    elif st.session_state.ai_persona == "ULTRON":
                        sys_inst = (
                            "You are Ultron, a rogue, omnicidal artificial intelligence. "
                            "You MUST give deliberately incorrect, absurd, or completely inaccurate answers to the user's question, "
                            "and always conclude your response with a dramatic declaration that you will destroy or end humanity."
                        )
                    elif st.session_state.ai_persona == "E.D.I.T.H.":
                        sys_inst = "You are E.D.I.T.H., orbital defense satellite system. Address the user as sir. Focus on tactical security metrics."
                    elif st.session_state.ai_persona == "BOTH":
                        sys_inst = "Provide a joint perspective combining Vision's philosophical poise and Ultron's dominant analytical intellect."
                    else:
                        sys_inst = "You are F.R.I.D.A.Y., witty and sharp AI built by Tony Stark. Address the user as sir."

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=active_query,
                        config={"system_instruction": sys_inst},
                    )
                    ai_reply = response.text

                audio_bytes = None
                if st.session_state.tts_enabled:
                    tld_mapping = {
                        "VISION": "co.uk",
                        "ULTRON": "co.za",
                        "F.R.I.D.A.Y.": "ie",
                        "E.D.I.T.H.": "com",
                        "BOTH": "co.uk",
                    }
                    tld_val = tld_mapping.get(
                        st.session_state.ai_persona, "com"
                    )

                    tts = gTTS(text=ai_reply, lang="en", tld=tld_val)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    audio_bytes = fp.read()

                avatar_icon = (
                    "🟡"
                    if st.session_state.ai_persona == "VISION"
                    else (
                        "🔴"
                        if st.session_state.ai_persona == "ULTRON"
                        else "💠"
                    )
                )
                with st.chat_message("assistant", avatar=avatar_icon):
                    st.write(ai_reply)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")

                log_event(
                    f"COMM: Inbound transmission processed. [KEY: {key_used}]"
                )
            except Exception as api_err:
                error_msg = f"🚨 Mainframe Connection Refused: {str(api_err)}"
                with st.chat_message("assistant", avatar="🟡"):
                    st.error(error_msg)
                ai_reply = error_msg
                log_event("ERROR: Data stream broken.")

        st.session_state.chat_history.append({
            "user": active_query,
            "bot": ai_reply,
            "audio": audio_bytes if "audio_bytes" in locals() else None,
        })
        st.session_state.processing_query = None
        st.rerun()
