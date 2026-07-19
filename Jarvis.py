import streamlit as st
import speech_recognition as sr
import pyttsx3
import datetime
import psutil
import io
from google import genai

# --- VOICE ENGINE INITIALIZATION ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        return r.recognize_google(audio).lower()
    except:
        return "None"

# --- UI LOGIC (Insert your existing process_jarvis_logic here) ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- UPDATED UI SECTION ---
st.markdown("<div class='header'>A.R.C. Core Neural Interface</div>", unsafe_allow_html=True)

# ... (Include your previous CSS styles here) ...

# VOICE ACTIVATION BUTTON
if st.button("🎙️ ACTIVATE NEURAL LINK (VOICE)"):
    st.session_state.voice_feed = "LISTENING..."
    query = listen_command()
    
    if query != "None":
        st.session_state.voice_feed = f"HEARD: {query}"
        
        # Process command
        response = process_jarvis_logic(query)
        st.session_state.chat_history.append({"user": query, "jarvis": response})
        
        # Speak response
        speak(response)
        st.rerun()
    else:
        st.session_state.voice_feed = "SIGNAL LOST"

# DISPLAY CHAT HISTORY
for log in reversed(st.session_state.chat_history):
    st.markdown(f"**YOU:** {log['user']}")
    st.markdown(f"**JARVIS:** {log['jarvis']}")
