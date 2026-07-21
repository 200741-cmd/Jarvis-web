import streamlit as st
import speech_recognition as sr
import datetime
import wikipedia
import psutil
import io
import time
import random
from google import genai
from google.genai import types
from PIL import Image
import json

# 1. SCI-FI TERMINAL STYLING & HEADERS (NEON BLUE COMMAND DECK)
st.set_page_config(
    page_title="JARVIS // Tactical OS",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #060b13;
        color: #8bb2d9;
        font-family: 'Consolas', 'Courier New', monospace;
    }
    .cyber-title {
        color: #00a2ff;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 8px rgba(0, 162, 255, 0.6), 0 0 15px rgba(0, 162, 255, 0.4);
        font-weight: 800;
        letter-spacing: 2px;
    }
    .terminal-card {
        background: rgba(0, 162, 255, 0.04);
        border: 1px solid #0055ff;
        padding: 22px;
        border-radius: 6px;
        box-shadow: 0 0 12px rgba(0, 85, 255, 0.2);
    }
    h3 {
        color: #00d2ff !important;
        border-bottom: 1px dashed #0055ff;
        padding-bottom: 5px;
    }
    .stProgress > div > div > div > div {
        background-color: #00a2ff !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. STATE PERSISTENCE & MEMORY ENGINE
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ui_mode" not in st.session_state:
    st.session_state.ui_mode = "IDLE"
if "voice_feed" not in st.session_state:
    st.session_state.voice_feed = "AWAITING INPUT"

api_key = st.secrets.get("API_KEY", "")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

# 3. CORE AUDIO SPEECH-TO-TEXT TRANSCRIPTION
def transcribe_audio(audio_buffer):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_buffer.read())) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data, language='en-US')
    except sr.UnknownValueError:
        return "ERROR: Acoustic waveform unreadable by central diagnostic grid."
    except Exception as e:
        return f"ERROR: System transcription layer failed. ({str(e)})"

# 4. ACTION MATRIX CAPABILITY PROTOCOLS (WITH 503 EXPONENTIAL BACKOFF RETRY)
def process_jarvis_logic(query_text):
    query = query_text.lower().strip()
    
    if "wikipedia" in query:
        search_target = query.replace("wikipedia", "").strip()
        try:
            return {"type": "text", "content": f"Querying international information grid... {wikipedia.summary(search_target, sentences=2)}"}
        except Exception:
            return {"type": "text", "content": "Unable to pull valid log matches from the Wikipedia index, Sir."}
            
    elif "open youtube" in query:
        return {"type": "text", "content": "Matrix link generated: [Click to launch YouTube Mainframe](https://youtube.com)"}
        
    elif "open google" in query:
        return {"type": "text", "content": "Matrix link generated: [Click to launch Google Gateway](https://google.com)"}
        
    elif "the time" in query or "time sync" in query:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return {"type": "text", "content": f"Localized time stream reads: {current_time}, Sir."}
        
    elif "generate image" in query or "draw" in query or "create a picture" in query:
        if client:
            image_prompt = query_text.replace("generate image", "").replace("draw", "").replace("create a picture", "").strip()
            
            # Retry loop with exponential backoff for 503 server overloads
            max_retries = 3
            wait_time = 2
            for attempt in range(max_retries):
                try:
                    result = client.models.generate_images(
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
                    if "503" in str(e) and attempt < max_retries - 1:
                        time.sleep(wait_time + random.uniform(0, 1))
                        wait_time *= 2
                        continue
                    return {"type": "text", "content": f"Visual synthesis failed, Sir. Server matrix overloaded (503). Logs state: {str(e)}"}
            return {"type": "text", "content": "Visual synthesis core busy, Sir. High traffic capacity lock encountered."}
        else:
            return {"type": "text", "content": "Neural core offline. Please configure your API_KEY, Sir."}
            
    else:
        if client:
            system_instruction = "You are JARVIS, a highly advanced, intelligent, loyal, and slightly witty AI assistant. Address the user as Sir."
            
            # Retry loop with exponential backoff for chat text overloads
            max_retries = 3
            wait_time = 2
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.5-flash', 
                        contents=query_text,
                        config={'system_instruction': system_instruction}
                    )
                    return {"type": "text", "content": response.text}
                except Exception as e:
                    if "503" in str(e) and attempt < max_retries - 1:
                        time.sleep(wait_time + random.uniform(0, 1))
                        wait_time *= 2
                        continue
                    return {"type": "text", "content": f"Neural link transmission failed, Sir. Server capacity saturated (503). Logs state: {str(e)}"}
        else:
            return {"type": "text", "content": "Neural core offline. Please configure your API_KEY in the Streamlit Settings dashboard, Sir."}

# 5. DYNAMIC GRAPHIC CANVAS COMPONENT
cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
core_temp = 31

