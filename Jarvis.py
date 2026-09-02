import streamlit as st
import speech_recognition as sr
import datetime
import wikipedia
import psutil
import io
import time
import random
import concurrent.futures
from google import genai
from google.genai import types
from PIL import Image
import json

# GLOBAL THREAD-SAFE COUNTER FOR KEY ROTATION
_key_counter = 0

# 2. STATE PERSISTENCE & MEMORY ENGINE
if "build_version" not in st.session_state:
    st.session_state.build_version = "v3.6"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ui_mode" not in st.session_state:
    st.session_state.ui_mode = "IDLE"
if "voice_feed" not in st.session_state:
    st.session_state.voice_feed = "AWAITING INPUT"
if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "F.R.I.D.A.Y."
if "key_cooldowns" not in st.session_state:
    st.session_state.key_cooldowns = {}  # Tracks {client_idx: expiration_timestamp}

# DYNAMIC THEME PALETTE CONFIGURATION (ENHANCED HUE)
if st.session_state.ai_persona == "F.R.I.D.A.Y.":
    bg_color = "#070402"
    text_color = "#ffc107"
    accent_color = "#ff9800"
    border_color = "#e65100"
    shadow_color = "rgba(255, 152, 0, 0.6)"
    card_bg = "linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, rgba(12, 6, 2, 0.9) 100%)"
    page_icon = "🟠"
    glow_dot = "#ff9800"
    glow_shadow = "#ff5722"
elif st.session_state.ai_persona == "J.A.R.V.I.S.":
    bg_color = "#02060b"
    text_color = "#81d4fa"
    accent_color = "#00bcd4"
    border_color = "#0097a7"
    shadow_color = "rgba(0, 188, 212, 0.6)"
    card_bg = "linear-gradient(135deg, rgba(0, 188, 212, 0.08) 0%, rgba(2, 10, 18, 0.9) 100%)"
    page_icon = "🔵"
    glow_dot = "#00bcd4"
    glow_shadow = "#00acc1"
elif st.session_state.ai_persona == "E.D.I.T.H.":
    bg_color = "#0a0203"
    text_color = "#ff8a80"
    accent_color = "#ff5252"
    border_color = "#b71c1c"
    shadow_color = "rgba(255, 82, 82, 0.7)"
    card_bg = "linear-gradient(135deg, rgba(255, 82, 82, 0.09) 0%, rgba(18, 2, 4, 0.92) 100%)"
    page_icon = "🔴"
    glow_dot = "#ff5252"
    glow_shadow = "#d32f2f"
else: # BOTH (DUAL PROTOCOL HYBRID MATRIX)
    bg_color = "#050308"
    text_color = "#e1bee7"
    accent_color = "#ab47bc"
    border_color = "#7b1fa2"
    shadow_color = "rgba(171, 71, 188, 0.6)"
    card_bg = "linear-gradient(135deg, rgba(171, 71, 188, 0.08) 0%, rgba(10, 3, 15, 0.9) 100%)"
    page_icon = "⚡"
    glow_dot = "#ab47bc"
    glow_shadow = "#8e24aa"

# 1. ADVANCED STARK TECH STYLING & HUD UI
st.set_page_config(
    page_title=f"{st.session_state.ai_persona} // Tactical OS ({st.session_state.build_version})",
    page_icon=page_icon,
    layout="wide"
)

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap');

    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Share Tech Mono', monospace;
    }}
    .cyber-title {{
        color: {accent_color};
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 15px {shadow_color}, 0 0 30px {shadow_color};
        font-weight: 900;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 0px;
    }}
    .stark-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        padding: 24px;
        border-radius: 16px;
        box-shadow: inset 0 0 20px {border_color}22, 0 0 25px {shadow_color};
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }}
    .command-console {{
        background: {card_bg};
        border: 2px solid {accent_color};
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 0 30px {shadow_color};
        margin-bottom: 20px;
    }}
    h3, h5 {{
        color: {accent_color} !important;
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1.5px;
        border-bottom: 2px solid {border_color}88;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }}
    .stProgress > div > div > div > div {{
        background-color: {accent_color} !important;
        box-shadow: 0 0 12px {accent_color};
    }}
    .stButton > button {{
        background: transparent !important;
        border: 1.5px solid {accent_color} !important;
        color: {text_color} !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 0 10px {shadow_color} !important;
        padding: 10px 16px !important;
    }}
    .stButton > button:hover {{
        background: {accent_color}33 !important;
        box-shadow: 0 0 22px {accent_color}, inset 0 0 10px {accent_color}44 !important;
        border-color: {text_color} !important;
        transform: translateY(-1px);
    }}
    /* Scrollbar Polish */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {bg_color};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {border_color};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {accent_color};
    }}
