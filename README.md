#  Echo - AI Desktop Companion

Echo is a privacy-focused, context-aware AI desktop companion. Unlike traditional cloud-based chatbots, Echo runs locally on your machine, reads your active screen context to provide relevant commentary, and respects your focus by muting itself during games or media.

## Features
- **Context-Aware Vision:** Uses `pygetwindow` to read your active window and react naturally to what you are doing (e.g., coding, gaming, browsing).
- **"Read the Room" Mute Logic:** Automatically mutes her voice when you are playing games, watching movies, or listening to music.
- **Proactive Idle Chatter:** Initiates conversation when you've been quiet for a while, making her feel like a living presence.
- **Lightning-Fast Brain:** Powered by Groq's API (Llama 3 / GPT-OSS), ensuring responses in under 1 second.
- **Natural Voice:** Uses Microsoft Edge Neural TTS for a highly realistic, human-sounding female voice.
- **Invisible UI:** Runs as a lightweight, frameless overlay in your system tray.

## Tech Stack
- **Language:** Python 3.10+
- **UI Framework:** PyQt6
- **AI Backend:** Groq API (via `groq` library)
- **Speech-to-Text:** `SpeechRecognition` (Google Web API)
- **Text-to-Speech:** `edge-tts`
- **Screen Context:** `pygetwindow`

## Installation & Usage

### Option 1: Using the Executable (Windows)
1. Download `Echo.exe` from the Releases section.
2. Run `Echo.exe`. 
3. On the first run, it will create a `groq_key.txt` file. Open it, paste your free Groq API key (get one at [console.groq.com](https://console.groq.com/)), save, and restart the app.
4. Click the invisible window in the bottom right corner to focus it, and start talking!

### Option 2: Running from Source
1. Clone this repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt