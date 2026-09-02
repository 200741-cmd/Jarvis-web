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
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ui_mode" not in st.session_state:
    st.session_state.ui_mode = "IDLE"
if "voice_feed" not in st.session_state:
    st.session_state.voice_feed = "AWAITING INPUT"
if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "F.R.I.D.A.Y."
if "build_version" not in st.session_state:
    st.session_state.build_version = "v3.6"

# DYNAMIC THEME PALETTE CONFIGURATION
if st.session_state.ai_persona == "F.R.I.D.A.Y.":
    bg_color = "#0c0805"
    text_color = "#ffb74d"
    accent_color = "#ff9900"
    border_color = "#ff6600"
    shadow_color = "rgba(255, 153, 0, 0.7)"
    card_bg = "rgba(255, 153, 0, 0.04)"
    page_icon = "🟠"
    glow_dot = "#ff9900"
    glow_shadow = "#ff6600"
elif st.session_state.ai_persona == "J.A.R.V.I.S.":
    bg_color = "#05080c"
    text_color = "#80d8ff"
    accent_color = "#00e5ff"
    border_color = "#00b8d4"
    shadow_color = "rgba(0, 229, 255, 0.7)"
    card_bg = "rgba(0, 229, 255, 0.04)"
    page_icon = "🔵"
    glow_dot = "#00e5ff"
    glow_shadow = "#00b8d4"
else: # BOTH (DUAL PROTOCOL HYBRID MATRIX)
    bg_color = "#07050c"
    text_color = "#e1bee7"
    accent_color = "#ab47bc"
    border_color = "#8e24aa"
    shadow_color = "rgba(171, 71, 188, 0.7)"
    card_bg = "rgba(171, 71, 188, 0.04)"
    page_icon = "⚡"
    glow_dot = "#ab47bc"
    glow_shadow = "#8e24aa"

# 1. IRON MAN STARK TECH STYLING & HEADERS
st.set_page_config(
    page_title=f"{st.session_state.ai_persona} // Tactical OS ({st.session_state.build_version})",
    page_icon=page_icon,
    layout="wide"
)

st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Consolas', 'Courier New', monospace;
    }}
    .cyber-title {{
        color: {accent_color};
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px {shadow_color}, 0 0 20px {shadow_color};
        font-weight: 800;
        letter-spacing: 2px;
    }}
    .terminal-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        padding: 22px;
        border-radius: 6px;
        box-shadow: 0 0 12px {border_color};
    }}
    h3 {{
        color: {accent_color} !important;
        border-bottom: 1px dashed {border_color};
        padding-bottom: 5px;
    }}
    .stProgress > div > div > div > div {{
        background-color: {accent_color} !important;
    }}
