# brovis_streamlit.py
import streamlit as st
import subprocess
import tempfile
import os
import time
from gtts import gTTS
from st_audiorec import st_audiorec


# --- PAGE CONFIG ---
st.set_page_config(page_title="BROVIS - JARVIS Edition", layout="centered")

# --- CSS Styling ---
st.markdown("""
<style>
body {
    background-color: #0a0a0f;
    color: #00ffc6;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 {
    color: #00ffc6;
    text-align: center;
}
.stTextInput>div>div>input, textarea {
    background-color: #141622 !important;
    color: #00ffc6 !important;
    border: 1px solid #00ffc6 !important;
}
.stButton>button {
    background: linear-gradient(90deg, #00ffc6, #00b4ff);
    color: #0a0a0f;
    border-radius: 10px;
    font-weight: bold;
    box-shadow: 0px 0px 15px #00ffc6;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #00b4ff, #00ffc6);
    box-shadow: 0px 0px 25px #00ffc6;
}
.chat-bubble {
    background: #141622;
    padding: 15px;
    border-radius: 15px;
    margin: 10px 0;
    color: #00ffc6;
    box-shadow: 0px 0px 8px #00ffc6;
}
.brovis-bubble {
    background: linear-gradient(145deg, #00ffc6, #00b4ff);
    color: #0a0a0f;
    padding: 15px;
    border-radius: 15px;
    margin: 10px 0;
    font-weight: 500;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown("<h1>🤖 BROVIS <span style='font-size:20px;'>(JARVIS Edition)</span></h1>", unsafe_allow_html=True)
st.caption("Your AI Voice Assistant — Powered by Mistral (Ollama) + Streamlit + gTTS")

# --- SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
st.sidebar.title("⚙️ Settings")
use_ollama = st.sidebar.checkbox("Use Ollama (Mistral)", value=True)
tts_language = st.sidebar.selectbox("Voice language", ["en", "hi"])
st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: You can type your question or upload a short audio file (.wav or .mp3).")

# --- UTILITIES ---
def query_ollama(prompt: str, timeout=30) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            encoding="utf-8",
        )
        out = result.stdout.strip()
        if out:
            return out
        if result.stderr:
            return f"(ollama stderr) {result.stderr.strip()}"
        return "(ollama returned empty response)"
    except FileNotFoundError:
        return "(ollama not found)"
    except subprocess.TimeoutExpired:
        return "(ollama timed out)"

def speak_and_play(text: str, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        tts.save(tmp.name)
        st.audio(tmp.name)
        time.sleep(1)
        try: os.unlink(tmp.name)
        except: pass
    except Exception as e:
        st.error(f"TTS error: {e}")

def transcribe_audio_file(uploaded_file) -> str:
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as f:
        f.write(uploaded_file.read())
        tmp_path = f.name
    try:
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return text
    except Exception as e:
        return f"(Audio error: {e})"
    finally:
        try: os.unlink(tmp_path)
        except: pass

# --- MAIN UI ---
st.markdown("### 💬 Talk to BROVIS")
user_input = st.text_area("Type your command or message:", placeholder="Example: What's the weather today?", height=120)
uploaded_audio = st.file_uploader("🎙️ Or upload your voice (WAV or MP3)", type=["wav","mp3","m4a","ogg"])
send = st.button("🚀 Ask BROVIS")

# --- CHAT OUTPUT ---
if send:
    query = user_input.strip()
    if not query and uploaded_audio:
        with st.spinner("🎧 Transcribing your voice..."):
            query = transcribe_audio_file(uploaded_audio)
            if "(Audio error" in query:
                st.error(query)
                query = ""
            else:
                st.success(f"🎙️ You said: {query}")

    if not query:
        st.warning("Please type or upload a message first.")
    else:
        st.markdown(f"<div class='chat-bubble'><b>You:</b> {query}</div>", unsafe_allow_html=True)
        with st.spinner("🤖 BROVIS is thinking..."):
            response = ""
            if use_ollama:
                result = query_ollama(query)
                if "(ollama not found" not in result:
                    response = result
                else:
                    st.info(result)
            if not response:
                response = f"I heard: '{query}'. (Ollama not active — using fallback.)"

        st.markdown(f"<div class='brovis-bubble'><b>BROVIS:</b> {response}</div>", unsafe_allow_html=True)
        speak_and_play(response, lang=tts_language)

# --- FOOTER ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffc6;'>⚡ BROVIS - Created by Ayush (ayu-haker) | Powered by Streamlit & Mistral ⚡</p>", unsafe_allow_html=True)
