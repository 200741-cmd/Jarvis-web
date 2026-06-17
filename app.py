import streamlit as st
from groq import Groq
import random
import time
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="J.A.R.V.I.S. Mainframe", page_icon="🤖", layout="wide")

# --- IMPROVED CSS ---
css_style = """
<style>
.stApp { background-color: #030508; color: #00E5FF; font-family: 'Courier New', Courier, monospace; }
.suit-container { position: relative; width: 280px; height: 420px; margin: 20px auto; perspective: 1000px; }
.suit-hologram { width: 100%; height: 100%; position: relative; transform-style: preserve-3d; animation: suitRotate 15s linear infinite; }
@keyframes suitRotate { 0% { transform: rotateY(0deg); } 100% { transform: rotateY(360deg); } }
/* Ensure all suit parts are positioned correctly */
.suit-hologram div { position: absolute; background: rgba(0, 229, 255, 0.1); border: 1px solid rgba(0, 229, 255, 0.5); }
.suit-head { width: 60px; height: 70px; top: 0px; left: 110px; border-radius: 20px 20px 10px 10px; }
.suit-torso { width: 100px; height: 120px; top: 75px; left: 90px; border-radius: 10px; transform: translateZ(20px); }
.suit-reactor { width: 30px; height: 30px; top: 110px; left: 125px; border-radius: 50%; background: radial-gradient(circle, #00E5FF, transparent); box-shadow: 0 0 20px #00E5FF; transform: translateZ(25px); }
.suit-arm-l { width: 30px; height: 100px; top: 80px; left: 55px; transform: rotate(15deg); }
.suit-arm-r { width: 30px; height: 100px; top: 80px; left: 195px; transform: rotate(-15deg); }
.stChatMessage { background: rgba(0, 20, 30, 0.8); border: 1px solid #00E5FF; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "System online. Systems nominal, sir."}]
if "armor" not in st.session_state: st.session_state.armor = 100
if "temp" not in st.session_state: st.session_state.temp = 42

client = Groq(api_key=st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY")))

# --- UI LAYOUT ---
st.title("⚙️ J.A.R.V.I.S. // MAINFRAME")
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("""
    <div class="suit-container"><div class="suit-hologram">
    <div class="suit-head"></div><div class="suit-torso"></div>
    <div class="suit-reactor"></div><div class="suit-arm-l"></div><div class="suit-arm-r"></div>
    </div></div>
    """, unsafe_allow_html=True)
    st.metric("Armor Integrity", f"{st.session_state.armor}%")
    st.metric("Reactor Temp", f"{st.session_state.temp}°C")

with col2:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Command?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are J.A.R.V.I.S. British, formal, dry wit. Address user as sir."}, 
                          *st.session_state.messages],
                model="llama-3.3-70b-versatile",
                stream=True
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- LOGIC ---
if st.sidebar.button("Run Diagnostics"):
    st.session_state.temp = random.randint(35, 60)
    st.rerun()