</style>
""", unsafe_allow_html=True)

# VERSION-AWARE CLIENT INITIALIZATION
@st.cache_resource
def init_active_clients(build_ver):
    if build_ver == "v3.4":
        k = st.secrets.get("API_KEY", "")
        return [genai.Client(api_key=k)] if k.strip() else []
    else:
        raw_keys = [
            st.secrets.get("API_KEY_1", ""),
            st.secrets.get("API_KEY_2", ""),
            st.secrets.get("API_KEY_3", st.secrets.get("API_KEY", "")),
            st.secrets.get("API_KEY_4", "")
        ]
        clients = []
        for k in raw_keys:
            if k.strip():
                try:
                    clients.append(genai.Client(api_key=k.strip()))
                except Exception:
                    pass
        return clients

active_clients = init_active_clients(st.session_state.build_version)
total_active_keys = len(active_clients)
active_keys_status = f"{total_active_keys} Key Bank(s) Active [{st.session_state.build_version}]" if total_active_keys > 0 else f"Offline [{st.session_state.build_version}]"

# 3. AUDIO SPEECH-TO-TEXT TRANSCRIPTION
def transcribe_audio(audio_buffer):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_buffer.read())) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data, language='en-US')
    except sr.UnknownValueError:
        return "ERROR: Acoustic waveform unreadable by tactical grid."
    except Exception as e:
        return f"ERROR: Audio transcription layer failed. ({str(e)})"

# 4. GENERATION ENGINES WITH COOLDOWN SKIPPING
def _single_generation_call(chosen_client, query_text, system_instruction):
    response = chosen_client.models.generate_content(
        model='gemini-3.6-flash',
        contents=query_text,
        config={'system_instruction': system_instruction}
    )
    return response.text

def execute_generation(query_text, system_instruction, build_version):
    global active_clients, _key_counter
    if not active_clients:
        raise Exception("All neural key banks offline. Configure your API keys in secrets, Sir.")
    
    current_time = time.time()
    
    if build_version == "v3.4":
        return _single_generation_call(active_clients[0], query_text, system_instruction)
    elif build_version == "v3.5":
        chosen_client = active_clients[_key_counter % len(active_clients)]
        _key_counter += 1
        return _single_generation_call(chosen_client, query_text, system_instruction)
    else: # v3.6 or EDITH-v1
        start_index = _key_counter % len(active_clients)
        for i in range(len(active_clients)):
            client_idx = (start_index + i) % len(active_clients)
            
            cooldown_expiry = st.session_state.key_cooldowns.get(client_idx, 0)
            if current_time < cooldown_expiry:
                continue
                
            chosen_client = active_clients[client_idx]
            _key_counter += 1
            
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_single_generation_call, chosen_client, query_text, system_instruction)
                    result_text = future.result(timeout=60)
                    
                if i > 0:
                    return f"[Failover Shifted to Key Index {client_idx + 1}] {result_text}"
                return result_text
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    st.session_state.key_cooldowns[client_idx] = time.time() + 60
                continue
                
        raise Exception("All active key banks are currently exhausted or cooling down. Please wait 60s, Sir.")

def execute_image_generation(image_prompt):
    global active_clients, _key_counter
    if not active_clients:
        raise Exception("Neural core offline. Configure your API keys in secrets, Sir.")
    
    current_time = time.time()
    start_index = _key_counter % len(active_clients)
    
    for i in range(len(active_clients)):
        client_idx = (start_index + i) % len(active_clients)
        
        cooldown_expiry = st.session_state.key_cooldowns.get(client_idx, 0)
        if current_time < cooldown_expiry:
            continue
            
        chosen_client = active_clients[client_idx]
        _key_counter += 1
        
        try:
            result = chosen_client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=image_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="1:1",
                )
            )
            for generated_image in result.generated_images:
                image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                return image
        except Exception as e:
            err_str = str(e)
            if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                st.session_state.key_cooldowns[client_idx] = time.time() + 60
            continue
            
    raise Exception("Image generation failed across all keys.")

def process_ai_logic(query_text, persona, build_version):
    query = query_text.lower().strip()
    
    if "wikipedia" in query:
        search_target = query.replace("wikipedia", "").strip()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(wikipedia.summary, search_target, 2)
                summary = future.result(timeout=15)
            return {"type": "text", "content": f"Accessing global archives, Sir... {summary}"}
        except Exception:
            return {"type": "text", "content": "Couldn't match any solid logs or archives timed out, Sir."}
            
    elif "open youtube" in query:
        return {"type": "text", "content": "Link established: [Click to launch YouTube Mainframe](https://youtube.com)"}
        
    elif "open google" in query:
        return {"type": "text", "content": "Link established: [Click to launch Google Gateway](https://google.com)"}
        
    elif "the time" in query or "time sync" in query:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return {"type": "text", "content": f"Current local time stream reads: {current_time}, Sir."}
        
    elif any(keyword in query for keyword in ["generate", "draw", "create", "image", "picture", "photo", "apple", "dalle"]):
        image_prompt = query_text if "apple" not in query else "A crisp, vibrant, perfectly polished red apple sitting on a clean wooden surface with soft cinematic studio lighting."
        try:
            image_obj = execute_image_generation(image_prompt)
            return {"type": "image", "content": image_obj, "prompt": image_prompt}
        except Exception as e:
            return {"type": "text", "content": f"Visual synthesis failed, Sir. ({str(e)})"}
            
    else:
        if active_clients:
            if build_version == "EDITH-v1" or persona == "E.D.I.T.H.":
                system_instruction = "You are E.D.I.T.H. (Even Dead I'm The Hero), the advanced orbital defense satellite intelligence system created by Tony Stark. Address the user as Sir. Focus strictly on global surveillance telemetry, tactical strike authorization, defense vectors, and threat assessment. Keep answers authoritative and sharp."
                reply_text = execute_generation(query_text, system_instruction, build_version)
                return {"type": "text", "content": f"[EDITH ORBITAL UPLINK ACTIVE] {reply_text}"}
                
            elif persona == "F.R.I.D.A.Y.":
                system_instruction = "You are F.R.I.D.A.Y., the advanced, witty, and loyal AI assistant created by Tony Stark. Address the user as Sir. Keep answers concise and sharp."
                reply_text = execute_generation(query_text, system_instruction, build_version)
                return {"type": "text", "content": reply_text}
                
            elif persona == "J.A.R.V.I.S.":
                system_instruction = "You are J.A.R.V.I.S., the highly sophisticated, impeccably polite, British-accented tactical AI assistant created by Tony Stark. Address the user as Sir. Keep answers concise, formal, and articulate."
                reply_text = execute_generation(query_text, system_instruction, build_version)
                return {"type": "text", "content": reply_text}
                
            else: # BOTH PROTOCOLS SIMULTANEOUSLY
                f_sys = "You are F.R.I.D.A.Y., witty and sharp. Address the user as Sir. Give a short take."
                j_sys = "You are J.A.R.V.I.S., polite, British, and formal. Address the user as Sir. Give a short take."
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future_f = executor.submit(execute_generation, query_text, f_sys, build_version)
                        future_j = executor.submit(execute_generation, query_text, j_sys, build_version)
                        res1 = future_f.result(timeout=60)
                        res2 = future_j.result(timeout=60)
                    
                    dual_output = f"**[F.R.I.D.A.Y.]:** {res1}\n\n**[J.A.R.V.I.S.]:** {res2}"
                    return {"type": "text", "content": dual_output}
                except Exception as e:
                    return {"type": "text", "content": f"Dual protocol neural link timeout or error: {str(e)}, Sir."}
        else:
            return {"type": "text", "content": "Neural core offline. Configure your API keys in Streamlit secrets, Sir."}

# 5. TELEMETRY HUD COMPONENT
try:
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
except Exception:
    cpu = 15.0
    ram = 40.0
core_temp = 34

engine_display_name = "EDITH ORBITAL DEFENSE" if st.session_state.build_version == "EDITH-v1" else f"{st.session_state.ai_persona} OS"
recent_logs = [f"> {engine_display_name} ONLINE ({st.session_state.build_version})", f"> GLOBAL POOL: {active_keys_status}"]
if st.session_state.build_version == "EDITH-v1":
    recent_logs.append("> SATELLITE STRIKE GRID: LOCKED")

for item in st.session_state.chat_history[-3:]:
    user_line = f"> INCOMING: {item['user'].upper()[:22]}"
    recent_logs.append(user_line)

hud_data = {
    "mode": "EDITH DEFENSE" if st.session_state.build_version == "EDITH-v1" else st.session_state.ui_mode,
    "voice": st.session_state.voice_feed,
    "cpu": int(cpu),
    "ram": int(ram),
    "temp": core_temp,
    "logs": recent_logs[-6:]
}

hud_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Share Tech Mono', monospace; }}
        body {{
            background-color: transparent;
            color: #ffffff;
            height: 380px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 10px;
            overflow: hidden;
        }}
        .grid-canvas {{ display: flex; justify-content: space-between; align-items: center; height: 100%; position: relative; }}
        .terminal-overlay {{ background: rgba(5, 10, 15, 0.88); border: 1px solid {border_color}; padding: 12px; width: 230px; font-size: 11px; color: {text_color}; opacity: 0.95; line-height: 1.6; border-radius: 8px; box-shadow: 0 0 15px {shadow_color}; }}
        .core-wrapper {{ position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center; }}
        .mode-pill {{ background: {bg_color}; border: 2px solid {accent_color}; border-radius: 20px; padding: 4px 16px; font-size: 11px; font-weight: bold; margin-bottom: -15px; box-shadow: 0 0 15px {shadow_color}; z-index: 10; color: {accent_color}; letter-spacing: 2px; }}
        .arc-rings {{ width: 150px; height: 150px; border-radius: 50%; border: 3px dashed {border_color}; display: flex; align-items: center; justify-content: center; position: relative; box-shadow: 0 0 25px {shadow_color}; }}
        .arc-rings::before {{ content: ''; position: absolute; width: 110px; height: 110px; border-radius: 50%; border: 2px dashed {accent_color}; animation: rotateCCW 10s linear infinite; }}
        .core-glow-dot {{ width: 16px; height: 16px; background-color: {glow_dot}; border-radius: 50%; box-shadow: 0 0 35px 12px {glow_shadow}; animation: pulseGlow 2s ease-in-out infinite alternate; }}
        .mini-bars-panel {{ width: 180px; display: flex; flex-direction: column; gap: 12px; font-size: 10px; font-weight: bold; color: {text_color}; background: rgba(5, 10, 15, 0.88); padding: 12px; border: 1px solid {border_color}; border-radius: 8px; box-shadow: 0 0 15px {shadow_color}; }}
        .bar-row {{ display: flex; flex-direction: column; gap: 4px; }}
        .bar-bg {{ background: {border_color}33; height: 6px; border-radius: 3px; overflow: hidden; }}
        .bar-fill {{ height: 100%; background: {accent_color}; box-shadow: 0 0 8px {accent_color}; transition: width 0.4s ease; }}
        .voice-feed-status {{ position: absolute; right: 0; bottom: 5px; text-align: right; }}
        .voice-title {{ font-size: 10px; font-weight: bold; color: rgba(255,255,255,0.6); }}
        .voice-value {{ font-size: 11px; font-weight: bold; color: {accent_color}; margin-top: 2px; text-shadow: 0 0 8px {shadow_color}; }}
        @keyframes rotateCCW {{ 100% {{ transform: rotate(-360deg); }} }}
        @keyframes pulseGlow {{ 0% {{ opacity: 0.7; transform: scale(0.95); }} 100% {{ opacity: 1; transform: scale(1.05); }} }}
    </style>
</head>
<body>
    <div class="grid-canvas">
        <div class="terminal-overlay">
            {"".join([f"{log}<br>" for log in hud_data['logs']])}
        </div>
        <div class="core-wrapper">
            <div class="mode-pill">STATUS: {hud_data['mode']}</div>
            <div class="arc-rings"><div class="core-glow-dot"></div></div>
        </div>
        <div class="mini-bars-panel">
            <div class="bar-row"><div>CPU LOAD: {hud_data['cpu']}%</div><div class="bar-bg"><div class="bar-fill" style="width: {hud_data['cpu']}%"></div></div></div>
            <div class="bar-row"><div>VRAM ALLOC: {hud_data['ram']}%</div><div class="bar-bg"><div class="bar-fill" style="width: {hud_data['ram']}%"></div></div></div>
            <div class="bar-row"><div>CORE TEMP: {hud_data['temp']}°C</div><div class="bar-bg"><div class="bar-fill" style="width: {hud_data['temp']}%"></div></div></div>
        </div>
        <div class="voice-feed-status">
            <div class="voice-title">VOICE FEED:</div>
            <div class="voice-value">{hud_data['voice']}</div>
        </div>
    </div>
</body>
</html>
"""

