import streamlit as st
import random
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="J.A.R.V.I.S. // Interface", page_icon="🤖", layout="wide")

# --- ADVANCED HOLOGRAM CSS ---
css_style = """
<style>
.stApp { background-color: #030508; color: #00E5FF; }

/* Hologram Field */
.field { perspective: 1000px; width: 300px; height: 400px; margin: auto; }
.suit { position: relative; width: 100%; height: 100%; transform-style: preserve-3d; animation: spin 20s infinite linear; }
@keyframes spin { from { transform: rotateY(0deg); } to { transform: rotateY(360deg); } }

/* Hologram Components */
.suit div { position: absolute; border: 1px solid #00E5FF; background: rgba(0, 229, 255, 0.05); }
.head { width: 50px; height: 60px; left: 125px; border-radius: 50% 50% 10% 10%; }
.chest { width: 100px; height: 120px; top: 65px; left: 100px; clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%); }
.arc { width: 30px; height: 30px; top: 100px; left: 135px; border-radius: 50%; background: radial-gradient(#00E5FF, transparent); box-shadow: 0 0 20px #00E5FF; }
.arm { width: 30px; height: 100px; top: 70px; }
.left { left: 60px; transform: rotate(15deg); }
.right { left: 210px; transform: rotate(-15deg); }

/* Data HUD Overlay */
.hud-text { font-family: 'Courier New', monospace; font-size: 10px; color: #00E5FF; text-transform: uppercase; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- UI LAYOUT ---
st.title("⚙️ J.A.R.V.I.S. // MAINFRAME")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("""
    <div class="field">
        <div class="suit">
            <div class="head"></div>
            <div class="chest"></div>
            <div class="arc"></div>
            <div class="arm left"></div>
            <div class="arm right"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.metric("System Core", "STABLE", delta="0.04%")
    if st.button("RECALIBRATE SENSORS"):
        st.toast("Recalibrating...", icon="🔄")

with col2:
    st.subheader("System Telemetry")
    chat_container = st.container(height=400)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Diagnostics complete, sir. Systems are at 100% efficiency."}]
    
    for msg in st.session_state.messages:
        with chat_container.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Input command..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)
        
        # Simulated response
        reply = "Processing request via localized neural link, sir."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        chat_container.chat_message("assistant").markdown(reply)
