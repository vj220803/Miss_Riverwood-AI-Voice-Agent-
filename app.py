import os
import json
import datetime
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs import ElevenLabs
from audio_recorder_streamlit import audio_recorder

# ====================================================
# CUSTOM DARK THEME + BETTER BUTTONS + CLEAN UI
# ====================================================
st.markdown("""
    <style>
        /* Whole App Background */
        .stApp {
            background-color: #0d1117;
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Titles */
        h1, h2, h3, h4, h5 {
            color: #58a6ff !important;
        }

        /* Regular Text */
        p, label, span {
            color: #c9d1d9 !important;
        }

        /* Input Box Style */
        input {
            background-color: #161b22 !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            border: 1px solid #30363d !important;
            padding: 10px !important;
        }

        /* Make Buttons Attractive */
        .stButton>button {
            background-color: #238636;
            color: white;
            padding: 0.7rem 1.2rem;
            border-radius: 10px;
            border: none;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #2ea043;
            border: 1px solid #3fb950;
        }

        /* Audio Recorder Button Style */
        button[kind="primary"] {
            background-color: #1f6feb !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0.8rem 1.4rem !important;
            font-size: 1rem !important;
        }

        /* Make Columns Spacing Nice */
        .block-container {
            padding-top: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        /* Divider Color */
        hr {
            border: 1px solid #30363d !important;
        }

        /* Memory JSON Box */
        .stJson {
            background-color: #161b22 !important;
            padding: 15px !important;
            border-radius: 10px !important;
        }
    </style>
""", unsafe_allow_html=True)


# =========================
# 0) Setup & keys
# =========================
st.set_page_config(page_title="Miss Riverwood – Voice Agent", page_icon="🎙️", layout="centered")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "")

# SDK clients (created even if keys missing; we guard calls below)
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
tts_client = ElevenLabs(api_key=ELEVEN_API_KEY) if ELEVEN_API_KEY else None

# =========================
# 1) Memory helpers
# =========================
MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"name": None, "preferences": None, "last_visit": None}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# =========================
# 2) Data helpers
# =========================
def read_crm():
    if os.path.exists("crm.csv"):
        df = pd.read_csv("crm.csv")
        return df.to_dict(orient="records")
    return []

def today_update():
    today = datetime.date.today().strftime("%d %B %Y")
    return (
        f"Today's Update ({today}):\n"
        "• Internal roads: 90% complete\n"
        "• Clubhouse foundation: completed\n"
        "• Landscaping work: in progress\n"
        "• Electrical trenching: ~40%\n"
    )

# =========================
# 3) Utility: detect quota/credit issues
# =========================
def is_quota_error(e: Exception | str) -> bool:
    s = str(e).lower()
    return ("insufficient_quota" in s) or ("quota" in s and "exceeded" in s) or ("429" in s and "quota" in s)

# =========================
# 4) STT (OpenAI Whisper) with guard
# =========================
def transcribe_wav_bytes(wav_bytes: bytes) -> str:
    if not client or not OPENAI_API_KEY:
        return "[STT ERROR] OpenAI key missing. Add OPENAI_API_KEY in .env"
    try:
        tmp = "temp_input.wav"
        with open(tmp, "wb") as f:
            f.write(wav_bytes)
        with open(tmp, "rb") as f:
            r = client.audio.transcriptions.create(model="gpt-4o-mini-transcribe", file=f)
        return r.text.strip()
    except Exception as e:
        if is_quota_error(e):
            return "[STT ERROR] insufficient_quota"
        return f"[STT ERROR] {e}"

