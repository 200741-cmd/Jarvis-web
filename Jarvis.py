import streamlit as st
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import psutil
import io
from google import genai

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

# 4. ACTION MATRIX CAPABILITY PROTOCOLS
def process_jarvis_logic(query_text):
    query = query_text.lower().strip()
    
    if "wikipedia" in query:
        search_target = query.replace("wikipedia", "").strip()
        try:
            return f"Querying international information grid... {wikipedia.summary(search_target, sentences=2)}"
        except Exception:
            return "Unable to pull valid log matches from the Wikipedia index, Sir."
            
    elif "open youtube" in query:
        return "Matrix link generated: [Click to launch YouTube Mainframe](https://youtube.com)"
        
    elif "open google" in query:
        return "Matrix link generated: [Click to launch Google Gateway](https://google.com)"
        
    elif "the time" in query or "time sync" in query:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"Localized time stream reads: {current_time}, Sir."
        
    else:
        # --- THE FRONTIER NEURAL UPDATE GATE ---
        if client:
            try:
                system_instruction = "You are JARVIS, a highly advanced, intelligent, loyal, and slightly witty AI assistant. Address the user as Sir."
                
                # Upgraded to the latest frontier model definition
                response = client.models.generate_content(
                    model='gemini-3.5-flash', 
                    contents=query_text,
                    config={'system_instruction': system_instruction}
                )
                return response.text
            except Exception as e:
                return f"Neural link transmission failed, Sir. Matrix logs state: {str(e)}"
        else:
            return "Neural core offline. Please configure your API_KEY in the Streamlit Settings dashboard, Sir."

# 5. USER FRONTEND INTERFACE MATRIX
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
    text_override = st.chat_input("Feed manual string command line interface...")
    
    active_query = None
    
    if recorded_audio:
        with st.spinner("Decoding vocal signal patterns..."):
            active_query = transcribe_audio(recorded_audio)
            
    if text_override:
        active_query = text_override

    if active_query:
        jarvis_reply = process_jarvis_logic(active_query)
        st.session_state.chat_history.append({"user": active_query, "jarvis": jarvis_reply})

    for log in reversed(st.session_state.chat_history):
        with st.chat_message("user", avatar="👤"):
            st.write(log["user"])
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(f"**JARVIS:** {log['jarvis']}")

with right_col:
    st.subheader("📊 Datastream Matrix")
    
    with st.container():
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        st.metric(label="CYBER LINK HUB", value="SECURE", delta="Gemini 3.5 Flash Active")
        
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        st.progress(cpu / 100, text=f"Core CPU Load Array: {cpu}%")
        st.progress(ram / 100, text=f"Volatile VRAM Allocation: {ram}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.write("")
    st.subheader("🛠️ Core Resets")
    if st.button("Flush Cache Matrices", use_container_width=True):
        st.session_state.chat_history = []
        st.toast("Active variable stack cleared, Sir.")
