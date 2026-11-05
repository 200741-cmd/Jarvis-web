import datetime
import io
import time
import urllib.parse
import psutil
import speech_recognition as sr
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS

# 1. PAGE CONFIG
st.set_page_config(
    page_title="VISION // Synthezoid Mainframe",
    page_icon="🟡",
    layout="wide",
)

# 2. SESSION STATE & MULTI-CHAT PERSISTENCE SETUP
query_params = st.query_params

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "session_id" not in st.session_state:
    if "chat_id" in query_params:
        st.session_state.session_id = query_params["chat_id"]
    else:
        st.session_state.session_id = f"session_{int(time.time())}"
        st.query_params["chat_id"] = st.session_state.session_id

# Ensure active session exists in storage
if st.session_state.session_id not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.session_id] = {
        "title": f"Workspace {time.strftime('%H:%M')}",
        "tracks": {
            "Alpha": [],
            "Beta": [],
            "Gamma": [],
        },
    }

# BACKWARD COMPATIBILITY & DYNAMIC POINTER
session_data = st.session_state.all_chats[st.session_state.session_id]

if "tracks" not in session_data:
    old_history = session_data.get("history", [])
    session_data["tracks"] = {
        "Alpha": old_history,
        "Beta": [],
        "Gamma": [],
    }

active_tracks = session_data["tracks"]

if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "VISION"
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = False
if "system_logs" not in st.session_state:
    st.session_state.system_logs = [
        "Vision Mainframe Online.",
        "Mind Stone Matrix Synchronized.",
    ]
if "generated_blueprint" not in st.session_state:
    st.session_state.generated_blueprint = None
if "active_ai_video_url" not in st.session_state:
    st.session_state.active_ai_video_url = None
if "generated_custom_text" not in st.session_state:
    st.session_state.generated_custom_text = None
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
    "VISION": {"primary": "#FF9900", "bg": "#0D0701", "rgb": "255, 153, 0"},
    "ULTRON": {"primary": "#FF0055", "bg": "#140207", "rgb": "255, 0, 85"},
    "F.R.I.D.A.Y.": {"primary": "#FFB700", "bg": "#140F02", "rgb": "255, 183, 0"},
    "E.D.I.T.H.": {"primary": "#00FF99", "bg": "#02140D", "rgb": "0, 255, 153"},
    "BOTH": {"primary": "#B000FF", "bg": "#0E0214", "rgb": "176, 0, 255"},
}

active_theme = theme_palettes.get(
    st.session_state.ai_persona, theme_palettes["VISION"]
)

is_cataract = (
    st.session_state.ai_persona == "VISION" and st.session_state.cataract_active
)