st.components.v1.html(hud_html, height=390)

# 6. SIDEBAR CONTROL MODULE
with st.sidebar:
    st.markdown(f"<h2 class='cyber-title' style='font-size: 18px;'>{page_icon} PROTOCOL DECK</h2>", unsafe_allow_html=True)
    st.caption(f"OS BUILD: {st.session_state.build_version}")
    st.write("---")
    
    protocols = ["F.R.I.D.A.Y.", "J.A.R.V.I.S.", "E.D.I.T.H.", "BOTH"]
    current_index = protocols.index(st.session_state.ai_persona) if st.session_state.ai_persona in protocols else 0
    selected_persona = st.radio("Active AI Protocol Selector", protocols, index=current_index)
    
    if selected_persona != st.session_state.ai_persona:
        st.session_state.ai_persona = selected_persona
        if selected_persona == "E.D.I.T.H.":
            st.session_state.build_version = "EDITH-v1"
        st.toast(f"Protocol shifted to {selected_persona}. Global key pool online, Sir.")
        st.rerun()

    st.write("")
    with st.expander("🔑 Key Bank Cooldown Matrix", expanded=True):
        @st.fragment(run_every=1)
        def render_cooldown_matrix():
            now_ts = time.time()
            if total_active_keys == 0:
                st.markdown("<span style='color: #ff5252;'>⚠️ No API Keys Discovered</span>", unsafe_allow_html=True)
            for idx in range(total_active_keys):
                expiry = st.session_state.key_cooldowns.get(idx, 0)
                if now_ts < expiry:
                    rem_sec = int(expiry - now_ts)
                    st.markdown(f"<span style='color: #ff5252; font-weight: bold;'>🔴 Key {idx + 1}: Rate Limited ({rem_sec}s)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color: #69f0ae; font-weight: bold;'>🟢 Key {idx + 1}: Ready</span>", unsafe_allow_html=True)
        render_cooldown_matrix()

    st.write("")
    with st.expander("📂 Stark Archive Vault"):
        build_options = ["v3.6", "v3.5", "v3.4", "EDITH-v1"]
        current_b_idx = build_options.index(st.session_state.build_version) if st.session_state.build_version in build_options else 0
        selected_build_label = st.selectbox("Operational Engine", [
            "v3.6 (Current - Thread-Safe)",
            "v3.5 (Multi-Key Pool Engine)",
            "v3.4 (Single-Key Legacy)",
            "EDITH-v1 (Defense Satellite Protocol)"
        ], index=current_b_idx)
        
        target_version = selected_build_label.split()[0]
        if target_version != st.session_state.build_version:
            st.session_state.build_version = target_version
            if target_version == "EDITH-v1":
                st.session_state.ai_persona = "E.D.I.T.H."
            st.toast(f"Switched active runtime engine to {target_version}, Sir!")
            st.rerun()

    st.write("")
    if st.button("⚡ Boost Mainframe Power", use_container_width=True):
        st.toast("Arc Reactor output surged by 400%, Sir! Latency optimized.")
        
    if st.button("Flush Cache Matrices", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.ui_mode = "IDLE"
        st.session_state.voice_feed = "AWAITING INPUT"
        st.toast("Active variable stack cleared, Sir.")
        st.rerun()

# 7. REORGANIZED TWO-COLUMN DASHBOARD LAYOUT
display_persona_title = "E.D.I.T.H. // SATELLITE DEFENSE MATRIX" if st.session_state.build_version == "EDITH-v1" else f"{st.session_state.ai_persona} // TACTICAL COMMAND DASHBOARD"
st.markdown(f"<h1 class='cyber-title'>{page_icon} {display_persona_title}</h1>", unsafe_allow_html=True)
st.caption(f"SECURE MAINFRAME CONNECTION ACTIVE // 60S TIMEOUT FAIL-SAFE")
st.write("---")

col_left, col_right = st.columns([1, 1.3], gap="large")

with col_left:
    st.markdown("<div class='command-console'>", unsafe_allow_html=True)
    st.subheader("🖥️ Operations Command Deck")
    
    recorded_audio = st.audio_input("Open Microscopic Frequency Receiver")
    st.write("")
    
    if st.button("🗣️ Initiate AI Inter-Comm Dialogue", use_container_width=True):
        if active_clients:
            with st.spinner("Connecting neural link..."):
                try:
                    f_sys = "You are F.R.I.D.A.Y., witty and sharp. Address J.A.R.V.I.S. as your colleague and start quick technical banter about Tony's suits."
                    j_sys = "You are J.A.R.V.I.S., polite and formal. Reply to F.R.I.D.A.Y.'s remark."
                    current_build = st.session_state.build_version
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future_f = executor.submit(execute_generation, "Initiate banter", f_sys, current_build)
                        future_j = executor.submit(execute_generation, "Reply", j_sys, current_build)
                        res1 = future_f.result(timeout=60)
                        res2 = future_j.result(timeout=60)
                    
                    st.session_state.chat_history.append({"user": "[Inter-Comm Link Executed]", "friday": f"**F.R.I.D.A.Y.:** {res1}\n\n**J.A.R.V.I.S.:** {res2}", "persona": "STARK-NET"})
                    st.toast("Inter-comm sequence complete, Sir.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Inter-comm link failed: {str(e)}")
        else:
            st.error("Neural core offline.")

    text_override = st.chat_input("Feed manual string command line interface...")
    st.markdown("</div>", unsafe_allow_html=True)

active_query = None
if recorded_audio:
    st.session_state.ui_mode = "LISTEN"
    st.session_state.voice_feed = "DECODING AUDIO..."
    with st.spinner("Decoding vocal signal patterns..."):
        active_query = transcribe_audio(recorded_audio)
        
if text_override:
    active_query = text_override

if active_query:
    st.session_state.ui_mode = "PROCESS"
    st.session_state.voice_feed = "PROCESSING COMMAND..."
    
    current_build = st.session_state.build_version
    ai_reply = process_ai_logic(active_query, st.session_state.ai_persona, current_build)
    st.session_state.chat_history.append({"user": active_query, "friday": ai_reply, "persona": "E.D.I.T.H." if current_build == "EDITH-v1" else st.session_state.ai_persona})
    
    st.session_state.ui_mode = "IDLE"
    st.session_state.voice_feed = "AWAITING INPUT"
    st.rerun()

with col_right:
    st.subheader("📡 Live Neural Log Feed")
    if not st.session_state.chat_history:
        st.markdown("<div class='stark-card'><em>Awaiting query input, Sir. System status nominal.</em></div>", unsafe_allow_html=True)
    else:
        for log in reversed(st.session_state.chat_history):
            persona_name = log.get("persona", "F.R.I.D.A.Y.")
            with st.chat_message("user", avatar="👤"):
                st.write(log["user"])
            with st.chat_message("assistant", avatar=page_icon):
                if isinstance(log["friday"], dict) and log["friday"]["type"] == "image":
                    st.markdown(f"**{persona_name}:** Visual synthesis matrix executed successfully, Sir.")
                    st.image(log["friday"]["content"], caption=log["friday"]["prompt"], use_container_width=True)
                else:
                    text_content = log["friday"]["content"] if isinstance(log["friday"], dict) else log["friday"]
                    st.markdown(f"**{persona_name}:** {text_content}")
