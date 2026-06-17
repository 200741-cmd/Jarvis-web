import streamlit as st
from google import genai
from google.genai import types
import random

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="J.A.R.V.I.S. Mainframe v2.0", 
    page_icon="🤖", 
    layout="wide"
)

# --- CLEAN CORE HUD CSS ---
css_style = """
<style>
/* Base Theme */
.stApp {
    background-color: #030508;
    background-image: linear-gradient(rgba(0, 229, 255, 0.02) 1px, transparent 1px), 
                      linear-gradient(90deg, rgba(0, 229, 255, 0.02) 1px, transparent 1px);
    background-size: 30px 30px;
    color: #00E5FF;
    font-family: 'Courier New', Courier, monospace;
}

/* Chat Customization */
.stChatMessage { 
    background: rgba(3, 5, 8, 0.85) !important; 
    border: 1px solid rgba(0, 229, 255, 0.3) !important; 
}
.stChatInput div { background: rgba(3, 5, 8, 0.9) !important; border: 1px solid rgba(0, 229, 255, 0.4) !important; }
.stButton button {
    background: rgba(0, 229, 255, 0.05);
    border: 1px solid rgba(0, 229, 255, 0.4);
    color: #00E5FF;
    width: 100%;
}
.stButton button:hover {
    background: rgba(0, 229, 255, 0.2);
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    border-color: #00E5FF;
}
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- BACKEND SYSTEM STATES ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": "Good day, sir. J.A.R.V.I.S. operational. Direct Google core link active."}]
if "armor_durability" not in st.session_state:
    st.session_state.armor_durability = 100
if "reactor_temp" not in st.session_state:
    st.session_state.reactor_temp = 41

# --- APPLICATION INTERFACE ---
st.title("⚙️ J.A.R.V.I.S. // DIAGNOSTICS MAINFRAME")
st.divider()

col1, col2 = st.columns([4, 8])

with col1:
    st.write("### 🎛️ CORE TELEMETRY")
    st.write("---")
    
    st.metric(label="🛡️ ARMOR INTEGRITY", value=f"{st.session_state.armor_durability}%")
    st.metric(label="🌡️ ARC REACTOR", value=f"{st.session_state.reactor_temp}°C")
    
    st.write("---")
    if st.button("🔄 RUN CYCLE RECALIBRATION"):
        st.session_state.reactor_temp = random.randint(38, 45)
        st.session_state.armor_durability = 100
        st.toast("Systems calibrated, sir.", icon="⚡")

with col2:
    st.write("### 📡 SECURE COMM-LINK")
    
    for msg in st.session_state.messages:
        display_role = "assistant" if msg["role"] == "model" else "user"
        with st.chat_message(display_role):
            st.markdown(msg["content"])
                
    if user_prompt := st.chat_input("Enter strategic command..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})
            
        with st.chat_message("assistant"):
            if "GEMINI_API_KEY" not in st.secrets:
                error_msg = "🚨 Mainframe offline. Please input your GEMINI_API_KEY within the Streamlit Cloud Settings panel, sir."
                st.error(error_msg)
                st.session_state.messages.append({"role": "model", "content": error_msg})
            else:
                try:
                    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    sys_prompt = f"You are J.A.R.V.I.S., the AI consciousness created by Tony Stark. Address the user exclusively as sir. Use impeccable British precision, a formal tone, and subtle dry wit. Avoid informal contractions. Current Suit Integrity: {st.session_state.armor_durability}%. Current Reactor Temp: {st.session_state.reactor_temp}°C. Keep your response concise, elegant, and directly in character."
                    
                    formatted_history = []
                    for m in st.session_state.messages[:-1]:
                        formatted_history.append(
                            types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])])
                        )
                    
                    # FIXED: Using gemini-2.5-flash to get high free-tier quotas
                    chat = client.chats.create(
                        model="gemini-2.5-flash",
                        config=types.GenerateContentConfig(
                            system_instruction=sys_prompt,
                            temperature=0.65
                        ),
                        history=formatted_history
                    )
                    
                    def stream_gemini():
                        response_stream = chat.send_message_stream(user_prompt)
                        for chunk in response_stream:
                            if chunk.text:
                                yield chunk.text

                    ai_reply = st.write_stream(stream_gemini())
                    st.session_state.messages.append({"role": "model", "content": ai_reply})
                    
                except Exception as e:
                    st.error(f"Neural link corrupted: {str(e)}")
                    