# =========================
# 5) LLM reply with graceful fallback
# =========================
def llm_reply(user_text: str, memory: dict, crm_data: list) -> str:
    system_prompt = f"""
You are Miss Riverwood — a warm, bilingual (Hindi+English) AI voice agent for Riverwood Projects LLP.

STYLE:
- Short, friendly (8–12 seconds), Hinglish (natural mix)
- Polite, sales-exec vibe; add light bonding (“chai pee li?”)
- Use memory if available (name, preferences, last_visit).
- If asked about construction, use the update below.

CONSTRUCTION UPDATE:
{today_update()}

MEMORY:
{memory}
""".strip()

    if not client or not OPENAI_API_KEY:
        # Fallback copy when no key present at all
        return (
            "Namaste! Main Miss Riverwood bol rahi hoon. Abhi mere paas OpenAI credits/key nahi hai, "
            "isliye main live reply generate nahi kar paa rahi. Kindly API credits add kijiye, "
            "tab main aapko Hinglish mein proper jawab dungi. Filhaal aaj ka update: "
            "internal roads 90% complete, clubhouse foundation done, landscaping in progress, "
            "aur electrical trenching ~40% hai. 😊"
        )

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            max_tokens=220,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Polite fallback message on quota
        if is_quota_error(e):
            return (
                "Namaste! 👋 Main Miss Riverwood hoon. Aapki request mili, "
                "par abhi OpenAI credits khatam ho gaye hain (insufficient quota). "
                "Jab tak credits add nahi hote, main aapko short update batati hoon: "
                "internal roads 90% complete, clubhouse foundation done, landscaping in progress, "
                "aur electrical trenching ~40% hai. Aap chaahein toh apna naam aur plot preference "
                "type karke bhej sakte hain — main use memory mein save kar dungi. 🙂"
            )
        return f"[GPT ERROR] {e}"

# =========================
# 6) TTS (optional) with guard
# =========================
VOICE_ID = "OuMzFHdSH2X2F1osLEcJ"

def speak(text: str) -> bytes | None:
    if not tts_client or not ELEVEN_API_KEY:
        return None
    try:
        return tts_client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
        )
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# =========================
# 7) UI
# =========================
st.title("🎙️ Miss Riverwood – AI Voice Agent (Push-to-Talk)")
st.caption("Record → Stop → Transcribe → Reply → Play Voice")

# 🔔 Greeting on load (once)
DEFAULT_GREETING = (
    "Namaste! Main Miss Riverwood hoon. Hinglish mein baat kijiye — main aapko daily construction "
    "updates aur project details bataungi. Aapka naam bhi yaad rakhungi! Chaliye, shuru karein? 😊"
)
if "last_reply" not in st.session_state or not st.session_state["last_reply"]:
    st.session_state["last_reply"] = DEFAULT_GREETING

# Key warnings
if not OPENAI_API_KEY:
    st.warning("OpenAI key missing. Add **OPENAI_API_KEY** in your `.env` file.", icon="⚠️")
if not ELEVEN_API_KEY:
    st.info("ElevenLabs key missing. Voice playback will be disabled.", icon="ℹ️")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 1) Record Voice")
    audio_bytes = audio_recorder(
        text="🎤 Record / Stop",
        recording_color="#ff4b4b",
        neutral_color="#0066cc",
        icon_size="2x",
    )
    if audio_bytes:
        st.success("✅ Audio recorded successfully!")

with col2:
    st.markdown("### 2) Or Type Message")
    typed = st.text_input("Type here (optional)")

st.divider()

if st.button("📝 Transcribe & Reply"):
    # Priority: voice → else typed
    if audio_bytes:
        user_text = transcribe_wav_bytes(audio_bytes)
        if user_text == "[STT ERROR] insufficient_quota":
            st.error("❌ OpenAI STT quota exhausted. Try typed message or add credits.")
            st.stop()
        elif user_text.startswith("[STT ERROR]"):
            st.error(user_text)
            st.stop()
        else:
            st.success(f"🗣️ You said: {user_text}")
    elif typed.strip():
        user_text = typed.strip()
        st.info(f"⌨️ You typed: {user_text}")
    else:
        st.warning("Please record audio OR type a message first.")
        st.stop()

    memory = load_memory()
    crm_data = read_crm()

    reply = llm_reply(user_text, memory, crm_data)
    st.session_state["last_reply"] = reply

    # Memory capture (simple)
    lower = user_text.lower()
    if "name is" in lower or "mera naam" in lower:
        # naive parsing
        try:
            memory["name"] = user_text.split("is")[-1].strip()
        except Exception:
            pass
    if any(k in lower for k in ["plot", "sq", "square", "corner", "facing"]):
        memory["preferences"] = user_text
    memory["last_visit"] = str(datetime.date.today())
    save_memory(memory)

# Reply panel
st.subheader("💬 Miss Riverwood says:")
st.write(st.session_state["last_reply"])

# Play voice (if TTS key available)
if st.session_state["last_reply"]:
    if st.button("🔊 Play Voice Reply"):
        audio_file = speak(st.session_state["last_reply"])
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
        else:
            st.info("Voice playback unavailable (missing or invalid ElevenLabs key).")

# Debug / memory
st.divider()
st.subheader("🧠 Memory (debug)")
st.json(load_memory())
