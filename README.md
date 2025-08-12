# 📚 CollegeAi – Your AI-Powered Learning Companion

CollegeAi is an all-in-one AI-powered educational platform that generates lectures, slides, professor scripts, flashcards, notes, quizzes, subtitles, and more – in multiple languages – to help students learn faster and smarter.


---

## 🎥 Demo Video
[![Watch the Demo](https://img.youtube.com/vi/WkI2gbuy4fs/0.jpg)](https://youtu.be/WkI2gbuy4fs)  


---

## 🚀 Features

### 🖼 Lecture Generator
- Extracts context from **YouTube videos** or **uploaded PDFs**.
- Summarizes content with **Google Gemini AI**.
- Generates **slides** in multiple themes:
  - Light Blue
  - Dark
  - Pastel
  - Minimal Monochrome
- Creates **professor scripts** (with different teaching styles).
- Translates scripts into **10+ languages** (with "Other" custom input).
- Generates **TTS narration** using Gemini voices.
- Creates a **video lecture** with slides + narration.
- Adds **subtitles** to videos.
- Downloads available for **slides, PDF, audio, video**.

  ### 📝 Quiz Generator 
- Generate quizzes based on notes or lectures.
- Gives multiple export formats
- Moodle XML supported
- Time Mode and Revision Mode available

### 🗒 Notes Maker
- Generate concise or detailed notes from:
  - YouTube video
  - PDF
  - Manual text input
- Export as **Markdown, TXT, PDF**.

### 🃏 Flashcards Generator
- Create **AI-powered study flashcards** from any text, PDF, or YouTube content.
- Export flashcards in ready-to-use formats.


---

## 🛠 Tech Stack

- **Frontend/UI**: [Streamlit]
- **Backend AI**: [Google Gemini 2.0 Flash]
- **Language Translation**: Gemini Multilingual
- **TTS**: Gemini Text-to-Speech
- **Video Processing**: `moviepy`, `Pillow`, `ffmpeg`
- **PDF Handling**: `PyMuPDF` (fitz), `reportlab`
- **File Conversion**: Markdown → PDF/TXT export

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/saarthak20/CollegeAi.git
cd Lecture
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Running Locally
```bash
streamlit run app.py
```
Then open: [http://localhost:8501](http://localhost:8501)

---

## ✨ Credits
Built with by Saarthak for the **Zense submission**.
