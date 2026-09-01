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

# 2. STATE PERSISTENCE & MEMORY ENGINE (Initialized early for theme configuration)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ui_mode" not in st.session_state:
    st.session_state.ui_mode = "IDLE"
if "voice_feed" not in st.session_state:
    st.session_state.voice_feed = "AWAITING INPUT"
if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "F.R.I.D.A.Y."

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
else:
    bg_color = "#05080c"
    text_color = "#80d8ff"
    accent_color = "#00e5ff"
    border_color = "#00b8d4"
    shadow_color = "rgba(0, 229, 255, 0.7)"
    card_bg = "rgba(0, 229, 255, 0.04)"
    page_icon = "🔵"
    glow_dot = "#00e5ff"
    glow_shadow = "#00b8d4"

# 1. IRON MAN STARK TECH STYLING & HEADERS (DYNAMIC THEME DECK)
st.set_page_config(
    page_title=f"{st.session_state.ai_persona} // Tactical OS",
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
    }
    .terminal-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        padding: 22px;
        border-radius: 6px;
        box-shadow: 0 0 12px {border_color};
    }
    h3 {{
        color: {accent_color} !important;
        border-bottom: 1px dashed {border_color};
        padding-bottom: 5px;
    }
    .stProgress > div > div > div > div {{
        background-color: {accent_color} !important;
    }}
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("API_KEY", "")

if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        client = None
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
        return "ERROR: Acoustic waveform unreadable by tactical grid."
    except Exception as e:
        return f"ERROR: Audio transcription layer failed. ({str(e)})"

# 4. STREAMLINED ACTION MATRIX (STABLE VERSION 3.6 ROUTING)
def process_ai_logic(query_text, persona):
    query = query_text.lower().strip()
    
    if "wikipedia" in query:
        search_target = query.replace("wikipedia", "").strip()
        try:
            return {"type": "text", "content": f"Accessing global archives, Boss... {wikipedia.summary(search_target, sentences=2)}"}
        except Exception:
            return {"type": "text", "content": "Couldn't match any solid logs in the database, Boss."}
            
    elif "open youtube" in query:
        return {"type": "text", "content": "Link established: [Click to launch YouTube Mainframe](https://youtube.com)"}
        
    elif "open google" in query:
        return {"type": "text", "content": "Link established: [Click to launch Google Gateway](https://google.com)"}
        
    elif "the time" in query or "time sync" in query:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return {"type": "text", "content": f"Current local time stream reads: {current_time}, Boss."}
        
    elif any(keyword in query for keyword in ["generate", "draw", "create", "image", "picture", "photo", "apple", "dalle"]):
        if client:
            image_prompt = query_text if "apple" not in query else "A crisp, vibrant, perfectly polished red apple sitting on a clean wooden surface with soft cinematic studio lighting."
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
                return {"type": "text", "content": f"Visual synthesis failed, Boss. ({str(e)})"}
        else:
            return {"type": "text", "content": "Neural core offline. Configure your API_KEY in secrets, Boss."}
            
    else:
        if client:
            if persona == "F.R.I.D.A.Y.":
                system_instruction = "You are F.R.I.D.A.Y., the advanced, witty, and loyal AI assistant created by Tony Stark. Address the user as Boss. Keep answers concise and sharp."
            else:
                system_instruction = "You are J.A.R.V.I.S., the highly sophisticated, impeccably polite, British-accented tactical AI assistant created by Tony Stark. Address the user as Boss. Keep answers concise, formal, and articulate."
                
            try:
                response = client.models.generate_content(
                    model='gemini-3.6-flash', 
                    contents=query_text,
                    config={'system_instruction': system_instruction}
                )
                return {"type": "text", "content": response.text}
            except Exception as e:
                return {"type": "text", "content": f"Neural link transmission error: {str(e)}, Boss."}
        else:
            return {"type": "text", "content": "Neural core offline. Configure your API_KEY in Streamlit secrets, Boss."}

# 5. DYNAMIC GRAPHIC CANVAS COMPONENT (THEME-AWARE HUD)
cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
core_temp = 34

recent_logs = [f"> {st.session_state.ai_persona} OS ONLINE (VERSION 3.6)", "> LINKED TO STARK ARCHIVES"]
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
st.markdown(f"<h1 class='cyber-title'>{page_icon} {st.session_state.ai_persona} // VERSION 3.6 OS</h1>", unsafe_allow_html=True)
st.caption(f"COMMUNICATION SPECTRUM: {st.session_state.ai_persona.upper()} THEME // ACTIVE PROTOCOL: {st.session_state.ai_persona} (VERSION 3.6)")
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
        st.metric(label="STARK LINK HUB", value="SECURE", delta="Version 3.6 Active")
        
        selected_persona = st.radio("AI Protocol Selector", ["F.R.I.D.A.Y.", "J.A.R.V.I.S."], index=0 if st.session_state.ai_persona == "F.R.I.D.A.Y." else 1)
        if selected_persona != st.session_state.ai_persona:
            st.session_state.ai_persona = selected_persona
            st.toast(f"Protocol shifted to {selected_persona}. Adapting color matrix, Boss.")
            st.rerun()
            
        st.write("")
        st.progress(cpu / 100, text=f"Core CPU Load Array: {cpu}%")
        st.progress(ram / 100, text=f"Volatile VRAM Allocation: {ram}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.write("")
    st.subheader("🛠 Honor Command Controls")
    
    st.markdown(f"""
    <div style='background: {card_bg}; border: 1px solid {border_color}; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px;'>
        <span style='color: rgba(255,255,255,0.4); font-size: 12px; display: block;'>SYSTEM MODE STATUS</span>
        <strong style='color: {accent_color}; font-size: 18px; font-family: monospace;'>{st.session_state.ui_mode}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Flush Cache Matrices", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.ui_mode = "IDLE"
        st.session_state.voice_feed = "AWAITING INPUT"
        st.toast("Active variable stack cleared, Boss.")
        st.rerun()