recent_logs = ["> A.R.C. CORES ACTIVE", "> LINKED TO STREAMLIT OS"]
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
            background-color: #060b13;
            background-image: 
                linear-gradient(rgba(0,162,255,0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,162,255,0.02) 1px, transparent 1px);
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
        .terminal-overlay {{ background: rgba(15, 17, 22, 0.6); border: 1px solid rgba(0, 162, 255, 0.2); padding: 12px; width: 230px; font-family: monospace; font-size: 11px; color: #a5b4fc; opacity: 0.8; line-height: 1.6; border-radius: 4px; }}
        .core-wrapper {{ position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center; }}
        .mode-pill {{ background: #060b13; border: 2px solid #00e5ff; border-radius: 20px; padding: 3px 15px; font-size: 11px; font-weight: bold; margin-bottom: -15px; box-shadow: 0 0 10px rgba(0, 229, 255, 0.2); z-index: 10; font-family: monospace; }}
        .arc-rings {{ width: 150px; height: 150px; border-radius: 50%; border: 3px dashed rgba(0, 229, 255, 0.4); display: flex; align-items: center; justify-content: center; position: relative; }}
        .arc-rings::before {{ content: ''; position: absolute; width: 110px; height: 110px; border-radius: 50%; border: 2px dashed rgba(0, 229, 255, 0.6); animation: rotateCCW 12s linear infinite; }}
        .core-glow-dot {{ width: 14px; height: 14px; background-color: #00e5ff; border-radius: 50%; box-shadow: 0 0 25px 8px #00e5ff; }}
        .mini-bars-panel {{ width: 180px; display: flex; flex-direction: column; gap: 12px; font-size: 9px; font-weight: bold; font-family: monospace; color: #8bb2d9; }}
        .bar-row {{ display: flex; flex-direction: column; gap: 4px; }}
        .bar-bg {{ background: rgba(0, 162, 255, 0.1); height: 5px; border-radius: 2px; overflow: hidden; }}
        .bar-fill {{ height: 100%; background: #00a2ff; transition: width 0.4s ease; }}
        .voice-feed-status {{ position: absolute; right: 0; bottom: 10px; text-align: right; font-family: monospace; }}
        .voice-title {{ font-size: 11px; font-weight: bold; color: rgba(255,255,255,0.6); }}
        .voice-value {{ font-size: 12px; font-weight: bold; color: #00e5ff; margin-top: 2px; }}
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
st.markdown("<h1 class='cyber-title'>⚡ JARVIS // TACTICAL BLUE OS</h1>", unsafe_allow_html=True)
st.caption("COMMUNICATION SPECTRUM: BLUE // NEURAL COGNITION GENERATION 3.5 ONLINE")
st.write("---")

left_col, right_col = st.columns([2, 1], gap="large")

with left_col:
    st.subheader("🖥️ Operations Control Array")
    
    st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
    recorded_audio = st.audio_input("Open Microscopic Frequency Receiver")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("")
    text_override = st.chat_input("Feed manual string command line interface... (e.g., 'Generate image of a futuristic laboratory')")
    
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
        
        jarvis_reply = process_jarvis_logic(active_query)
        st.session_state.chat_history.append({"user": active_query, "jarvis": jarvis_reply})
        
        st.session_state.ui_mode = "IDLE"
        st.session_state.voice_feed = "AWAITING INPUT"
        st.rerun()

    for log in reversed(st.session_state.chat_history):
        with st.chat_message("user", avatar="👤"):
            st.write(log["user"])
        with st.chat_message("assistant", avatar="⚡"):
            if isinstance(log["jarvis"], dict) and log["jarvis"]["type"] == "image":
                st.markdown(f"**JARVIS:** Visual schematic rendered successfully for: *{log['jarvis']['prompt']}*")
                st.image(log["jarvis"]["content"], caption=log["jarvis"]["prompt"], use_container_width=True)
            else:
                text_content = log["jarvis"]["content"] if isinstance(log["jarvis"], dict) else log["jarvis"]
                st.markdown(f"**JARVIS:** {text_content}")

with right_col:
    st.subheader("📊 Datastream Matrix")
    
    with st.container():
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        st.metric(label="CYBER LINK HUB", value="SECURE", delta="Gemini 3.5 Flash Active")
        
        st.progress(cpu / 100, text=f"Core CPU Load Array: {cpu}%")
        st.progress(ram / 100, text=f"Volatile VRAM Allocation: {ram}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.write("")
    st.subheader("🛠 Honor Command Controls")
    
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px;'>
        <span style='color: rgba(255,255,255,0.4); font-size: 12px; display: block;'>SYSTEM MODE STATUS</span>
        <strong style='color: #00e5ff; font-size: 18px; font-family: monospace;'>{st.session_state.ui_mode}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Flush Cache Matrices", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.ui_mode = "IDLE"
        st.session_state.voice_feed = "AWAITING INPUT"
        st.toast("Active variable stack cleared, Sir.")
        st.rerun()
