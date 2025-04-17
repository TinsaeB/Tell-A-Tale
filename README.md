# Tell-A-Tale: AI Story Generator & Narrator

Tell-A-Tale is an interactive desktop web application that lets you generate, narrate, save, and share fictional tales using a local LLM (Ollama) and text-to-speech engines. It provides a modern, user-friendly interface with advanced sharing and narration options.

---

## Features

- **Generate Tales**: Create imaginative stories in various styles (Biblical, Historical, Fun Facts, etc.) using your locally running Ollama LLM (e.g., phi4).
- **Narrate with AI Voices**: Listen to tales with either offline (pyttsx3) or human-like (Edge TTS) narration. Choose your preferred voice for each mode.
- **Save & Download**: Download tales as `.txt`, audio as `.mp3`, or both as a `.zip` archive.
- **Share Easily**: Share tales via WhatsApp, Telegram, or Email with one click. Copy tales to clipboard for use anywhere.
- **Modern UI**: Clean, tabbed interface for generation and narration/sharing, with clear instructions and helpful tooltips.

---

## Requirements

- **Python 3.8+** (recommended Python 3.10+)
- **Ollama** (running locally with your preferred LLM, e.g., phi4)
- **Microsoft Edge TTS** (for human-like voices)
- **Internet connection** (for sharing features)

> **No external database required. All data is stored locally in `tell_a_tale.db` using SQLite.**

### Python Dependencies
- See `requirements.txt` for all required Python packages:
  - `streamlit`, `requests`, `pyttsx3`, `edge-tts`, `pyperclip`

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Tell-A-Tale
```

### 2. (Recommended) Create and Activate a Virtual Environment
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# OR Windows CMD:
.venv\Scripts\activate.bat
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Ollama
- Download and install [Ollama](https://ollama.com/).
- Start Ollama and pull your desired model (e.g., phi4):
  ```bash
  ollama pull phi4
  ollama serve
  ```
- By default, the app connects to `http://localhost:11434`.

### 5. Run the App
```bash
streamlit run app.py
```
- The app will open in your browser at [http://localhost:8501](http://localhost:8501).

---

## Usage Guide

### Saving and Managing Tales

Tales and their narrations are saved to a local SQLite database (`tell_a_tale.db`).

- Use the sidebar to **view, search, filter, edit, delete, and play/download** any saved tale.
- No setup or extra database required—everything works out of the box.
- Choose narration type (offline or Edge TTS) and select a voice.
- Click **Generate Tale**. The story will appear in the preview.

### 2. Narration & Save/Share Tab
- Click **Narrate Tale** to generate audio.
- Use the audio player to listen.
- Download the text, audio, or both as a ZIP.
- Share the tale via WhatsApp, Telegram, or Email with one click.
- Copy the tale to your clipboard for use anywhere.

---

## Customization
- **Add More Voices**: Edit `edge_voices.py` to add more Edge TTS voices.
- **Change Tale Types**: Update the tale type options in `app.py`.
- **Enhance Sharing**: Add more platforms or integrations as needed.

---

## Troubleshooting
- **Ollama Not Running**: Ensure `ollama serve` is active and the model is pulled.
- **ModuleNotFoundError**: Double-check that your virtual environment is activated and all dependencies are installed.
- **Audio Issues**: Some TTS voices may not be available on all systems. Try different voices if you encounter errors.
- **Sharing Not Working**: Ensure you have an active internet connection.

---

## Credits
- Built with [Streamlit](https://streamlit.io/), [Ollama](https://ollama.com/), [pyttsx3](https://pyttsx3.readthedocs.io/), [edge-tts](https://github.com/ranyelhousieny/edge-tts), and open-source inspiration.

---

## License
This project is for personal and educational use. See `LICENSE` for details.
