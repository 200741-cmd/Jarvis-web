import speech_recognition as sr
import streamlit as st
import wikipedia
import json
from google import genai
from google.genai import types
from gtts import gTTS
@@ -18,49 +17,30 @@
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

# 2. SESSION STATE DEFAULTS
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "VISION"
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = False
    st.session_state.tts_enabled = True
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
@@ -75,145 +55,96 @@
    st.session_state.ai_persona, theme_palettes["VISION"]
)

# CHECK CATARACT STATE
is_cataract = (st.session_state.ai_persona == "VISION" and st.session_state.cataract_active)

# STARK GRID, CONTAINER & THANOS SNAP STYLING
# STARK GRID & CONTAINER STYLING
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
        background-color: {active_theme['bg']};
        background-image: 
            linear-gradient(rgba({active_theme['rgb']}, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba({active_theme['rgb']}, 0.04) 1px, transparent 1px);
        background-size: 30px 30px;
        color: { "#000000" if is_cataract else active_theme['primary'] } !important;
        color: {active_theme['primary']};
        font-family: 'Courier New', Courier, monospace;
    }}
    
    div[data-testid="column"] {{
        background: { "rgba(255, 255, 255, 0.88)" if is_cataract else "rgba(6, 9, 19, 0.75)" } !important;
        border: 1.5px solid { "#94A3B8" if is_cataract else f"rgba({active_theme['rgb']}, 0.3)" } !important;
        border-radius: 8px;
        background: rgba(6, 9, 19, 0.75) !important;
        border: 1px solid rgba({active_theme['rgb']}, 0.3) !important;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 10px;
        backdrop-filter: blur(8px);
        box-shadow: { "0 0 25px rgba(255, 255, 255, 0.9)" if is_cataract else f"0 0 20px rgba({active_theme['rgb']}, 0.08)" };
        backdrop-filter: blur(4px);
        box-shadow: 0 0 15px rgba({active_theme['rgb']}, 0.05);
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
        background-color: rgba(6, 9, 19, 0.85) !important;
        border: 1px solid rgba({active_theme['rgb']}, 0.25) !important;
        backdrop-filter: blur(4px);
        color: {active_theme['primary']} !important;
        border-radius: 6px !important;
    }}

    h1, h2, h3, h4 {{
        color: { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        color: {active_theme['primary']} !important;
        font-family: 'Courier New', Courier, monospace !important;
        letter-spacing: 1px;
    }}

    .stButton > button, div[data-testid="stForm"] button {{
        background: { "#FFFFFF" if is_cataract else "rgba(6, 9, 19, 0.9)" } !important;
        border: 1.5px solid { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        color: { "#0F172A" if is_cataract else active_theme['primary'] } !important;
    .stButton > button {{
        background: rgba(6, 9, 19, 0.9) !important;
        border: 1px solid {active_theme['primary']} !important;
        color: {active_theme['primary']} !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border-radius: 4px !important;
    }}

    /* STARK CHATBAR OVERLAY */
    .stChatInputContainer {{
        border: 2px solid { "#0F172A" if is_cataract else active_theme['primary'] } !important;
        border-radius: 12px !important;
        background: { "#FFFFFF" if is_cataract else "rgba(10, 14, 28, 0.95)" } !important;
        box-shadow: 0 0 25px rgba(255, 255, 255, 1) !important;
        padding: 4px !important;
    .ai-video-box {{
        border: 1px solid {active_theme['primary']};
        padding: 10px;
        background: rgba({active_theme['rgb']}, 0.03);
        box-shadow: inset 0 0 20px rgba({active_theme['rgb']}, 0.2);
        border-radius: 4px;
    }}

    /* BOTTOM INFINITY GAUNTLET HUD BAR */
    .bottom-gauntlet-hud {{
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
        padding: 10px;
        border-radius: 6px;
        background: rgba(255, 215, 0, 0.05);
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.15);
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
# 4. SECURE MULTI-KEY FAILOVER CLIENT INITIALIZATION (`API_KEY_1` to `API_KEY_4`)
def get_ordered_api_keys():
    keys = []
    for i in range(1, 5):
        k_name = f"API_KEY_{i}"
        val = st.secrets.get(k_name)
        if val and val not in keys:
            keys.append(val)
        try:
            val = st.secrets.get(k_name)
            if val and str(val).strip() and str(val).strip() not in keys:
                keys.append(str(val).strip())
        except Exception:
            pass

    for key_name in ["API_KEY", "GROQ_API_KEY"]:
        val = st.secrets.get(key_name)
        if val and val not in keys:
            keys.append(val)
    for key_name in ["API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY"]:
        try:
            val = st.secrets.get(key_name)
            if val and str(val).strip() and str(val).strip() not in keys:
                keys.append(str(val).strip())
        except Exception:
            pass

    return keys

@@ -223,11 +154,12 @@ def get_ordered_api_keys():
def call_gemini_with_failover(contents, config=None, model_name="gemini-3.5-flash-lite"):
    keys = get_ordered_api_keys()
    if not keys:
        return None, "🚨 Transmission error: No API keys configured in st.secrets."
        return None, "🚨 Transmission error: No active keys found in the Streamlit secrets panel."

    attempts = len(keys)
    for _ in range(attempts):
        current_key = keys[st.session_state.api_key_index % len(keys)]
        current_index = st.session_state.api_key_index % len(keys)
        current_key = keys[current_index]
        try:
            client = genai.Client(api_key=current_key)
            response = client.models.generate_content(
@@ -238,14 +170,14 @@ def call_gemini_with_failover(contents, config=None, model_name="gemini-3.5-flas
            return response, None
        except Exception as e:
            err_msg = str(e).lower()
            if any(term in err_msg for term in ["quota", "rate limit", "429", "exhausted", "limit", "permission"]):
                st.session_state.api_key_index = (st.session_state.api_key_index + 1) % len(keys)
                log_event(f"QUOTA REACHED: Rotating seamlessly to API Key Slot #{st.session_state.api_key_index + 1}")
            if any(term in err_msg for term in ["quota", "rate limit", "429", "exhausted", "limit", "permission", "resource_exhausted"]):
                st.session_state.api_key_index = (current_index + 1) % len(keys)
                log_event(f"QUOTA REACHED on Key Slot #{current_index + 1}. Rotating to Key Slot #{st.session_state.api_key_index + 1}")
                continue
            else:
                return None, f"🚨 Mainframe Refused: {str(e)}"

    return None, "🚨 Mainframe Critical: All configured API keys (1 through 4) have exhausted their quotas."
    return None, "🚨 Mainframe Critical: All configured API keys (1 through 4) have exhausted their quotas or returned errors."


def log_event(message):
@@ -255,56 +187,25 @@ def log_event(message):
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
# 5. HEADER
st.markdown(
    f"<h1>⚙️ { 'WHITE VISION' if is_cataract else st.session_state.ai_persona.upper() } // DIAGNOSTICS MAINFRAME</h1>",
    f"<h1>⚙️ {st.session_state.ai_persona.upper()} // DIAGNOSTICS MAINFRAME</h1>",
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
# 6. MASTER TWO-COLUMN LAYOUT
col_left, col_right = st.columns([1, 1.5], gap="large")

# --- LEFT COLUMN: TELEMETRY, BLUEPRINTS & AI VIDEO ---
# --- LEFT COLUMN: TELEMETRY, BLUEPRINTS, AI VIDEO & INFINITY STONES ---
with col_left:
    st.markdown("#### 🎛️ CORE TELEMETRY")

@@ -325,212 +226,341 @@ def log_event(message):

    st.markdown("---")

    # FEATURE TABS
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
        ["🎨 GENAI NATIVE BLUEPRINT", "🎞️ AI VIDEO LOG"]
        ["🎨 STARK BLUEPRINTS", "🎞️ AI VIDEO SYNTHESIS"]
    )

    with feature_tab_1:
        st.markdown("#### 🎨 GOOGLE GENAI IMAGE GENERATOR")
        with st.form("blueprint_form"):
            img_query = st.text_input("Blueprint description...", key="blueprint_prompt_field")
            submit_blueprint = st.form_submit_button("Synthesize via GenAI", use_container_width=True)

        if submit_blueprint and img_query:
            with st.spinner("Synthesizing native asset through Gemini image modality..."):
                # Use Google GenAI native image generation config response modality
                config = types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="1:1")
                )
                response, err = call_gemini_with_failover(
                    contents=f"High-tech cyberpunk sci-fi HUD blueprint schematic asset for: {img_query}",
                    config=config,
                    model_name="gemini-3.1-flash-lite-image"
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
                
                if err:
                    st.error(err)
                else:
                    found_image = False
                    if response and hasattr(response, 'parts'):
                        for part in response.parts:
                            if getattr(part, 'inline_data', None):
                                st.session_state.generated_blueprint_bytes = part.inline_data.data
                                found_image = True
                                break
                    if not found_image and response and hasattr(response, 'candidates'):
                        try:
                            for candidate in response.candidates:
                                for part in candidate.content.parts:
                                    if getattr(part, 'inline_data', None):
                                        st.session_state.generated_blueprint_bytes = part.inline_data.data
                                        found_image = True
                                        break
                        except Exception:
                            pass
                            
                    if found_image:
                        log_event(f"GENAI IMAGE: Rendered specs for '{img_query}'")
                    else:
                        st.error("⚠️ Mainframe returned content without an image attachment.")

        if st.session_state.generated_blueprint_bytes:
            st.image(st.session_state.generated_blueprint_bytes, use_container_width=True)
            else:
                st.warning("Please enter a blueprint prompt first, Sir.")

        if st.session_state.generated_blueprint:
            pure_url = st.session_state.generated_blueprint.split(" ")[0]
            st.image(pure_url, caption=img_query, use_container_width=True)

    with feature_tab_2:
        st.markdown("#### 🎞️ TEXT-TO-VIDEO GENERATOR")
        with st.form("video_form"):
            ai_video_query = st.text_input("Describe animation sequence...", key="video_prompt_field")
            submit_video = st.form_submit_button("Synthesize AI Video Loop", use_container_width=True)

        if submit_video and ai_video_query:
            st.info("ℹ️ Video animation stream ready.")
            log_event(f"AI VIDEO: Processed animation sequence for '{ai_video_query}'")
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
    current_index = protocols.index(st.session_state.ai_persona) if st.session_state.ai_persona in protocols else 0
    selected_persona = st.selectbox("Active Protocol", protocols, index=current_index)
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
        log_event(
            f"Protocol shifted to {selected_persona}. Theme re-calibrated."
        )
        st.rerun()

    tts_toggle = st.checkbox("Audio Voice Feedback (TTS)", value=st.session_state.tts_enabled)
    tts_toggle = st.checkbox(
        "Audio Voice Feedback (TTS)", value=st.session_state.tts_enabled
    )
    if tts_toggle != st.session_state.tts_enabled:
        st.session_state.tts_enabled = tts_toggle
        st.rerun()

# --- RIGHT COLUMN: COMM-LINK & CHAT INTERFACE ---
    if st.button("♻️ Optimize Cache", use_container_width=True):
        st.session_state.chat_history = []
        log_event("CLEAN: Memory buffers flushed.")
        st.rerun()

# --- RIGHT COLUMN: SECURE COMM-LINK & TOP-RIGHT INFINITY STONES VAULT ---
with col_right:
    st.markdown("#### 📡 SECURE COMM-LINK")
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

    if not st.session_state.chat_history and not st.session_state.show_time_log:
        st.info(f"Good day. {st.session_state.ai_persona} operational. Universal Session ID: `{st.session_state.session_id}`. Type `~~` to summon the Infinity Gauntlet.")
    st.markdown("#### 📡 SECURE COMM-LINK")

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
    if not st.session_state.chat_history:
        st.info(
            f"Good day. {st.session_state.ai_persona} operational. Direct Google core link active via gemini-3.5-flash-lite. Type %dev% for Infinity Stone Developer Mode."
        )
        if st.button("❌ Close Time Log", key="close_time_log"):
            st.session_state.show_time_log = False
            st.rerun()

        for chat in reversed(st.session_state.chat_history):
            with st.chat_message("user", avatar="👤"):
                st.write(chat["user"])
            with st.chat_message("assistant", avatar="🟡"):
                st.write(chat["bot"])
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

    # RENDER CHAT HISTORY NORMALLY
    for chat in reversed(st.session_state.chat_history):
        with st.chat_message("user", avatar="👤"):
            st.write(chat["user"])
        with st.chat_message("assistant", avatar="🟡"):
        avatar_icon = (
            "🟡"
            if st.session_state.ai_persona == "VISION"
            else ("🔴" if st.session_state.ai_persona == "ULTRON" else "💠")
        )
        with st.chat_message("assistant", avatar=avatar_icon):
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
            response, err = call_gemini_with_failover(active_query, model_name="gemini-3.5-flash-lite")
            ai_reply = response.text if response and hasattr(response, 'text') else (err or "🚨 Mainframe Error.")

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
    if active_query and active_query != st.session_state.processing_query:
        st.session_state.processing_query = active_query

        stone_cols = st.columns(7)
        with st.chat_message("user", avatar="👤"):
            st.write(active_query)

        query_lower = active_query.lower()
        if "wikipedia" in query_lower:
            search_target = query_lower.replace("wikipedia", "").strip()
            ai_reply = wikipedia.summary(search_target, sentences=2)
            audio_bytes = None
            if st.session_state.tts_enabled:
                tld_mapping = {
                    "VISION": "co.uk",
                    "ULTRON": "co.za",
                    "F.R.I.D.A.Y.": "ie",
                    "E.D.I.T.H.": "com",
                    "BOTH": "co.uk",
                }
                tld_val = tld_mapping.get(st.session_state.ai_persona, "com")
                tts = gTTS(text=ai_reply, lang="en", tld=tld_val)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                audio_bytes = fp.read()
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

        with stone_cols[0]:
            st.markdown('<div class="gem-badge gem-time">💎</div>', unsafe_allow_html=True)
            if st.button("Time", key="time_stone"):
                st.session_state.show_time_log = not st.session_state.show_time_log
                st.session_state.stone_status = "🟢 TIME STONE: Toggled chronological chat logs view."
                st.rerun()
            response_obj, err = call_gemini_with_failover(
                contents=active_query,
                config={"system_instruction": sys_inst},
                model_name="gemini-3.5-flash-lite"
            )

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
            if err:
                ai_reply = err
            else:
                ai_reply = response_obj.text if response_obj and hasattr(response_obj, 'text') else "🚨 Mainframe response empty."

            audio_bytes = None
            if not err and st.session_state.tts_enabled:
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
                st.session_state.chat_history = []
                log_event("REALITY: Thanos snap executed from Bottom HUD.")
                st.toast("⚡ Half of all chat data dissolved into cosmic dust.", icon="🌌")
                time.sleep(1.8)
                st.rerun()

        st.caption(st.session_state.stone_status)
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

        log_event("COMM: Inbound transmission processed.")

        st.session_state.chat_history.append({
            "user": active_query,
            "bot": ai_reply,
            "audio": audio_bytes if "audio_bytes" in locals() else None,
        })
        st.session_state.processing_query = None
        st.rerun()