</style>
""", unsafe_allow_html=True)

# VERSION-AWARE CLIENT INITIALIZATION
@st.cache_resource
def init_active_clients(build_ver):
    if build_ver == "v3.4":
        # v3.4 Mode: Single legacy key fallback only
        k = st.secrets.get("API_KEY", "")
        return [genai.Client(api_key=k)] if k.strip() else []
    else:
        # v3.5 & v3.6 Mode: Multi-key pool bank
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

# 3. CORE AUDIO SPEECH-TO-TEXT TRANSCRIPTION
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

# 4. VERSION-AWARE GENERATION ENGINE
def _single_generation_call(chosen_client, query_text, system_instruction):
    response = chosen_client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=query_text,
        config={'system_instruction': system_instruction}
    )
    return response.text

def execute_generation(query_text, system_instruction):
    global active_clients, _key_counter
    if not active_clients:
        raise Exception("All neural key banks offline. Configure your API keys in secrets, Boss.")
    
    # Behavior adapts based on chosen build version
    if st.session_state.build_version == "v3.4":
        # v3.4: Simple single call without failover loop or thread timeout
        return _single_generation_call(active_clients[0], query_text, system_instruction)
        
    elif st.session_state.build_version == "v3.5":
        # v3.5: Multi-key rotation without strict thread safety/timeouts
        chosen_client = active_clients[_key_counter % len(active_clients)]
        _key_counter += 1
        return _single_generation_call(chosen_client, query_text, system_instruction)
        
    else:
        # v3.6 (Current): Thread-safe failover with 12s timeout guards
        start_index = _key_counter % len(active_clients)
        for i in range(len(active_clients)):
            client_idx = (start_index + i) % len(active_clients)
            chosen_client = active_clients[client_idx]
            _key_counter += 1
            
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_single_generation_call, chosen_client, query_text, system_instruction)
                    result_text = future.result(timeout=12)
                    
                if i > 0:
                    return f"[Failover Shifted to Key Index {client_idx + 1}] {result_text}"
                return result_text
            except Exception:
                continue
        raise Exception("Neural query timed out or key bank exhausted, Boss.")

def process_ai_logic(query_text, persona):
    query = query_text.lower().strip()
    
    if "wikipedia" in query:
        search_target = query.replace("wikipedia", "").strip()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(wikipedia.summary, search_target, 2)
                summary = future.result(timeout=8)
            return {"type": "text", "content": f"Accessing global archives, Boss... {summary}"}
        except Exception:
            return {"type": "text", "content": "Couldn't match any solid logs or archives timed out, Boss."}
            
    elif "open youtube" in query:
        return {"type": "text", "content": "Link established: [Click to launch YouTube Mainframe](https://youtube.com)"}
        
    elif "open google" in query:
        return {"type": "text", "content": "Link established: [Click to launch Google Gateway](https://google.com)"}
        
    elif "the time" in query or "time sync" in query:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return {"type": "text", "content": f"Current local time stream reads: {current_time}, Boss."}
        
    elif any(keyword in query for keyword in ["generate", "draw", "create", "image", "picture", "photo", "apple", "dalle"]):
        if active_clients:
            image_prompt = query_text if "apple" not in query else "A crisp, vibrant, perfectly polished red apple sitting on a clean wooden surface with soft cinematic studio lighting."
            try:
                result = active_clients[0].models.generate_images(
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
                    return {"type": "image", "content": image, "prompt": image_prompt}
            except Exception as e:
                return {"type": "text", "content": f"Visual synthesis failed, Boss. ({str(e)})"}
        else:
            return {"type": "text", "content": "Neural core offline. Configure your API keys in secrets, Boss."}
            
    else:
        if active_clients:
            if persona == "F.R.I.D.A.Y.":
                system_instruction = "You are F.R.I.D.A.Y., the advanced, witty, and loyal AI assistant created by Tony Stark. Address the user as Boss. Keep answers concise and sharp."
                reply_text = execute_generation(query_text, system_instruction)
                return {"type": "text", "content": reply_text}
                
            elif persona == "J.A.R.V.I.S.":
                system_instruction = "You are J.A.R.V.I.S., the highly sophisticated, impeccably polite, British-accented tactical AI assistant created by Tony Stark. Address the user as Boss. Keep answers concise, formal, and articulate."
                reply_text = execute_generation(query_text, system_instruction)
                return {"type": "text", "content": reply_text}
                
            else: # BOTH PROTOCOLS SIMULTANEOUSLY
                f_sys = "You are F.R.I.D.A.Y., witty and sharp. Address the user as Boss. Give a short take."
                j_sys = "You are J.A.R.V.I.S., polite, British, and formal. Address the user as Boss. Give a short take."
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future_f = executor.submit(execute_generation, query_text, f_sys)
                        future_j = executor.submit(execute_generation, query_text, j_sys)
                        res1 = future_f.result(timeout=14)
                        res2 = future_j.result(timeout=14)
                    
                    dual_output = f"**[F.R.I.D.A.Y.]:** {res1}\n\n**[J.A.R.V.I.S.]:** {res2}"
                    return {"type": "text", "content": dual_output}
                except Exception as e:
                    return {"type": "text", "content": f"Dual protocol neural link timeout or error: {str(e)}, Boss."}
        else:
            return {"type": "text", "content": "Neural core offline. Configure your API keys in Streamlit secrets, Boss."}

# 5. LIGHTWEIGHT NON-BLOCKING TELEMETRY
try:
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
except Exception:
    cpu = 15.0
    ram = 40.0
core_temp = 34

recent_logs = [f"> {st.session_state.ai_persona} OS ONLINE ({st.session_state.build_version})", f"> GLOBAL POOL: {active_keys_status}"]
for item in st.session_state.chat_history[-3:]:
    user_line = f"> INCOMING: {item['user'].upper()[:22]}"
    recent_logs.append(user_line)

hud_data = {
    "mode": st.session_state.ui_mode,
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
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; }}
        body {{
            background-color: {bg_color};
            background-image: 
                linear-gradient({border_color}0a 1px, transparent 1px),
                linear-gradient(90deg, {border_color}0a 1px, transparent 1px);
            background-size: 30px 30px;
            color: #ffffff;
            height: 380px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 10px;
            overflow: hidden;
        }}
        .grid-canvas {{ display: flex; justify-content: space-between; align-items: center; height: 100%; position: relative; }}
        .terminal-overlay {{ background: rgba(10, 15, 20, 0.7); border: 1px solid {border_color}; padding: 12px; width: 230px; font-family: monospace; font-size: 11px; color: {text_color}; opacity: 0.9; line-height: 1.6; border-radius: 4px; }}
        .core-wrapper {{ position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center; }}
        .mode-pill {{ background: {bg_color}; border: 2px solid {accent_color}; border-radius: 20px; padding: 3px 15px; font-size: 11px; font-weight: bold; margin-bottom: -15px; box-shadow: 0 0 12px {shadow_color}; z-index: 10; font-family: monospace; color: {accent_color}; }}
        .arc-rings {{ width: 150px; height: 150px; border-radius: 50%; border: 3px dashed {border_color}; display: flex; align-items: center; justify-content: center; position: relative; }}
        .arc-rings::before {{ content: ''; position: absolute; width: 110px; height: 110px; border-radius: 50%; border: 2px dashed {accent_color}; animation: rotateCCW 12s linear infinite; }}
        .core-glow-dot {{ width: 14px; height: 14px; background-color: {glow_dot}; border-radius: 50%; box-shadow: 0 0 25px 8px {glow_shadow}; }}
        .mini-bars-panel {{ width: 180px; display: flex; flex-direction: column; gap: 12px; font-size: 9px; font-weight: bold; font-family: monospace; color: {text_color}; }}
        .bar-row {{ display: flex; flex-direction: column; gap: 4px; }}
        .bar-bg {{ background: {border_color}1a; height: 5px; border-radius: 2px; overflow: hidden; }}
        .bar-fill {{ height: 100%; background: {accent_color}; transition: width 0.4s ease; }}
        .voice-feed-status {{ position: absolute; right: 0; bottom: 10px; text-align: right; font-family: monospace; }}
        .voice-title {{ font-size: 11px; font-weight: bold; color: rgba(255,255,255,0.6); }}
        .voice-value {{ font-size: 12px; font-weight: bold; color: {accent_color}; margin-top: 2px; }}
        @keyframes rotateCCW {{ 100% {{ transform: rotate(-360deg); }} }}
    </style>
</head>
<body class="ui-{hud_data['mode']}">
    <div class="grid-canvas">
        <div class="terminal-overlay">
            {"".join([f"{log}<br>" for log in hud_data['logs']])}
        </div>
        <div class="core-wrapper">
            <div class="mode-pill">MODE: {hud_data['mode']}</div>
            <div class="arc-rings"><div class="core-glow-dot"></div></div>
        </div>
        <div class="mini-bars-panel">
            <div class="bar-row"><div>CPU LOAD</div><div class="bar-bg"><div class="bar-fill" style="width: {hud_data['cpu']}%"></div></div></div>
            <div class="bar-row"><div>MEM ALLOC</div><div class="bar-bg"><div class="bar-fill" style="width: {hud_data['ram']}%"></div></div></div>
            <div class="bar-row"><div>CORE TEMP</div><div class="bar-bg"><div class="bar-fill" style="width: {hud_data['temp']}%"></div></div></div>
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

# 6. USER FRONTEND INTERFACE MATRIX
st.markdown(f"<h1 class='cyber-title'>{page_icon} {st.session_state.ai_persona} // OS BUILD {st.session_state.build_version}</h1>", unsafe_allow_html=True)
st.caption(f"COMMUNICATION SPECTRUM: {st.session_state.ai_persona.upper()} THEME // ENGINE PROFILE: {st.session_state.build_version}")
st.write("---")

left_col, right_col = st.columns([2, 1], gap="large")

with left_col:
    st.subheader("🖥️ Operations Control Array")
    
    st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
    recorded_audio = st.audio_input("Open Microscopic Frequency Receiver")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("")
    text_override = st.chat_input("Feed manual string command line interface... (e.g., 'Generate an image of a red apple')")
    
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
        
        ai_reply = process_ai_logic(active_query, st.session_state.ai_persona)
        st.session_state.chat_history.append({"user": active_query, "friday": ai_reply, "persona": st.session_state.ai_persona})
        
        st.session_state.ui_mode = "IDLE"
        st.session_state.voice_feed = "AWAITING INPUT"
        st.rerun()

    for log in reversed(st.session_state.chat_history):
        persona_name = log.get("persona", "F.R.I.D.A.Y.")
        with st.chat_message("user", avatar="👤"):
            st.write(log["user"])
        with st.chat_message("assistant", avatar=page_icon):
            if isinstance(log["friday"], dict) and log["friday"]["type"] == "image":
                st.markdown(f"**{persona_name}:** Visual synthesis matrix executed successfully, Boss.")
                st.image(log["friday"]["content"], caption=log["friday"]["prompt"], use_container_width=True)
            else:
                text_content = log["friday"]["content"] if isinstance(log["friday"], dict) else log["friday"]
                st.markdown(f"**{persona_name}:** {text_content}")

with right_col:
    st.subheader("📊 Datastream Matrix")
    
    with st.container():
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        st.metric(label="STARK LINK HUB", value="SECURE", delta=active_keys_status)
        
        protocols = ["F.R.I.D.A.Y.", "J.A.R.V.I.S.", "BOTH"]
        current_index = protocols.index(st.session_state.ai_persona) if st.session_state.ai_persona in protocols else 0
        selected_persona = st.radio("AI Protocol Selector", protocols, index=current_index)
        
        if selected_persona != st.session_state.ai_persona:
            st.session_state.ai_persona = selected_persona
            st.toast(f"Protocol shifted to {selected_persona}. Global key pool online, Boss.")
            st.rerun()
            
        st.write("")
        if st.button("🗣️ Initiate AI Inter-Comm Dialogue", use_container_width=True):
            if active_clients:
                with st.spinner("Connecting F.R.I.D.A.Y. and J.A.R.V.I.S. neural link..."):
                    try:
                        f_sys = "You are F.R.I.D.A.Y., witty and sharp. Address J.A.R.V.I.S. as your colleague and start quick technical banter about Tony's suits."
                        j_sys = "You are J.A.R.V.I.S., polite and formal. Reply to F.R.I.D.A.Y.'s remark."
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future_f = executor.submit(execute_generation, "Initiate banter", f_sys)
                            future_j = executor.submit(execute_generation, "Reply", j_sys)
                            res1 = future_f.result(timeout=12)
                            res2 = future_j.result(timeout=12)
                        
                        st.session_state.chat_history.append({"user": "[Inter-Comm Link Executed]", "friday": f"**F.R.I.D.A.Y.:** {res1}\n\n**J.A.R.V.I.S.:** {res2}", "persona": "STARK-NET"})
                        st.toast("Inter-comm sequence complete, Boss.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Inter-comm link timed out or failed: {str(e)}")
            else:
                st.error("Neural core offline. Configure API keys in secrets, Boss.")

        st.write("")
        st.progress(cpu / 100, text=f"Core CPU Load Array: {cpu}%")
        st.progress(ram / 100, text=f"Volatile VRAM Allocation: {ram}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.write("")
    st.subheader("📂 Stark Archive Vault")
    
    with st.expander("Code Version Vault & Runner"):
        st.caption("Switch active execution engines to older updates.")
        
        build_options = ["v3.6", "v3.5", "v3.4"]
        current_b_idx = build_options.index(st.session_state.build_version) if st.session_state.build_version in build_options else 0
        
        selected_build_label = st.selectbox("Active Operational Build", [
            "v3.6 (Current - Thread-Safe & Fail-Safe)",
            "v3.5 (Multi-Key Pool Engine)",
            "v3.4 (Single-Key Legacy Mode)"
        ], index=current_b_idx)
        
        target_version = selected_build_label.split()[0]
        
        if target_version != st.session_state.build_version:
            st.session_state.build_version = target_version
            st.toast(f"Switched active runtime engine to {target_version}, Boss!")
            st.rerun()
            
        if st.session_state.build_version == "v3.5":
            st.info("Active Engine: v3.5 (Multi-key pool active without thread timeout guards).")
        elif st.session_state.build_version == "v3.4":
            st.warning("Active Engine: v3.4 (Single legacy key mode active).")
        else:
            st.success("Active Engine: v3.6 (Fully optimized with fail-safe thread pools).")

    st.write("")
    st.subheader("🛠 Honor Command Controls")
    
    st.markdown(f"""
    <div style='background: {card_bg}; border: 1px solid {border_color}; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px;'>
        <span style='color: rgba(255,255,255,0.4); font-size: 12px; display: block;'>SYSTEM MODE STATUS</span>
        <strong style='color: {accent_color}; font-size: 18px; font-family: monospace;'>{st.session_state.ui_mode}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔍 Diagnostics", use_container_width=True):
            st.toast(f"Diagnostic scan complete ({st.session_state.build_version}): Subsystems operational, Boss.")
    with col_b:
        if st.button("🚀 Lockdown", use_container_width=True):
            st.toast("Emergency Protocol: Perimeter secure. Armor bay sealed.")
            
    if st.button("⚡ Boost Mainframe Power", use_container_width=True):
        st.toast("Arc Reactor output surged by 400%, Boss! Latency optimized.")

    st.write("")
    if st.button("Flush Cache Matrices", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.ui_mode = "IDLE"
        st.session_state.voice_feed = "AWAITING INPUT"
        st.toast("Active variable stack cleared, Boss.")
        st.rerun()
