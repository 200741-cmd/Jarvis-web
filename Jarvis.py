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
        "history": []
    }

st.session_state.chat_history = st.session_state.all_chats[st.session_state.session_id]["history"]

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
    ]
if "generated_blueprint_report" not in st.session_state:
    st.session_state.generated_blueprint_report = None
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

# CHECK CATARACT STATE
is_cataract = (st.session_state.ai_persona == "VISION" and st.session_state.cataract_active)

# STARK GRID, CONTAINER, HOLOGRAPHIC FRAME & THANOS SNAP STYLING
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

    /* STARK CHATBAR OVERLAY */
    .stChatInputContainer {{
        border: 2px solid { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        border-radius: 12px !important;
        background: { "#FFFFFF" if is_cataract else "rgba(10, 14, 28, 0.95)" } !important;
        box-shadow: 0 0 25px rgba(255, 255, 255, 1) !important;
        padding: 4px !important;
    }}

    /* BOTTOM INFINITY GAUNTLET HUD BAR */
    .bottom-gauntlet-hud {{
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
    }}

    /* GLOWING INFINITY GEM BADGES */
    .gem-badge {{
        width: 42px;
        height: 42px;
        border-radius: 50%;
        margin: 0 auto 8px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        box-shadow: inset 0 0 8px rgba(255, 255, 255, 0.8);
    }}
    .gem-time {{ background: radial-gradient(circle, #00ff88 0%, #006622 100%); box-shadow: 0 0 15px #00ff88; border: 1px solid #00ff88; }}
    .gem-mind {{ background: radial-gradient(circle, #ffea00 0%, #998c00 100%); box-shadow: 0 0 15px #ffea00; border: 1px solid #ffea00; }}
    .gem-power {{ background: radial-gradient(circle, #cc00ff 0%, #660088 100%); box-shadow: 0 0 15px #cc00ff; border: 1px solid #cc00ff; }}
    .gem-space {{ background: radial-gradient(circle, #00bfff 0%, #004488 100%); box-shadow: 0 0 15px #00bfff; border: 1px solid #00bfff; }}
    .gem-reality {{ background: radial-gradient(circle, #ff0044 0%, #880022 100%); box-shadow: 0 0 15px #ff0044; border: 1px solid #ff0044; }}
    .gem-soul {{ background: radial-gradient(circle, #ff8800 0%, #884400 100%); box-shadow: 0 0 15px #ff8800; border: 1px solid #ff8800; }}
    .gem-snap {{ background: radial-gradient(circle, #ffd700 0%, #886600 100%); box-shadow: 0 0 18px #ffd700; border: 1px solid #ffd700; font-size: 18px; }}
</style>

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


# 4. MULTI-KEY FAILOVER ROTATION ENGINE (`API_KEY_1` to `API_KEY_4`)
def get_ordered_api_keys():
    keys = []
    for i in range(1, 5):
        k_name = f"API_KEY_{i}"
        val = st.secrets.get(k_name)
        if val and val not in keys:
            keys.append(val)
            
    for key_name in ["API_KEY", "GROQ_API_KEY"]:
        val = st.secrets.get(key_name)
        if val and val not in keys:
            keys.append(val)
            
    return keys

if "api_key_index" not in st.session_state:
    st.session_state.api_key_index = 0

def call_gemini_with_failover(contents):
    keys = get_ordered_api_keys()
    if not keys:
        return None, "🚨 Transmission error: No API keys configured in st.secrets."

    attempts = len(keys)
    for _ in range(attempts):
        current_key = keys[st.session_state.api_key_index % len(keys)]
        try:
            client = genai.Client(api_key=current_key)
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=contents,
            )
            return response.text, None
        except Exception as e:
            err_msg = str(e).lower()
            if any(term in err_msg for term in ["quota", "rate limit", "429", "exhausted", "limit", "permission"]):
                st.session_state.api_key_index = (st.session_state.api_key_index + 1) % len(keys)
                log_event(f"QUOTA REACHED: Rotating seamlessly to API Key Slot #{st.session_state.api_key_index + 1}")
                continue
            else:
                return None, f"🚨 Mainframe Refused: {str(e)}"
                
    return None, "🚨 Mainframe Critical: All configured API keys (1 through 4) have exhausted their quotas."


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
    f"<h1>⚙️ { 'WHITE VISION' if is_cataract else st.session_state.ai_persona.upper() } // DIAGNOSTICS MAINFRAME</h1>",
    unsafe_allow_html=True,
)
if is_cataract:
    st.info("👁️ PROJECT CATARACT ACTIVE: WHITE VISION PROTOCOL ENGAGED.")

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
        ["🎨 STARK BLUEPRINT ANALYZER", "🎞️ AI VIDEO SYNTHESIS"]
    )

    with feature_tab_1:
        st.markdown("#### 🎨 GOOGLE GENAI SCHEMATIC GENERATOR")
        with st.form("blueprint_form"):
            img_query = st.text_input("Enter blueprint or system query...", key="blueprint_prompt_field")
            submit_blueprint = st.form_submit_button("Synthesize via Google GenAI", use_container_width=True)

        if submit_blueprint and img_query:
            # Uses google-genai gemini-3.5-flash-lite to build a detailed tech specs report
            prompt_text = f"Act as Stark Industries F.R.I.D.A.Y. mainframe. Provide a comprehensive engineering schematic blueprint breakdown, technical data specs, and architectural components for: {img_query}"
            report_text, err = call_gemini_with_failover(prompt_text)
            if report_text:
                st.session_state.generated_blueprint_report = report_text
                log_event(f"GENAI SCHEMATIC: Generated specs for '{img_query}'")
            else:
                st.error(err)

        if st.session_state.generated_blueprint_report:
            st.info("📋 **Stark Technical Blueprint Specifications**")
            st.write(st.session_state.generated_blueprint_report)

    with feature_tab_2:
        st.markdown("#### 🎞️ TEXT-TO-VIDEO GENERATOR")
        with st.form("video_form"):
            ai_video_query = st.text_input("Describe animation sequence...", key="video_prompt_field")
            submit_video = st.form_submit_button("Synthesize AI Video Loop", use_container_width=True)

        if submit_video and ai_video_query:
            encoded_prompt = urllib.parse.quote(ai_video_query)
            st.session_state.active_ai_video_url = f"https://gen.pollinations.ai/video/{encoded_prompt}"
            log_event(f"AI VIDEO: Synthesized animation sequence for '{ai_video_query}'")

        if st.session_state.active_ai_video_url:
            try:
                st.video(st.session_state.active_ai_video_url, format="video/mp4")
            except Exception:
                st.error("⚠️ Video generation processing error.")

    st.markdown("---")
    protocols = ["VISION", "ULTRON", "F.R.I.D.A.Y.", "E.D.I.T.H.", "BOTH"]
    current_index = protocols.index(st.session_state.ai_persona) if st.session_state.ai_persona in protocols else 0
    selected_persona = st.selectbox("Active Protocol", protocols, index=current_index)
    if selected_persona != st.session_state.ai_persona:
        st.session_state.ai_persona = selected_persona
        st.session_state.cataract_active = False
        log_event(f"Protocol shifted to {selected_persona}.")
        st.rerun()

    tts_toggle = st.checkbox("Audio Voice Feedback (TTS)", value=st.session_state.tts_enabled)
    if tts_toggle != st.session_state.tts_enabled:
        st.session_state.tts_enabled = tts_toggle
        st.rerun()

# --- RIGHT COLUMN: COMM-LINK & CHAT INTERFACE ---
with col_right:
    st.markdown("#### 📡 SECURE COMM-LINK")

    if not st.session_state.chat_history and not st.session_state.show_time_log:
        st.info(f"Good day. {st.session_state.ai_persona} operational. Universal Session ID: `{st.session_state.session_id}`. Type `~~` to summon the Infinity Gauntlet.")

    # TIME STONE CHAT LOG PANEL
    if st.session_state.show_time_log:
        st.markdown(
            """
            <div class="time-stone-vault">
                <h4 style="color: #00FF66; margin-top: 0;">🟢 TIME STONE CHAT LOG ARCHIVE</h4>
                <p style="font-size: 11px; color: #aaa;">Temporal review of past communication sequences.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("❌ Close Time Log", key="close_time_log"):
            st.session_state.show_time_log = False
            st.rerun()

        for chat in reversed(st.session_state.chat_history):
            with st.chat_message("user", avatar="👤"):
                st.write(chat["user"])
            with st.chat_message("assistant", avatar="🟡"):
                st.write(chat["bot"])
                if chat.get("audio") and st.session_state.tts_enabled:
                    st.audio(chat["audio"], format="audio/mp3")

    # RENDER CHAT HISTORY NORMALLY
    for chat in reversed(st.session_state.chat_history):
        with st.chat_message("user", avatar="👤"):
            st.write(chat["user"])
        with st.chat_message("assistant", avatar="🟡"):
            st.write(chat["bot"])
            if chat.get("audio") and st.session_state.tts_enabled:
                st.audio(chat["audio"], format="audio/mp3")

    # NATIVE STREAMLIT CHAT INPUT
    active_query = st.chat_input("💬 Transmit command to mainframe (Type ~~ for Gauntlet)...")

    if active_query:
        if "cataract" in active_query.lower() and st.session_state.ai_persona == "VISION":
            st.session_state.cataract_active = not st.session_state.cataract_active
            log_event("OPACIFICATION: Cataract whiteout layer toggled in Vision mode.")
            st.rerun()
        elif active_query.strip() == "~~":
            st.session_state.show_gauntlet = not st.session_state.show_gauntlet
            log_event("REALITY: Infinity Stones portal toggled via '~~'.")
            st.rerun()
        else:
            st.session_state.processing_query = active_query

            with st.chat_message("user", avatar="👤"):
                st.write(active_query)

            if len(st.session_state.chat_history) == 0:
                st.session_state.all_chats[st.session_state.session_id]["title"] = active_query[:25] + "..."

            # INSTANT TEXT GENERATION VIA GEMINI 3.5 FLASH LITE WITH MULTI-KEY FAILOVER
            ai_reply, err = call_gemini_with_failover(active_query)

            if err:
                ai_reply = err

            with st.chat_message("assistant", avatar="🟡"):
                st.write(ai_reply)

            # SAVE HISTORY INSTANTLY
            st.session_state.chat_history.append({
                "user": active_query,
                "bot": ai_reply,
                "audio": None,
            })
            st.session_state.processing_query = None
            st.rerun()

    # --- BOTTOM SCREEN: INFINITY GAUNTLET HUD BAR ---
    if st.session_state.show_gauntlet:
        st.markdown(
            """
            <div class="bottom-gauntlet-hud">
                <h4 style="color: #FFD700; margin: 0 0 10px 0; font-size: 14px;">🥊 INFINITY GAUNTLET HUD BAR (Summoned via '~~')</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        stone_cols = st.columns(7)

        with stone_cols[0]:
            st.markdown('<div class="gem-badge gem-time">💎</div>', unsafe_allow_html=True)
            if st.button("Time", key="time_stone"):
                st.session_state.show_time_log = not st.session_state.show_time_log
                st.session_state.stone_status = "🟢 TIME STONE: Toggled chronological chat logs view."
                st.rerun()

        with stone_cols[1]:
            st.markdown('<div class="gem-badge gem-mind">💎</div>', unsafe_allow_html=True)
            if st.button("Mind", key="mind_stone"):
                st.session_state.stone_status = f"🟡 MIND STONE: Active persona is {st.session_state.ai_persona}"

        with stone_cols[2]:
            st.markdown('<div class="gem-badge gem-power">💎</div>', unsafe_allow_html=True)
            if st.button("Power", key="power_stone"):
                st.session_state.stone_status = f"🟣 POWER STONE: CPU Load at {psutil.cpu_percent()}%"

        with stone_cols[3]:
            st.markdown('<div class="gem-badge gem-space">💎</div>', unsafe_allow_html=True)
            if st.button("Space", key="space_stone"):
                st.session_state.stone_status = f"🔵 SPACE STONE: Session `{st.session_state.session_id}`"

        with stone_cols[4]:
            st.markdown('<div class="gem-badge gem-reality">💎</div>', unsafe_allow_html=True)
            if st.button("Reality", key="reality_stone"):
                st.session_state.stone_status = "🔴 REALITY STONE: Matrix styling warped."

        with stone_cols[5]:
            st.markdown('<div class="gem-badge gem-soul">💎</div>', unsafe_allow_html=True)
            if st.button("Soul", key="soul_stone"):
                st.session_state.stone_status = "🟠 SOUL STONE: Core synchronized."

        with stone_cols[6]:
            st.markdown('<div class="gem-badge gem-snap">🫰</div>', unsafe_allow_html=True)
            if st.button("SNAP", key="snap_btn"):
                st.markdown(
                    "<script>triggerGoogleThanosSnap();</script>",
                    unsafe_allow_html=True
                )
                st.session_state.chat_history = []
                log_event("REALITY: Thanos snap executed from Bottom HUD.")
                st.toast("⚡ Half of all chat data dissolved into cosmic dust.", icon="🌌")
                time.sleep(1.8)
                st.rerun()

        st.caption(st.session_state.stone_status)
