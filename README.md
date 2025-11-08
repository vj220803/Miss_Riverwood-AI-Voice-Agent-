# Miss_Riverwood-AI-Voice-Agent-

# 🎙️ Miss Riverwood – AI Voice Agent (Hinglish Sales Assistant)

An advanced, interactive **Push-to-Talk Voice Agent** built using Streamlit, OpenAI, and ElevenLabs.  
The assistant speaks natural **Hinglish**, remembers past details, gives **daily construction updates**, and responds like a real sales executive.

This system demonstrates how **AI + Voice + Memory** can transform real estate customer engagement.

---
## 📊 Project Architecture Flowchart

![Architecture Flowchart]()

---

# ✅ Why We Avoided Other Tools

The assignment mentioned tools like:  
**Play.ht, Twilio Voice, LangChain, Vocode, JS, Node.js, Replit**

We intentionally **did NOT use them**, because:

### ❌ Play.ht
- Paid only  
- Latency issues  
- No reliable free-tier for student projects  

### ❌ Twilio Voice
- Requires public HTTPS URLs  
- Expensive  
- Complicated call routing  
- Overkill for a simple voice agent  

### ❌ LangChain / Vocode
- Heavy frameworks  
- Adds unnecessary complexity  
- Our app requires full custom control instead  

### ❌ Node.js / Replit / JS
- Streamlit already handles UI + interactivity  
- Python gives direct access to OpenAI + ElevenLabs  
- Simpler for demo and oral examination  

✅ Using **pure Python + Streamlit** makes the project cleaner, easier to evaluate, and more reliable.

---

# ✅ What Technologies We Used & Why

### ✅ **Streamlit**
- Front-end UI  
- Easy to create interactive voice interface  
- Supports state, theming, styling  
- Speeds up development dramatically  

### ✅ **audio_recorder_streamlit**
- Works flawlessly across browsers  
- No WebRTC issues  
- Lightweight and stable  
- Perfect for recording WAV bytes for Whisper  

### ✅ **OpenAI Whisper (STT)**
- Converts speech → text  
- Accurate for Indian accents  
- Faster & easier than Google Speech or DeepSpeech  

### ✅ **OpenAI GPT (LLM Brain)**
- Generates Hinglish conversational replies  
- Can blend sales tone and emotional tone  
- Works with our memory system  

### ✅ **ElevenLabs TTS**
- Converts text → natural lifelike voice  
- Best Indian-accent output among all TTS services  

### ✅ **Local memory.json**
- Stores:
  - user name  
  - preferences  
  - last visit  
- Simulates a CRM  
- Makes conversations feel personal  

### ✅ **crm.csv (optional)**
- If present, enriches conversation using customer data  

---

# ✅ How the Construction Updates Work

The project uses a **function** to simulate daily updates:

```python
def today_update():
    today = datetime.date.today().strftime("%d %B %Y")
    return (
        f"Today's Update ({today}):\n"
        "• Internal roads: 90% complete\n"
        "• Clubhouse foundation: completed\n"
        "• Landscaping work: in progress\n"
        "• Electrical trenching: ~40%\n"
    )
```

✅ The date updates automatically  
✅ The content is pre-written (no database needed)  
✅ This method is common in prototyping demos  

---

# ✅ System Architecture

```
 ┌──────────────────────────────────────────┐
 │             STREAMLIT UI                 │
 │  - Dark theme                            │
 │  - Record Button                         │
 │  - Text Input                            │
 │  - Play Voice Button                     │
 └──────────────────────────────────────────┘
                     │
                     ▼
 ┌──────────────────────────────────────────┐
 │     Audio Recorder Streamlit             │
 │  Captures mic input → WAV bytes          │
 └──────────────────────────────────────────┘
                     │
                     ▼
 ┌──────────────────────────────────────────┐
 │         OPENAI WHISPER (STT)             │
 │ Converts audio → text                    │
 └──────────────────────────────────────────┘
                     │ user_text
                     ▼
 ┌──────────────────────────────────────────┐
 │              GPT Reply                   │
 │  Hinglish Sales Agent Prompt             │
 │  Memory-Aware Response                   │
 └──────────────────────────────────────────┘
                     │ reply_text
                     ▼
 ┌──────────────────────────────────────────┐
 │          ELEVENLABS TTS                  │
 │ Converts text → natural voice            │
 └──────────────────────────────────────────┘
                     │ audio
                     ▼
 ┌──────────────────────────────────────────┐
 │          STREAMLIT AUDIO PLAYER          │
 └──────────────────────────────────────────┘
```

---

# ✅ Project Structure

```
riverwood-voice-agent/
│
├── app.py                # Main application
├── requirements.txt      # Dependencies
├── .env.example          # Sample environment variables
├── memory.json           # AI memory store
├── crm.csv (optional)    # Customer records
└── README.md             # Documentation
```

---

# ✅ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-user>/riverwood-voice-agent.git
cd riverwood-voice-agent
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install --no-cache-dir -r requirements.txt
```

### 4️⃣ Add Environment Variables
Create a file **.env**:

```
OPENAI_API_KEY=your_openai_api_key_here
ELEVEN_API_KEY=your_elevenlabs_api_key_here
```

---

# ✅ Running the Application

```bash
streamlit run app.py
```

---

# ✅ Earlier Attempts & Why We Changed (Important Section)

### ✅ **Attempt 1: WebRTC microphone (streamlit-webrtc)**
Problems faced:
- Required PyAudio (not installable on Python 3.11)  
- WebRTC handshake kept failing  
- STUN/TURN server errors  
- Browser mic permissions unstable  
- High latency  

✅ Replaced with **audio_recorder_streamlit**  
- Works everywhere  
- Lightweight  
- No WebRTC dependencies  
- Perfect for demos  

### ✅ **Attempt 2: Node.js + Vocode + LangChain**
Problems faced:
- Heavy frameworks  
- Harder to deploy  
- More bugs  
- Not required for this voice agent  

✅ Switched to **pure Python**  
- Faster  
- Easier to debug  
- More reliable for evaluation  

---

# ✅ requirements.txt

```
streamlit==1.51.0
python-dotenv
openai==1.55.3
elevenlabs==1.11.0
audio-recorder-streamlit==0.1.2
pandas
```

---

# ✅ .env.example

```
OPENAI_API_KEY=
ELEVEN_API_KEY=
```

---

# ✅ Known Issues

| Issue | Reason | Solution |
|-------|--------|----------|
| 429 quota error | OpenAI free credits exhausted | Use new key or paid plan |
| No voice playback | ElevenLabs key missing | Add ELEVEN_API_KEY |
| Mic stops after 2 seconds | Normal behavior of audio_recorder | Click again to record |

---

# ✅ How to Present This Project (Loom Script)

**Intro:**  
“Hello, this is my AI-powered project called *Miss Riverwood Voice Agent*.”

**Technology:**  
- Streamlit UI  
- OpenAI Whisper  
- GPT for Hinglish replies  
- ElevenLabs for speech  
- JSON memory system  

**Demo:**  
1. Click Record  
2. Speak  
3. Transcribe  
4. AI replies  
5. Click Play to hear voice output  

**End:**  
“This system shows how AI voice assistants can enhance customer engagement in real estate.”

---

# ✅ Future Enhancements

✅ Real-time database for construction updates  
✅ Full CRM integration  
✅ Phone-call mode using Twilio  
✅ WhatsApp bot version  
✅ Dashboard for conversation analytics  

---

# ✅ Author  
**Vijayan Naidu**

---

