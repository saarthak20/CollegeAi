
import streamlit as st
import os
from extractor import extract_pdf_text, extract_youtube_transcript, summarize_text
from script import generate_slide_content, generate_professor_script
from slides import generate_slides_from_markdown
from TTS import generate_tts_per_slide
from advance import generate_advanced_synced_video
from video import convert_pptx_to_pdf, convert_pdf_to_images

st.set_page_config(page_title="CollegeAi", layout="centered")

def homepage():
    st.title("🎓 Welcome to CollegeAi")
    st.markdown(
        "An AI-powered tool to auto-generate **lectures, slides, voiceovers, and videos** from YouTube or PDF notes. "
        "Just enter a topic and let the magic happen!"
    )
    st.markdown("---")
    st.subheader("🚀 Get Started")
    st.write("Go to the **Lecture Generator** tab to begin!")

def lecture_generator():
    st.title("📚 Lecture Generator")

    topic = st.text_input("Enter Topic", "")
    input_source = st.radio("Choose context source", ["None", "YouTube Video", "PDF Notes"])
    context = ""

    if input_source == "YouTube Video":
        url = st.text_input("Enter YouTube URL")
        if url:
            with st.spinner("Extracting and summarizing transcript..."):
                transcript = extract_youtube_transcript(url)
                context = summarize_text(transcript, topic)
    elif input_source == "PDF Notes":
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
        if pdf_file:
            with st.spinner("Extracting and summarizing PDF content..."):
                text = extract_pdf_text(pdf_file)
                context = summarize_text(text, topic)

    length = st.selectbox("Lecture Length", ["Short (Revision)", "Detailed", "Coursework"])
    language = st.selectbox("Language", ["English", "Hindi", "Kannada", "German", "French", "Japanese", "Spanish", "Tamil", "Telugu", "Malayalam", "Chinese", "Other"])
    if language == "Other":
        language = st.text_input("Enter your language")

    persona = st.selectbox("Professor Persona", ["Enthusiastic", "Calm Mentor", "Friendly Senior", "Strict Examiner"])
    persona_map = {
        "Enthusiastic": ("enthusiastic professor", "Kore"),
        "Calm Mentor": ("calm and clear mentor", "Aoede"),
        "Friendly Senior": ("friendly senior explaining with stories", "Puck"),
        "Strict Examiner": ("strict examiner, focused and concise", "Charon"),
    }

    theme = st.selectbox("Slide Theme", ["1 - Light Blue", "2 - Dark", "3 - Pastel", "4 - Minimal Monochrome"])
    theme_choice = theme.split(" ")[0]

    if st.button("🎬 Generate Lecture"):
        if not topic:
            st.warning("Please enter a topic.")
            return

        with st.spinner("Generating slide content..."):
            slide_md = generate_slide_content(topic, length, context=context, language=language)
            slide_md_file = f"Lecture_{topic.replace(' ', '_')}.md"
            with open(slide_md_file, "w", encoding="utf-8") as f:
                f.write(slide_md)

        with st.spinner("Generating professor script..."):
            persona_text, voice = persona_map[persona]
            script = generate_professor_script(topic, slide_md, persona_text, context, language)
            script_file = slide_md_file.replace(".md", f"_{language}_ProfessorScript.md")
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(script)

        with st.spinner("Generating slides..."):
            generate_slides_from_markdown(slide_md_file, theme_choice=theme_choice)

        pptx_path = slide_md_file.replace("Lecture", "Slides").replace(".md", ".pptx")

        with st.spinner("Converting to images..."):
            pdf_path = convert_pptx_to_pdf(pptx_path)
            slide_imgs = convert_pdf_to_images(pdf_path, output_folder=os.path.dirname(pptx_path))

        with st.spinner("Generating audio per slide..."):
            generate_tts_per_slide(script_file, voice_name=voice)

        with st.spinner("Creating final video..."):
            wav_files = sorted([f for f in os.listdir(".") if f.startswith("slide_") and f.endswith(".wav")])
            img_paths = sorted([f for f in slide_imgs if f.endswith(".png")])
            output_vid = pptx_path.replace(".pptx", ".mp4")
            generate_advanced_synced_video(img_paths, wav_files, output_vid)

        st.success("✅ Lecture generation complete!")
        st.download_button("📥 Download Slides", data=open(pptx_path, "rb"), file_name=os.path.basename(pptx_path))
        st.video(output_vid)

PAGES = {
    "🏠 Home": homepage,
    "🎓 Lecture Generator": lecture_generator,
}

st.sidebar.title("📂 Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
PAGES[selection]()