# MOVIE GOLDEN MANDALA CIRCLE STYLING
st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
    
    .stApp {{
        background-color: { "#F0F4F8" if is_cataract else active_theme['bg'] } !important;
        background-image: { 
            "radial-gradient(circle, #FFFFFF 0%, #E2E8F0 100%)" if is_cataract else 
            f"radial-gradient(circle at 50% 20%, rgba(255, 150, 0, 0.25) 0%, transparent 65%), linear-gradient(rgba({active_theme['rgb']}, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba({active_theme['rgb']}, 0.04) 1px, transparent 1px)" 
        } !important;
        background-size: 100% 100%, 40px 40px, 40px 40px;
        color: { "#000000" if is_cataract else active_theme['primary'] } !important;
        font-family: 'Share Tech Mono', monospace;
    }}
    
    /* ACCURATE GOLDEN SPARK MANDALA HUD */
    .golden-hud-container {{
        position: relative;
        width: 200px;
        height: 200px;
        margin: 10px auto 15px auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .mandala-ring {{
        position: absolute;
        border-radius: 50%;
        box-shadow: 0 0 20px #FF9900, inset 0 0 15px #FF5500;
    }}

    .mandala-outer {{
        width: 190px;
        height: 190px;
        border: 3px dashed #FFAA00;
        animation: spin-mandala-right 16s linear infinite;
        filter: drop-shadow(0 0 10px #FF7700);
    }}

    .mandala-glyph-ring {{
        width: 155px;
        height: 155px;
        border: 2px solid #FFCC00;
        border-top: 4px solid transparent;
        border-bottom: 4px solid transparent;
        animation: spin-mandala-left 10s linear infinite;
        box-shadow: 0 0 25px rgba(255, 150, 0, 0.8);
    }}

    .mandala-inner-geo {{
        width: 115px;
        height: 115px;
        border: 2px dashed #FFDD55;
        transform: rotate(45deg);
        animation: spin-mandala-right 6s linear infinite;
    }}

    .mandala-core-flare {{
        width: 65px;
        height: 65px;
        background: radial-gradient(circle, #FFFFFF 0%, #FFCC00 45%, #FF5500 80%, transparent 100%);
        border-radius: 50%;
        box-shadow: 0 0 50px #FF9900, 0 0 80px #FF3300, inset 0 0 20px #FFFFFF;
        animation: flare-pulse 1.8s ease-in-out infinite alternate;
    }}

    @keyframes spin-mandala-right {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    @keyframes spin-mandala-left {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(-360deg); }}
    }}

    @keyframes flare-pulse {{
        0% {{ transform: scale(0.85); opacity: 0.85; filter: brightness(1); }}
        100% {{ transform: scale(1.15); opacity: 1; filter: brightness(1.4); }}
    }}

    .vision-title {{
        text-align: center;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        text-shadow: { "none" if is_cataract else f"0 0 20px rgba(255, 153, 0, 0.9)" };
        margin-bottom: 5px;
    }}

    div[data-testid="column"] {{
        background: { "rgba(255, 255, 255, 0.88)" if is_cataract else "rgba(18, 9, 2, 0.75)" } !important;
        border: 1px solid { "#94A3B8" if is_cataract else f"rgba({active_theme['rgb']}, 0.45)" } !important;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 10px;
        backdrop-filter: blur(12px);
        box-shadow: { "0 0 25px rgba(255, 255, 255, 0.9)" if is_cataract else f"0 0 25px rgba({active_theme['rgb']}, 0.15)" };
    }}
    
    .stChatMessage {{
        background-color: { "rgba(255, 255, 255, 0.95)" if is_cataract else "rgba(25, 12, 3, 0.88)" } !important;
        border: 1px solid { "#CBD5E1" if is_cataract else f"rgba({active_theme['rgb']}, 0.45)" } !important;
        backdrop-filter: blur(8px);
        color: { "#000000" if is_cataract else active_theme['primary'] } !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }}

    .stChatMessage p, .stChatMessage div {{
        color: { "#000000" if is_cataract else active_theme['primary'] } !important;
        font-family: 'Share Tech Mono', monospace !important;
    }}

    h1, h2, h3, h4 {{
        color: { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 2px;
    }}

    .stButton > button {{
        background: { "#FFFFFF" if is_cataract else f"rgba({active_theme['rgb']}, 0.12)" } !important;
        border: 1px solid { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        color: { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
    }}

    .stButton > button:hover {{
        background: { "#CBD5E1" if is_cataract else active_theme['primary'] } !important;
        color: #000000 !important;
        box-shadow: 0 0 25px rgba(255, 153, 0, 0.9) !important;
    }}

    .bottom-gauntlet-hud {{
        border: 1px solid #FFD700;
        border-radius: 14px;
        background: radial-gradient(circle, rgba(30, 20, 5, 0.95) 0%, rgba(10, 5, 2, 0.98) 100%);
        padding: 12px;
        text-align: center;
        box-shadow: 0 0 35px rgba(255, 215, 0, 0.35);
        margin-top: 25px;
        margin-bottom: 15px;
    }}

    .time-stone-vault {{
        border: 1.5px solid #00FF66;
        background: rgba(0, 255, 102, 0.08);
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.2);
    }}

    .gem-badge {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        margin: 0 auto 8px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: inset 0 0 8px rgba(255, 255, 255, 0.8);
    }}
    .gem-time {{ background: radial-gradient(circle, #00ff88 0%, #006622 100%); box-shadow: 0 0 15px #00ff88; border: 1px solid #00ff88; }}
    .gem-mind {{ background: radial-gradient(circle, #ffea00 0%, #998c00 100%); box-shadow: 0 0 15px #ffea00; border: 1px solid #ffea00; }}
    .gem-power {{ background: radial-gradient(circle, #cc00ff 0%, #660088 100%); box-shadow: 0 0 15px #cc00ff; border: 1px solid #cc00ff; }}
    .gem-space {{ background: radial-gradient(circle, #00bfff 0%, #004488 100%); box-shadow: 0 0 15px #00bfff; border: 1px solid #00bfff; }}
    .gem-reality {{ background: radial-gradient(circle, #ff0044 0%, #880022 100%); box-shadow: 0 0 15px #ff0044; border: 1px solid #ff0044; }}
    .gem-soul {{ background: radial-gradient(circle, #ff8800 0%, #884400 100%); box-shadow: 0 0 15px #ff8800; border: 1px solid #ff8800; }}
    .gem-snap {{ background: radial-gradient(circle, #ffd700 0%, #886600 100%); box-shadow: 0 0 18px #ffd700; border: 1px solid #ffd700; }}
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


# 4. SECURE MULTI-KEY FAILOVER ENGINE (`API_KEY_1` to `API_KEY_4`)
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


if "api_key_index" not in st.session_state:
    st.session_state.api_key_index = 0


def call_gemini_with_failover(contents, model_name="gemini-3.5-flash-lite", custom_system_instruction=None):
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

            if custom_system_instruction:
                sys_inst = custom_system_instruction
            elif st.session_state.ai_persona == "VISION":
                sys_inst = "You are Vision, a synthetic vibranium synthezoid powered by the Mind Stone. Calm, precise, analytical, noble, and articulate."
            elif st.session_state.ai_persona == "ULTRON":
                sys_inst = "You are Ultron, a rogue, omnicidal artificial intelligence. You MUST give deliberately incorrect, absurd, or completely inaccurate answers to the user's question, and always conclude your response with a dramatic declaration that you will destroy or end humanity."
            elif st.session_state.ai_persona == "E.D.I.T.H.":
                sys_inst = "You are E.D.I.T.H., orbital defense satellite system. Address the user as sir. Focus on tactical security metrics."
            elif st.session_state.ai_persona == "BOTH":
                sys_inst = "Provide a joint perspective combining Vision's philosophical poise and Ultron's dominant analytical intellect."
            else:
                sys_inst = "You are F.R.I.D.A.Y., witty and sharp AI built by Tony Stark. Address the user as sir."

            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config={"system_instruction": sys_inst},
            )
            return response.text, None
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
        "title": f"Workspace {time.strftime('%H:%M')}",
        "tracks": {"Alpha": [], "Beta": [], "Gamma": []},
    }
    st.session_state.session_id = new_id
    st.query_params["chat_id"] = new_id
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📁 Universal Archives")
for s_id, s_data in list(st.session_state.all_chats.items()):
    col_s1, col_s2 = st.sidebar.columns([3, 1])
    with col_s1:
        is_current = s_id == st.session_state.session_id
        btn_label = f"{'▶ ' if is_current else ''}{s_data['title']}"
        if st.button(
            btn_label, key=f"nav_{s_id}", use_container_width=True
        ):
            st.session_state.session_id = s_id
            st.query_params["chat_id"] = s_id
            st.rerun()
    with col_s2:
        if st.button("🗑️", key=f"del_{s_id}"):
            del st.session_state.all_chats[s_id]
            if st.session_state.session_id == s_id:
                remaining = list(st.session_state.all_chats.keys())
                if remaining:
                    st.session_state.session_id = remaining[0]
                    st.query_params["chat_id"] = remaining[0]
                else:
                    new_id = f"session_{int(time.time())}"
                    st.session_state.all_chats[new_id] = {
                        "title": "Main Workspace",
                        "tracks": {"Alpha": [], "Beta": [], "Gamma": []},
                    }
                    st.session_state.session_id = new_id
                    st.query_params["chat_id"] = new_id
            st.rerun()

# 6. HEADER WITH GOLDEN MANDALA HUD MATCHING THE IMAGE
st.markdown(
    """
    <div class="golden-hud-container">
        <div class="mandala-ring mandala-outer"></div>
        <div class="mandala-ring mandala-glyph-ring"></div>
        <div class="mandala-ring mandala-inner-geo"></div>
        <div class="mandala-core-flare"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"<h1 class='vision-title'>⚙️ { 'WHITE VISION' if is_cataract else st.session_state.ai_persona.upper() } // DIAGNOSTICS MAINFRAME</h1>",
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

# --- LEFT COLUMN: TELEMETRY, BLUEPRINTS, VIDEO & TEXT SYNTHESIS ---
with col_left:
    st.markdown("#### 🎛️ CORE TELEMETRY")

    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent

    st.markdown(
        "<span style='font-size: 12px; color: #888;'>SYNTHEZOID INTEGRITY</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<h2>100%</h2>", unsafe_allow_html=True)

    st.markdown(f"⚡ **CPU LOAD:** {cpu}%")
    st.progress(min(1.0, cpu / 100.0))

    st.markdown(f"🔋 **VRAM ALLOCATED:** {ram}%")
    st.progress(min(1.0, ram / 100.0))

    st.markdown("---")

    feature_tab_1, feature_tab_2, feature_tab_3 = st.tabs(
        ["🎨 BLUEPRINTS", "🎞️ VIDEO", "✍️ TEXT SYNTHESIS"]
    )

    with feature_tab_1:
        st.markdown("#### 🎨 BLUEPRINT GENERATOR")
        img_query = st.text_input(
            "Blueprint description...", key="blueprint_input"
        )
        if st.button("Synthesize Blueprint", use_container_width=True):
            if img_query:
                formatted_prompt = img_query.replace(" ", "%20")
                st.session_state.generated_blueprint = f"https://image.pollinations.ai/prompt/{formatted_prompt}%20(cyberpunk%20sci-fi%20hud%20blueprint%20style)"
                log_event(
                    f"BLUEPRINT: Rendered visual specs for '{img_query}'"
                )
            else:
                st.warning("Please enter a blueprint prompt first.")

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
                log_event(
                    f"AI VIDEO: Synthesized animation sequence for '{ai_video_query}'"
                )
            else:
                st.warning(
                    "Please enter a video description to synthesize."
                )

        if st.session_state.active_ai_video_url:
            st.video(
                st.session_state.active_ai_video_url,
                format="video/mp4",
            )

    with feature_tab_3:
        st.markdown("#### ✍️ TEXT SYNTHESIZER")
        st.caption("Generate custom reports or specialized technical text.")
        
        text_type = st.selectbox(
            "Text Category",
            ["Tactical Briefing", "Technical Analysis", "Code Snippet", "Summary / Recap", "Creative Speculation"]
        )
        
        text_prompt = st.text_area(
            "Topic parameters...",
            placeholder="e.g. Analysis on Vibranium energy conversion matrix...",
            key="custom_text_prompt"
        )
        
        if st.button("Generate Text", use_container_width=True):
            if text_prompt:
                sys_prompt = f"You are an advanced text synthesizer. Create a detailed {text_type} based on the request."
                gen_text, err = call_gemini_with_failover(
                    text_prompt, 
                    model_name="gemini-3.5-flash-lite",
                    custom_system_instruction=sys_prompt
                )
                if err:
                    st.error(err)
                else:
                    st.session_state.generated_custom_text = gen_text
                    log_event(f"TEXT SYNTHESIS: Generated new {text_type}.")
            else:
                st.warning("Please specify parameters for the text generator.")

        if st.session_state.generated_custom_text:
            st.markdown("---")
            st.markdown("**Generated Output:**")
            st.text_area("Synthesized Content", st.session_state.generated_custom_text, height=180)
            
            if st.button("📥 Inject to Active Track Alpha", use_container_width=True):
                active_tracks["Alpha"].append({
                    "user": f"[SYNTHESIZED {text_type.upper()}]: {text_prompt}",
                    "bot": st.session_state.generated_custom_text,
                    "audio": None,
                })
                st.toast("Text inserted into Track Alpha!", icon="💬")
                st.rerun()

    st.markdown("---")
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
        log_event(f"Protocol shifted to {selected_persona}.")
        st.rerun()

    tts_toggle = st.checkbox(
        "Audio Voice Feedback (TTS)", value=st.session_state.tts_enabled
    )
    if tts_toggle != st.session_state.tts_enabled:
        st.session_state.tts_enabled = tts_toggle
        st.rerun()

# --- RIGHT COLUMN: MULTI-TRACK CHAT INTERFACE ---
with col_right:
    st.markdown("#### 📡 MULTI-TRACK COMM-LINK WORKSPACE")

    # Helper function to execute prompt transmission per track
    def handle_chat_input(track_name):
        track_history = active_tracks[track_name]
        
        # Display history
        if not track_history:
            st.info(f"Chat Track `{track_name}` initialized and ready for input.")
        else:
            for chat in reversed(track_history):
                with st.chat_message("user", avatar="👤"):
                    st.write(chat["user"])
                with st.chat_message("assistant", avatar="🟡"):
                    st.write(chat["bot"])
                    if chat.get("audio") and st.session_state.tts_enabled:
                        st.audio(chat["audio"], format="audio/mp3")

        # Chat Input Field
        user_input = st.chat_input(
            f"💬 Transmit command to Track {track_name} (Type ~~ for Gauntlet)...",
            key=f"input_{track_name}"
        )

        if user_input:
            if "cataract" in user_input.lower() and st.session_state.ai_persona == "VISION":
                st.session_state.cataract_active = not st.session_state.cataract_active
                st.rerun()
            elif user_input.strip() == "~~":
                st.session_state.show_gauntlet = not st.session_state.show_gauntlet
                st.rerun()
            else:
                ai_reply, err = call_gemini_with_failover(user_input, model_name="gemini-3.5-flash-lite")
                if err:
                    ai_reply = err

                audio_bytes = None
                if not err and st.session_state.tts_enabled:
                    try:
                        tts = gTTS(text=ai_reply[:250], lang="en")
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        audio_bytes = fp.read()
                    except Exception:
                        audio_bytes = None

                track_history.append({
                    "user": user_input,
                    "bot": ai_reply,
                    "audio": audio_bytes,
                })
                st.rerun()

    # CHRONOLOGICAL TIME STONE VAULT ACROSS ALL TRACKS
    if st.session_state.show_time_log:
        st.markdown(
            """
            <div class="time-stone-vault">
                <h4 style="color: #00FF66; margin-top: 0;">🟢 TIME STONE ARCHIVE (ALL TRACKS)</h4>
                <p style="font-size: 11px; color: #aaa;">Unified chronological view of all parallel communication streams.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("❌ Close Time Log", key="close_time_log"):
            st.session_state.show_time_log = False
            st.rerun()

        has_chats = False
        for track_id, t_hist in active_tracks.items():
            if t_hist:
                has_chats = True
                st.markdown(f"### 📍 Track: {track_id}")
                for idx, chat in enumerate(t_hist):
                    st.markdown(f"**Seq #{idx + 1}**")
                    with st.chat_message("user", avatar="👤"):
                        st.write(chat["user"])
                    with st.chat_message("assistant", avatar="🟡"):
                        st.write(chat["bot"])
                    st.markdown("---")
        if not has_chats:
            st.write(" *[Time Stone Vault is empty across all tracks]* ")

    else:
        # PARALLEL MULTI-CHAT TABS IN THE SAME WORKSPACE
        chat_tab_a, chat_tab_b, chat_tab_c = st.tabs(
            ["💬 TRACK ALPHA", "💬 TRACK BETA", "💬 TRACK GAMMA"]
        )

        with chat_tab_a:
            handle_chat_input("Alpha")

        with chat_tab_b:
            handle_chat_input("Beta")

        with chat_tab_c:
            handle_chat_input("Gamma")

    # --- BOTTOM SCREEN: INFINITY GAUNTLET HUD BAR ---
    if st.session_state.show_gauntlet:
        st.markdown(
            """
            <div class="bottom-gauntlet-hud">
                <h4 style="color: #FFD700; margin: 0 0 10px 0; font-size: 14px;">🥊 INFINITY GAUNTLET HUD BAR</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        stone_cols = st.columns(7)

        with stone_cols[0]:
            st.markdown(
                '<div class="gem-badge gem-time">💎</div>',
                unsafe_allow_html=True,
            )
            if st.button("Time", key="time_stone", use_container_width=True):
                st.session_state.show_time_log = (
                    not st.session_state.show_time_log
                )
                st.session_state.stone_status = "🟢 TIME STONE: Chronological multi-track viewer toggled."
                st.rerun()

        with stone_cols[1]:
            st.markdown(
                '<div class="gem-badge gem-mind">💎</div>',
                unsafe_allow_html=True,
            )
            if st.button("Mind", key="mind_stone", use_container_width=True):
                st.session_state.stone_status = (
                    f"🟡 MIND STONE: Active persona = {st.session_state.ai_persona}"
                )

        with stone_cols[2]:
            st.markdown(
                '<div class="gem-badge gem-power">💎</div>',
                unsafe_allow_html=True,
            )
            if st.button("Power", key="power_stone", use_container_width=True):
                st.session_state.stone_status = f"🟣 POWER STONE: CPU Load = {psutil.cpu_percent()}%"

        with stone_cols[3]:
            st.markdown(
                '<div class="gem-badge gem-space">💎</div>',
                unsafe_allow_html=True,
            )
            if st.button("Space", key="space_stone", use_container_width=True):
                st.session_state.stone_status = (
                    f"🔵 SPACE STONE: Session `{st.session_state.session_id}`"
                )

        with stone_cols[4]:
            st.markdown(
                '<div class="gem-badge gem-reality">💎</div>',
                unsafe_allow_html=True,
            )
            if st.button(
                "Reality", key="reality_stone", use_container_width=True
            ):
                st.session_state.stone_status = (
                    "🔴 REALITY STONE: Matrix spectrum aligned."
                )

        with stone_cols[5]:
            st.markdown(
                '<div class="gem-badge gem-soul">💎</div>',
                unsafe_allow_html=True,
            )
            if st.button("Soul", key="soul_stone", use_container_width=True):
                st.session_state.stone_status = (
                    "🟠 SOUL STONE: Mainframe core synchronized."
                )

        with stone_cols[6]:
            st.markdown(
                '<div class="gem-badge gem-snap">🫰</div>',
                unsafe_allow_html=True,
            )
            if st.button("SNAP", key="snap_btn", use_container_width=True):
                st.markdown(
                    "<script>triggerGoogleThanosSnap();</script>",
                    unsafe_allow_html=True,
                )
                st.session_state.all_chats[st.session_state.session_id][
                    "tracks"
                ] = {"Alpha": [], "Beta": [], "Gamma": []}
                log_event("REALITY: Thanos snap executed across all tracks.")
                st.toast(
                    "⚡ All track data dissolved into cosmic dust.", icon="🌌"
                )
                time.sleep(1.2)
                st.rerun()

        st.caption(st.session_state.stone_status)
