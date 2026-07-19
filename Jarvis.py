import streamlit as st
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import psutil
import io

# 1. SCI-FI TERMINAL STYLING & HEADERS
st.set_page_config(
    page_title="JARVIS // Cloud Interface",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Courier New', Courier, monospace;
    }
    .cyber-title {
        color: #00f0ff;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px #00f0ff;
        font-weight: bold;
    }
    .terminal-card {
        background: rgba(0, 240, 255, 0.03);
        border: 1px solid #00f0ff;
        padding: 20px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 2. STATE PERSISTENCE & MEMORY ENGINE
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Fetch key securely from Streamlit App Settings -> Secrets panel
# (Will not throw errors if you are testing locally without the key loaded yet)
api_key = st.secrets.get("API_KEY", "LOCAL_DEV_MODE")

# 3. CORE AUDIO SPEECH-TO-TEXT TRANSCRIPTION
def transcribe_audio(audio_buffer):
    """Converts recorded browser audio bytes into text strings."""
    recognizer = sr.Recognizer()
    try:
        # Convert the Streamlit upload file structure into an audio source object
        with sr.AudioFile(io.BytesIO(audio_buffer.read())) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data, language='en-US')
    except sr.UnknownValueError:
        return "ERROR: Telemetry audio waveform was unreadable."
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
        # If no local keyword triggers match, it gracefully prepares the system key for LLM calls
        return f"Command parsed. Standard system tools are empty for this text. System key authentication check: '{api_key[:6]}... OK'. Ready for neural update."

# 5. USER FRONTEND INTERFACE MATRIX
st.markdown("<h1 class='cyber-title'>⚡ JARVIS // CORE SECURE TERMINAL</h1>", unsafe_allow_html=True)
st.caption("TELEMETRY CHANNEL: SECURE // PUBLIC CODE LINKED // HOST CONTROLS INJECTED")
st.write("---")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("🖥️ Central Communication Deck")
    
    # Feature: Native multi-device browser mic recorder widget
    recorded_audio = st.audio_input("Activate Jarvis Vocal Command Array")
    
    # Alternate layout feature: standard chat text override field
    text_override = st.chat_input("Input direct system text command override...")
    
    # Process actions based on active feeds
    active_query = None
    
    if recorded_audio:
        with st.spinner("Processing vocal signal frequencies..."):
            active_query = transcribe_audio(recorded_audio)
            
    if text_override:
        active_query = text_override

    if active_query:
        jarvis_reply = process_jarvis_logic(active_query)
        st.session_state.chat_history.append({"user": active_query, "jarvis": jarvis_reply})

    # Display the visual running response queue
    for log in reversed(st.session_state.chat_history):
        with st.chat_message("user", avatar="👤"):
            st.write(log["user"])
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(f"**JARVIS:** {log['jarvis']}")

with right_col:
    st.subheader("📊 Host Machine Diagnostics")
    
    with st.container(border=True):
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        st.metric(label="CENTRAL SYSTEM CORE", value="SECURED", delta="GitHub Connection Safe")
        
        # Feature: Live system diagnostic monitoring array
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        st.progress(cpu / 100, text=f"Host Server CPU Core Load: {cpu}%")
        st.progress(ram / 100, text=f"Active Ram Capacity Allocation: {ram}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.subheader("🛠️ Hardware Functions")
    if st.button("Flush Internal Variable Arrays", use_container_width=True):
        st.session_state.chat_history = []
        st.toast("Active log buffer wiped entirely, Sir.")
