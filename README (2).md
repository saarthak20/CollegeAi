# 📚 CollegeAi – Your AI-Powered Learning Companion

CollegeAi is an all-in-one AI-powered educational platform that generates lectures, slides, professor scripts, flashcards, notes, quizzes, subtitles, and more – in multiple languages – to help students learn faster and smarter.

---

## 🎥 Demo Video
[![Watch the Demo](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://youtu.be/VIDEO_ID)  
*(Replace `VIDEO_ID` with your uploaded demo link)*

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

### 🗒 Notes Maker
- Generate concise or detailed notes from:
  - YouTube video
  - PDF
  - Manual text input
- Export as **Markdown, TXT, PDF**.

### 🃏 Flashcards Generator
- Create **AI-powered study flashcards** from any text, PDF, or YouTube content.
- Export flashcards in ready-to-use formats.

### ❓ Doubt Explaining Bot
- Ask any question from your study materials.
- AI explains in **clear, easy-to-understand** steps.
- Works in multiple languages.

### 📝 Quiz Generator *(Optional Extension)*
- Generate quizzes based on notes or lectures.
- MCQs and True/False format.

---

## 🛠 Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **Backend AI**: [Google Gemini 2.0 Flash](https://deepmind.google/technologies/gemini/)
- **Language Translation**: Gemini Multilingual
- **TTS**: Gemini Text-to-Speech
- **Video Processing**: `moviepy`, `Pillow`, `ffmpeg`
- **PDF Handling**: `PyMuPDF` (fitz), `reportlab`
- **File Conversion**: Markdown → PDF/TXT export
- **Vector Search (Optional)**: Pinecone

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/CollegeAi.git
cd CollegeAi
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set Up Google API Key
- Get your **Google Gemini API key** from [Google AI Studio](https://aistudio.google.com/).
- You can:
  - Set it in the UI on the home page (**recommended**), or
  - Export as an environment variable:
    ```bash
    export GOOGLE_API_KEY="your_api_key_here"
    ```

---

## ▶️ Running Locally
```bash
streamlit run app.py
```
Then open: [http://localhost:8501](http://localhost:8501)

---

## ☁️ Deployment
You can deploy CollegeAi on:
- **Streamlit Cloud**
- **Render**
- **Hugging Face Spaces**
- **Heroku**
- **Vercel (via Docker)**

---

## 📸 Screenshots

| Lecture Generator | Notes Maker | Flashcards |
|-------------------|-------------|------------|
| ![Lecture](screenshots/lecture.png) | ![Notes](screenshots/notes.png) | ![Flashcards](screenshots/flashcards.png) |

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss.

---

## 📜 License
MIT License – feel free to use and modify.

---

## ✨ Credits
Built with ❤️ by Saarthak and team for the **Hackathon Project**.
