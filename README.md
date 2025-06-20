# 🎙️ Narrator Studio

**Narrator Studio** is a user-friendly voiceover tool — designed for Python 3.11 — that lets you convert written text into professional-sounding speech – with background music, customizable pauses, fade effects, and much more.

---

## ✨ Features

- ✅ Convert text to speech using Edge TTS (Polish AI voices like Marek and Zofia)
- ✅ Add customizable pauses in seconds with `{pause=3}` notation
- ✅ Adjust speech tempo (-30% to +30%)
- ✅ Select and loop background music
- ✅ Apply fade in/out to music
- ✅ Delay speech start and extend background after speech ends
- ✅ Adjust background volume (0–150%)
- ✅ Work with multiple text fragments (1 text fragment = max 2500 characters)
- ✅ Save and preview individual parts or final audio
- ✅ Built with a clean, modern GUI using CustomTkinter

---

## 📁 Folder Structure

```
Narrator-Studio/
├── main.py                  # Main application
├── .env                     # Your local FFmpeg path (not included in repo)
├── requirements.txt         # All required Python libraries
├── README.md
├── backgrounds/             # Add your background .mp3 files here
├── fragments/               # Temporary voiceover parts (auto-created)
├── output/                  # Final merged audio files
```

---

## ⚙️ Setup Instructions

> ❗ Narrator Studio requires **Python 3.11**  
> Other versions (e.g. 3.12) may not work due to compatibility with `pydub` and `edge-tts`.


### 1. Clone the repo

```bash
git clone https://github.com/your-username/Narrator-Studio.git
cd Narrator-Studio
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate      # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add `.env` file

Create a file named `.env` and add your local path to FFmpeg:

```env
FFMPEG_PATH=C:\\ffmpeg\\bin\\ffmpeg.exe
```

Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/

---

## 🚀 How to Run

```bash
python main.py
```

---

## 🎧 Tips

- Add a pause using `{pause=3}` to insert a 3-second silence.
- Select a background track or leave it empty.
- Use multiple fragments to organize complex scripts.
- You can overwrite and re-save fragments at any time.
- Use different voices and compare results in real-time.

---

## 📦 Dependencies

- `customtkinter`
- `pygame`
- `pydub`
- `edge-tts`
- `python-dotenv`

---

## 📄 License

MIT – feel free to use, modify, and share.

---

Made with ❤️ by czekaj-no, powered by Python.
