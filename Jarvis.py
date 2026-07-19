import streamlit as st
import speech_recognition as sr
import datetime
import wikipedia
import psutil
import io
from google import genai

# --- PAGE SETUP ---
st.set_page_config(page_title="A.R.C. Core Neural Interface", layout="wide")

# --- CORE LOGIC (Keep your existing functions) ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "mode" not in st.session_state: st.session_state.mode = "IDLE"

def process_jarvis_logic(query):
    # Your existing process_jarvis_logic code here
    return "Command Processed"

# --- THE INTERFACE (Matches your screenshot) ---
st.markdown("""
<style>
    body { background-color: #0b0b0d; color: #fff; font-family: 'Segoe UI', sans-serif; }
    .ui-container { background: #0b0b0d; padding: 20px; border: 1px solid #333; }
    .header { font-size: 24px; margin-bottom: 20px; }
    .grid-container { display: grid; grid-template-columns: 200px 1fr 200px; gap: 20px; align-items: center; }
    .terminal { font-family: monospace; font-size: 12px; color: #00e5ff; background: rgba(0,0,0,0.5); padding: 10px; border: 1px solid #222; }
    .arc-reactor { text-align: center; border: 2px dashed #00e5ff; border-radius: 50%; width: 150px; height: 150px; margin: 0 auto; display: flex; align-items: center; justify-content: center; }
    .stats-row { display: flex; justify-content: space-around; margin-top: 30px; border-top: 1px solid #333; padding-top: 20px; }
    .control-bar { background: #1a1a1a; padding: 15px; margin-top: 20px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
</style>
""", unsafe_allow_html=True)

# UI RENDER
st.markdown("<div class='header'>A.R.C. Core Neural Interface</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown("<div class='terminal'>> BUFFERING STREAM 0x442<br>> UPDATING HEURISTICS<br>> VOLTAGE STABILIZED</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div style='text-align:center;'><strong>MODE: IDLE</strong></div>", unsafe_allow_html=True)
    st.markdown("<div class='arc-reactor'>[ CORE ]</div>", unsafe_allow_html=True)

with col3:
    st.write("CPU LOAD")
    st.progress(psutil.cpu_percent() / 100)
    st.write("MEM ALLOC")
    st.progress(psutil.virtual_memory().percent / 100)
    st.write("CORE TEMP")
    st.progress(0.31) # Simulated temp

# BOTTOM STATS
st.markdown(f"""
<div class='stats-row'>
    <div>CPU LOAD<br><strong>{psutil.cpu_percent()}%</strong></div>
    <div>MEMORY<br><strong>{psutil.virtual_memory().percent}%</strong></div>
    <div>CORE TEMP<br><strong>31°C</strong></div>
</div>
""", unsafe_allow_html=True)

# CONTROL BAR
st.markdown("<div class='control-bar'><span>System Mode</span><span>IDLE</span><span>></span></div>", unsafe_allow_html=True)

# INPUT AREA
user_input = st.chat_input("Command...")
if user_input:
    # Handle logic here
    st.rerun()
