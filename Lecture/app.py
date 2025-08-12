import streamlit as st
import os
import json
import time
from datetime import datetime
from extractor import extract_pdf_text, extract_youtube_transcript, summarize_text
from script import generate_slide_content, generate_professor_script ,generate_notes_gemini
from slides import generate_slides_from_markdown
from TTS import generate_tts_per_slide
from advance import generate_advanced_synced_video
from video import convert_pptx_to_pdf, convert_pdf_to_images
from quiz import generate_quiz , export_quiz_to_pdf , export_quiz_to_moodle_xml , export_quiz_to_json
from Flashcard import generate_flashcards
from fpdf import FPDF
import pypandoc

def configure_gemini():
    import google.generativeai as genai
    if "GOOGLE_API_KEY" not in st.session_state:
        st.error("❌ Google API Key is missing. Please go to Home and enter it.")
        st.stop()
    genai.configure(api_key=st.session_state["GOOGLE_API_KEY"])


st.set_page_config(
    page_title="CollegeAi - AI-Powered Learning", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Export Functions (Enhanced with error handling)

def get_timer_seconds(time_limit):
    """Convert time limit string to seconds"""
    if "30 seconds" in time_limit:
        return 30
    elif "1 minute" in time_limit:
        return 60
    elif "2 minutes" in time_limit:
        return 120
    return 60  # default

# Custom CSS (keeping your existing styles)
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin: 1rem 0;
    }
    
    /* Title styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: white;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        text-align: center;
        margin-bottom: 1rem;
    }

    
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Export section styling */
    .export-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Card styling */
    .feature-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(76, 175, 80, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.5);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Success/Error message styling */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Quiz section styling */
    .quiz-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.8) 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Timer styling */
    .timer-container {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .timer-warning {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%) !important;
    }
    
    .timer-critical {
        background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%) !important;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar radio button styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        border: 2px dashed #667eea;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: #764ba2;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)



def homepage():
    # Hero Section
    st.markdown('<h1 class="main-title">🎓 CollegeAi</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform your learning experience with AI-powered lectures, interactive slides, and personalized content generation</p>', unsafe_allow_html=True)
    
    # Google API Key Input
    with st.container():
        st.subheader("🔑 Google API Key")
        api_key = st.text_input("Enter your Google API Key", type="password", help="Required for all AI features")
        if api_key:
            st.session_state["GOOGLE_API_KEY"] = api_key
            os.environ["GOOGLE_API_KEY"] = api_key
            st.success("✅ API Key saved successfully for this session.")
        elif "GOOGLE_API_KEY" not in st.session_state:
            st.warning("⚠️ Please enter your Google API Key to use the app.")
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea; font-size: 1.5rem; margin-bottom: 1rem;">🎬 Lecture Generation</h3>
            <p>Create comprehensive lectures with slides, voiceovers, and videos from any topic or source material.</p>
            <ul style="color: #666;">
                <li>YouTube transcript integration</li>
                <li>PDF content extraction</li>
                <li>Multi-language support</li>
                <li>Professional voiceovers</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #764ba2; font-size: 1.5rem; margin-bottom: 1rem;">📝 Smart Quizzes</h3>
            <p>Generate intelligent quizzes with instant feedback and detailed explanations for better learning.</p>
            <ul style="color: #666;">
                <li>Adaptive difficulty levels</li>
                <li>Instant feedback</li>
                <li>Progress tracking</li>
                <li>Export to multiple formats</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea; font-size: 1.5rem; margin-bottom: 1rem;">📝 Flashcards & Notes 🗂️</h3>
            <p>Create concise study materials and interactive flashcards for effective learning and quick revisions.</p>
            <ul style="color: #666;">
                <li>AI-generated concise notes from any source</li>
                <li>Beautifully formatted for easy reading</li>
                <li>Smart flashcards for active recall</li>
                <li>Supports multiple export formats (PDF, TXT, JSON)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting Started Section
    st.markdown("---")
    st.markdown("### 🚀 Ready to Get Started?")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("📚 Navigate to **Lecture Generator** to create your first AI-powered lecture, or try the **Quiz Generator** to test your knowledge! You can also checkout **Flashcards** and **Notes**")

def lecture_generator():
    configure_gemini()
    st.markdown('<h1 class="main-title">📚 Lecture Generator</h1>', unsafe_allow_html=True)
    
    # Input Section
    with st.container():
        st.markdown("### 📝 Lecture Configuration")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            topic = st.text_input("🎯 Enter Your Topic", placeholder="e.g., Machine Learning Fundamentals", help="Be specific for better results")
        
        with col2:
            length = st.selectbox("📏 Lecture Length", ["Short (Revision)", "Detailed", "Coursework"])
    
    # Source Selection
    st.markdown("### 📖 Content Source (Optional)")
    input_source = st.radio("Choose context source", ["None", "YouTube Video", "PDF Notes"], horizontal=True)
    context = ""
    if input_source == "YouTube Video":
        url = st.text_input("🎥 YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        if url:
            with st.spinner("🔄 Extracting and summarizing transcript..."):
                try:
                    transcript = extract_youtube_transcript(url)
                    context = summarize_text(transcript, topic)
                    st.success("✅ Transcript processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error processing YouTube URL: {str(e)}")
                    
    elif input_source == "PDF Notes":
        pdf_file = st.file_uploader("📄 Upload PDF Notes", type=["pdf"], help="Upload your study materials")
        if pdf_file:
            with st.spinner("📖 Extracting and summarizing PDF content..."):
                try:
                    text = extract_pdf_text(pdf_file)
                    context = summarize_text(text, topic)
                    st.success("✅ PDF content processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")

    # Customization Options
    st.markdown("### 🎨 Customization Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox("🌍 Language", 
            ["English", "Hindi", "Kannada", "German", "French", "Japanese", "Spanish", "Tamil", "Telugu", "Malayalam", "Chinese", "Other"])
        if language == "Other":
            language = st.text_input("Enter your language")
        
        persona = st.selectbox("👨‍🏫 Professor Persona", 
            ["Enthusiastic", "Calm Mentor", "Friendly Senior", "Strict Examiner"])
    
    with col2:
        theme = st.selectbox("🎨 Slide Theme", 
            ["1 - Light Blue", "2 - Dark", "3 - Pastel", "4 - Minimal Monochrome"])
        theme_choice = theme.split(" ")[0]
    
    persona_map = {
        "Enthusiastic": ("enthusiastic professor", "Kore"),
        "Calm Mentor": ("calm and clear mentor", "Aoede"),
        "Friendly Senior": ("friendly senior explaining with stories", "Puck"),
        "Strict Examiner": ("strict examiner, focused and concise", "Charon"),
    }

    # Generate Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🎬 Generate Lecture", use_container_width=True)
    
    if generate_btn:
        if not topic:
            st.warning("⚠️ Please enter a topic to continue.")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Generate slide content
            status_text.text("🔄 Generating slide content...")
            progress_bar.progress(20)
            slide_md = generate_slide_content(topic, length, context=context, language=language)
            slide_md_file = f"Lecture_{topic.replace(' ', '_')}.md"
            with open(slide_md_file, "w", encoding="utf-8") as f:
                f.write(slide_md)

            # Step 2: Generate professor script
            status_text.text("🎭 Creating professor script...")
            progress_bar.progress(35)
            persona_text, voice = persona_map[persona]
            script = generate_professor_script(topic, slide_md, persona_text, context, language)
            script_file = slide_md_file.replace(".md", f"_{language}_ProfessorScript.md")
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(script)

            # Step 3: Generate slides
            status_text.text("🎨 Designing slides...")
            progress_bar.progress(50)
            generate_slides_from_markdown(slide_md_file, theme_choice=theme_choice)

            pptx_path = slide_md_file.replace("Lecture", "Slides").replace(".md", ".pptx")

            # Step 4: Convert to images
            status_text.text("🖼️ Converting slides to images...")
            progress_bar.progress(65)
            pdf_path = convert_pptx_to_pdf(pptx_path)
            slide_imgs = convert_pdf_to_images(pdf_path, output_folder=os.path.dirname(pptx_path))

            # Step 5: Generate audio
            status_text.text("🔊 Generating voiceover...")
            progress_bar.progress(80)
            generate_tts_per_slide(script_file, voice_name=voice)

            # Step 6: Create final video
            status_text.text("🎬 Creating final video...")
            progress_bar.progress(95)
            wav_files = sorted([f for f in os.listdir(".") if f.startswith("slide_") and f.endswith(".wav")])
            img_paths = sorted([f for f in slide_imgs if f.endswith(".png")])
            output_vid = pptx_path.replace(".pptx", ".mp4")
            generate_advanced_synced_video(img_paths, wav_files, output_vid)

            progress_bar.progress(100)
            status_text.text("✅ Lecture generation complete!")
            
            # Success section
            st.balloons()
            st.success("🎉 Your lecture has been successfully generated!")
            
            col1, col2 = st.columns(2)
            with col1:
                with open(pptx_path, "rb") as file:
                    st.download_button("📥 Download Slides", data=file, file_name=os.path.basename(pptx_path))
            with col2:
                st.info(f"📊 Generated {len(slide_imgs)} slides with full narration")
            
            # Video player
            st.markdown("### 🎥 Preview Your Lecture")
            st.video(output_vid)
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def quiz_generator():
    configure_gemini()
    st.markdown('<h1 class="main-title">📝 Quiz Generator</h1>', unsafe_allow_html=True)

    # Input section
    st.markdown("### 🎯 Quiz Configuration")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input("📚 Enter Topic", placeholder="e.g., Python Programming Basics")
    with col2:
        num_questions = st.slider("❓ Number of Questions", 1, 20, 5)
    
    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.selectbox("🎖️ Difficulty Level", ["Easy", "Medium", "Hard"])
        timed_mode = st.checkbox("⏰ Enable Timed Mode", help="Add countdown timer for each question")
    with col2:
        time_limit = st.selectbox("⏰ Time per Question", ["30 seconds", "1 minute", "2 minutes"])
        quiz_mode = st.selectbox("🎯 Quiz Mode", ["Standard", "Review Mode"], 
                                help="Review Mode: Browse all questions without time pressure")

    st.markdown("### 📖 Content Source (Optional)")
    input_source = st.radio("Choose context source", ["None", "YouTube Video", "PDF Notes"], horizontal=True)
    slide_md = ""
    context = ""

    if input_source == "YouTube Video":
        url = st.text_input("🎥 YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        if url:
            with st.spinner("🔄 Extracting and summarizing transcript..."):
                try:
                    transcript = extract_youtube_transcript(url)
                    context = summarize_text(transcript, topic)
                    st.success("✅ Transcript processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error processing YouTube URL: {str(e)}")
                    
    elif input_source == "PDF Notes":
        pdf_file = st.file_uploader("📄 Upload PDF Notes", type=["pdf"], help="Upload your study materials")
        if pdf_file:
            with st.spinner("📖 Extracting and summarizing PDF content..."):
                try:
                    text = extract_pdf_text(pdf_file)
                    context = summarize_text(text, topic)
                    st.success("✅ PDF content processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")

    # Optional inputs
    with st.expander("📁 Optional Content Sources"):
        uploaded_md = st.file_uploader("Upload Slide Markdown", type=["md"])
        if uploaded_md:
            slide_md = uploaded_md.read().decode("utf-8")

    # Initialize session state
    quiz_state_vars = [
        ("quiz", []), ("score", 0), ("q_index", 0), ("answers", {}),
        ("quiz_generated", False), ("quiz_completed", False),
        ("start_time", None), ("time_remaining", None), ("timed_mode", False),
        ("incorrect_questions", []), ("review_mode", False), ("quiz_topic", ""),
        ("quiz_metadata", {}), ("export_quiz_data", None)
    ]
    
    for var, default in quiz_state_vars:
        if var not in st.session_state:
            st.session_state[var] = default

    # Generate quiz button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 Generate Quiz", use_container_width=True):
            if not topic:
                st.warning("⚠️ Please enter a topic to generate quiz.")
            else:
                with st.spinner("🤖 Creating your personalized quiz..."):
                    try:
                        quiz_data = generate_quiz(topic, slide_md, context, num_questions, difficulty)
                        if quiz_data:
                            st.session_state.quiz = quiz_data
                            st.session_state.score = 0
                            st.session_state.q_index = 0
                            st.session_state.answers = {}
                            st.session_state.quiz_generated = True
                            st.session_state.quiz_completed = False
                            st.session_state.quiz_topic = topic
                            st.session_state.timed_mode = timed_mode
                            st.session_state.review_mode = (quiz_mode == "Review Mode")
                            st.session_state.quiz_metadata = {
                                "difficulty": difficulty,
                                "time_limit": time_limit,
                                "timed_mode": timed_mode,
                                "mode": quiz_mode,
                                "num_questions": num_questions
                            }
                            
                            if timed_mode and not st.session_state.review_mode:
                                st.session_state.time_remaining = get_timer_seconds(time_limit)
                                st.session_state.start_time = time.time()
                            
                            st.success("✅ Quiz generated successfully! Start answering below.")
                        else:
                            st.error("❌ Failed to generate quiz. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Error generating quiz: {str(e)}")

    # Export Options (Show only after quiz is generated)
    if st.session_state.quiz_generated and st.session_state.quiz:
        st.markdown("---")
        st.markdown('<div class="export-section">', unsafe_allow_html=True)
        st.markdown("### 📤 Export Quiz")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📄 Export to PDF", use_container_width=True, help="Download quiz as PDF with answers and explanations"):
                with st.spinner("Creating PDF..."):
                    pdf_file = export_quiz_to_pdf(
                        st.session_state.quiz, 
                        st.session_state.quiz_topic,
                        st.session_state.answers if st.session_state.quiz_completed else None,
                        st.session_state.score if st.session_state.quiz_completed else None
                    )
                    if pdf_file and os.path.exists(pdf_file):
                        with open(pdf_file, "rb") as file:
                            st.download_button(
                                "📥 Download PDF",
                                data=file.read(),
                                file_name=pdf_file,
                                mime="application/pdf",
                                use_container_width=True
                            )
                        os.remove(pdf_file)  # Clean up temporary file
                        st.success("✅ PDF created successfully!")
        
        with col2:
            if st.button("🎓 Export to Moodle XML", use_container_width=True, help="Export for Moodle LMS import"):
                with st.spinner("Creating Moodle XML..."):
                    xml_file = export_quiz_to_moodle_xml(st.session_state.quiz, st.session_state.quiz_topic)
                    if xml_file and os.path.exists(xml_file):
                        with open(xml_file, "rb") as file:
                            st.download_button(
                                "📥 Download XML",
                                data=file.read(),
                                file_name=xml_file,
                                mime="application/xml",
                                use_container_width=True
                            )
                        os.remove(xml_file)  # Clean up temporary file
                        st.success("✅ Moodle XML created successfully!")
        
        with col3:
            if st.button("📊 Export to JSON", use_container_width=True, help="Export as JSON for data analysis"):
                with st.spinner("Creating JSON..."):
                    json_file = export_quiz_to_json(
                        st.session_state.quiz, 
                        st.session_state.quiz_topic,
                        st.session_state.quiz_metadata,
                        st.session_state.answers if st.session_state.quiz_completed else None,
                        st.session_state.score if st.session_state.quiz_completed else None
                    )
                    if json_file and os.path.exists(json_file):
                        with open(json_file, "rb") as file:
                            st.download_button(
                                "📥 Download JSON",
                                data=file.read(),
                                file_name=json_file,
                                mime="application/json",
                                use_container_width=True
                            )
                        os.remove(json_file)  # Clean up temporary file
                        st.success("✅ JSON created successfully!")
        
        with col4:
            if st.button("📋 Copy Quiz Text", use_container_width=True, help="Copy quiz as formatted text"):
                quiz_text = f"Quiz: {st.session_state.quiz_topic}\n"
                quiz_text += f"Generated on: {datetime.now().strftime('%B %d, %Y')}\n\n"
                
                for i, q in enumerate(st.session_state.quiz):
                    quiz_text += f"Question {i+1}: {q['question']}\n"
                    for j, option in enumerate(q['options']):
                        letter = chr(65 + j)
                        mark = " (Correct)" if letter == q['correct'] else ""
                        quiz_text += f"{letter}. {option}{mark}\n"
                    quiz_text += f"Explanation: {q['explanation']}\n\n"
                
                st.text_area("Quiz Text (Copy this)", value=quiz_text, height=200)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Quiz interface
    if st.session_state.quiz_generated and st.session_state.quiz:
        quiz = st.session_state.quiz
        q_index = st.session_state.q_index

        st.markdown("---")
        
        if q_index < len(quiz) and not st.session_state.quiz_completed:
            current_q = quiz[q_index]
            
            # Quiz container
            st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
            
            # Timer for timed mode
            if st.session_state.timed_mode and not st.session_state.review_mode:
                if st.session_state.time_remaining is not None:
                    elapsed = time.time() - st.session_state.start_time
                    remaining = max(0, st.session_state.time_remaining - elapsed)
                    
                    if remaining > 0:
                        minutes = int(remaining // 60)
                        seconds = int(remaining % 60)
                        
                        # Timer styling based on remaining time
                        timer_class = "timer-container"
                        if remaining <= 10:
                            timer_class += " timer-critical"
                        elif remaining <= 30:
                            timer_class += " timer-warning"
                        
                        st.markdown(f"""
                        <div class="{timer_class}">
                            ⏰ Time Remaining: {minutes:02d}:{seconds:02d}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Auto-submit when time runs out
                        if remaining <= 0:
                            st.session_state.answers[q_index] = "Time Expired"
                            st.session_state.q_index += 1
                            if st.session_state.q_index < len(quiz):
                                st.session_state.start_time = time.time()
                            else:
                                st.session_state.quiz_completed = True
                            st.rerun()
                    else:
                        # Time expired for this question
                        st.error("⏰ Time expired for this question!")
                        st.session_state.answers[q_index] = "Time Expired"
                        st.session_state.q_index += 1
                        if st.session_state.q_index < len(quiz):
                            st.session_state.start_time = time.time()
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
            
            # Progress section
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                progress = q_index / len(quiz)
                st.progress(progress)
            with col2:
                st.metric("Question", f"{q_index + 1}/{len(quiz)}")
            with col3:
                st.metric("Score", f"{st.session_state.score}/{q_index}")
            
            st.markdown(f"### ❓ Question {q_index + 1}")
            st.markdown(f"**{current_q['question']}**")
            
            # Review mode - show all questions at once
            if st.session_state.review_mode:
                st.info("📖 **Review Mode:** You can browse all questions without time pressure.")
                
                # Navigation buttons for review mode
                nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
                with nav_col1:
                    if q_index > 0:
                        if st.button("⬅️ Previous", key="prev_review"):
                            st.session_state.q_index = max(0, q_index - 1)
                            st.rerun()
                with nav_col3:
                    if q_index < len(quiz) - 1:
                        if st.button("➡️ Next", key="next_review"):
                            st.session_state.q_index = min(len(quiz) - 1, q_index + 1)
                            st.rerun()
                    elif q_index == len(quiz) - 1:
                        if st.button("✅ Finish Review", key="finish_review"):
                            st.session_state.quiz_completed = True
                            st.rerun()
            
            # Answer options
            choice = st.radio(
                "Select your answer:", 
                current_q["options"], 
                key=f"q_{q_index}_{st.session_state.quiz_generated}",
                disabled=st.session_state.review_mode and q_index in st.session_state.answers
            )

            # Show correct answer in review mode
            if st.session_state.review_mode:
                correct_answer = current_q["options"][ord(current_q["correct"]) - 65]
                st.success(f"✅ **Correct Answer:** {correct_answer}")
                st.info(f"💡 **Explanation:** {current_q['explanation']}")
            
            # Submit button (not in review mode)
            if not st.session_state.review_mode:
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("✅ Submit Answer", key=f"submit_{q_index}", use_container_width=True):
                        # Store the answer
                        st.session_state.answers[q_index] = choice
                        
                        # Check if correct
                        correct_option = current_q["options"][ord(current_q["correct"]) - 65]
                        is_correct = choice == correct_option
                        
                        if is_correct:
                            st.session_state.score += 1
                            st.success("🎉 Correct! Well done!")
                        else:
                            st.error(f"❌ Incorrect. The correct answer was: **{correct_option}**")
                            # Add to incorrect questions for retry option
                            st.session_state.incorrect_questions.append(q_index)
                        
                        # Show explanation
                        st.info(f"💡 **Explanation:** {current_q['explanation']}")
                        
                        # Move to next question
                        st.session_state.q_index += 1
                        
                        # Reset timer for next question
                        if st.session_state.timed_mode and st.session_state.q_index < len(quiz):
                            st.session_state.start_time = time.time()
                        
                        # Check if quiz is completed
                        if st.session_state.q_index >= len(quiz):
                            st.session_state.quiz_completed = True
                        
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.quiz_completed:
            # Quiz completed - show results
            st.balloons()
            
            # Results header
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                percentage = (st.session_state.score / len(quiz)) * 100
                
                # Performance badge
                if percentage >= 80:
                    badge = "🏆 Excellent!"
                    color = "#4CAF50"
                elif percentage >= 60:
                    badge = "🥈 Good Job!"
                    color = "#FF9800"
                else:
                    badge = "📚 Keep Learning!"
                    color = "#2196F3"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {color}22 0%, {color}11 100%); border-radius: 20px; margin: 1rem 0;">
                    <h1 style="color: {color}; margin: 0;">{badge}</h1>
                    <h2 style="margin: 0.5rem 0;">Quiz Complete!</h2>
                    <h3 style="color: #666; margin: 0;">Score: {st.session_state.score}/{len(quiz)} ({percentage:.1f}%)</h3>
                </div>
                """, unsafe_allow_html=True)

            # Export results section
            st.markdown("---")
            st.markdown('<div class="export-section">', unsafe_allow_html=True)
            st.markdown("### 📤 Export Your Results")
            st.info("💡 Now that you've completed the quiz, you can export your results with answers and scores!")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Export Results to PDF", use_container_width=True):
                    with st.spinner("Creating results PDF..."):
                        pdf_file = export_quiz_to_pdf(
                            st.session_state.quiz, 
                            st.session_state.quiz_topic,
                            st.session_state.answers,
                            st.session_state.score
                        )
                        if pdf_file and os.path.exists(pdf_file):
                            with open(pdf_file, "rb") as file:
                                st.download_button(
                                    "📥 Download Results PDF",
                                    data=file.read(),
                                    file_name=pdf_file,
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            os.remove(pdf_file)
                            st.success("✅ Results PDF created!")
            
            with col2:
                if st.button("📊 Export Results to JSON", use_container_width=True):
                    with st.spinner("Creating results JSON..."):
                        json_file = export_quiz_to_json(
                            st.session_state.quiz, 
                            st.session_state.quiz_topic,
                            st.session_state.quiz_metadata,
                            st.session_state.answers,
                            st.session_state.score
                        )
                        if json_file and os.path.exists(json_file):
                            with open(json_file, "rb") as file:
                                st.download_button(
                                    "📥 Download Results JSON",
                                    data=file.read(),
                                    file_name=json_file,
                                    mime="application/json",
                                    use_container_width=True
                                )
                            os.remove(json_file)
                            st.success("✅ Results JSON created!")
            
            with col3:
                # Performance summary
                st.metric("Final Score", f"{st.session_state.score}/{len(quiz)}")
                st.metric("Percentage", f"{percentage:.1f}%")
                if st.session_state.incorrect_questions:
                    st.metric("Incorrect", len(st.session_state.incorrect_questions))
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed results
            st.markdown("### 📊 Detailed Results")
            for i, q in enumerate(quiz):
                user_answer = st.session_state.answers.get(i, "No answer")
                correct_answer = q['options'][ord(q['correct'])-65]
                is_correct = user_answer == correct_answer
                
                with st.expander(f"Question {i+1} {'✅ Correct' if is_correct else '❌ Incorrect'}"):
                    st.markdown(f"**Question:** {q['question']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if user_answer == "Time Expired":
                            st.markdown(f"**Your Answer:** ⏰ Time Expired")
                        else:
                            st.markdown(f"**Your Answer:** {user_answer}")
                    with col2:
                        st.markdown(f"**Correct Answer:** {correct_answer}")
                    st.markdown(f"**Explanation:** {q['explanation']}")
            
            # Actions
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Take Another Quiz", use_container_width=True):
                    # Reset all session state
                    for var, default in quiz_state_vars:
                        st.session_state[var] = default
                    st.rerun()

def flashcard_generator():
    configure_gemini()
    st.markdown('<h1 class="main-title">📇 Flashcard Generator</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input("📚 Enter Topic", placeholder="e.g., Data Structures Basics")
    with col2:
        num_cards = st.slider("🃏 Number of Flashcards", 1, 30, 10)

    col1, col2 = st.columns(2)
    st.markdown("### 📖 Content Source (Optional)")
    input_source = st.radio("Choose context source", ["None", "YouTube Video", "PDF Notes"], horizontal=True)
    slide_md = ""
    context = ""

    if input_source == "YouTube Video":
        url = st.text_input("🎥 YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        if url:
            with st.spinner("🔄 Extracting and summarizing transcript..."):
                try:
                    transcript = extract_youtube_transcript(url)
                    context = summarize_text(transcript, topic)
                    st.success("✅ Transcript processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error processing YouTube URL: {str(e)}")
                    
    elif input_source == "PDF Notes":
        pdf_file = st.file_uploader("📄 Upload PDF Notes", type=["pdf"], help="Upload your study materials")
        if pdf_file:
            with st.spinner("📖 Extracting and summarizing PDF content..."):
                try:
                    text = extract_pdf_text(pdf_file)
                    context = summarize_text(text, topic)
                    st.success("✅ PDF content processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")

    with col1:
        difficulty = st.selectbox("🎖️ Difficulty Level", ["Easy", "Medium", "Hard"])
        language = st.selectbox("🌍 Language", 
            ["English", "Hindi", "Kannada", "German", "French", "Japanese", "Spanish", "Tamil", "Telugu", "Malayalam", "Chinese", "Other"])
        if language == "Other":
            language = st.text_input("Enter your language")
    with col2:
        slide_md = ""
        uploaded_md = st.file_uploader("📄 Upload Slide Markdown (optional)", type=["md"])
        if uploaded_md:
            slide_md = uploaded_md.read().decode("utf-8")
        

    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 Generate Flashcards", use_container_width=True):
            if not topic:
                st.warning("⚠️ Please enter a topic.")
            else:
                with st.spinner("🪄 Creating flashcards..."):
                    cards = generate_flashcards(topic, num_cards, difficulty, language, slide_md, context)
                    if cards:
                        st.session_state.flashcards = cards
                        st.success("✅ Flashcards generated successfully!")
                    else:
                        st.error("❌ Failed to generate flashcards.")

    # Display flashcards using Streamlit columns for better layout
    if st.session_state.flashcards:
        st.markdown("### 📌 Your Flashcards")
        st.markdown("*Click on any flashcard to reveal the answer*")
        
        # Initialize flip state for each card if not exists
        if "card_flipped" not in st.session_state:
            st.session_state.card_flipped = [False] * len(st.session_state.flashcards)
        
        # Ensure the flip state list matches the number of cards
        if len(st.session_state.card_flipped) != len(st.session_state.flashcards):
            st.session_state.card_flipped = [False] * len(st.session_state.flashcards)
        
        # CSS for the flashcards
        st.markdown("""
        <style>
        .flashcard-container {
            margin: 20px 0;
        }
        
        .flashcard {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            color: white;
            text-align: center;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            font-size: 16px;
            font-weight: 500;
            position: relative;
            overflow: hidden;
        }
        
        .flashcard:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .flashcard-front {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .flashcard-back {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .flashcard-content {
            padding: 10px;
            line-height: 1.4;
            word-wrap: break-word;
        }
        
        .flip-all-btn {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border: none;
            border-radius: 25px;
            padding: 10px 20px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            margin: 10px 5px;
            transition: all 0.3s ease;
        }
        
        .flip-all-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Add flip all buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                if st.button("🔄 Flip All to Questions", use_container_width=True):
                    st.session_state.card_flipped = [False] * len(st.session_state.flashcards)
                    st.rerun()
            with subcol2:
                if st.button("🔄 Flip All to Answers", use_container_width=True):
                    st.session_state.card_flipped = [True] * len(st.session_state.flashcards)
                    st.rerun()
        
        st.markdown("---")
        
        # Display flashcards in a responsive grid using Streamlit columns
        cards_per_row = 2  # Adjust this based on your preference
        
        for i in range(0, len(st.session_state.flashcards), cards_per_row):
            cols = st.columns(cards_per_row)
            
            for j in range(cards_per_row):
                card_idx = i + j
                if card_idx < len(st.session_state.flashcards):
                    card = st.session_state.flashcards[card_idx]
                    
                    with cols[j]:
                        # Determine if card is flipped
                        is_flipped = st.session_state.card_flipped[card_idx]
                        
                        # Create the flashcard
                        card_class = "flashcard-back" if is_flipped else "flashcard-front"
                        card_content = card['back'] if is_flipped else card['front']
                        
                        # Make the card clickable
                        if st.button(
                            f"📱 Card {card_idx + 1}",
                            key=f"card_button_{card_idx}",
                            help="Click to flip the card",
                            use_container_width=True
                        ):
                            st.session_state.card_flipped[card_idx] = not st.session_state.card_flipped[card_idx]
                            st.rerun()
                        
                        # Display the card content
                        st.markdown(f"""
                        <div class="flashcard {card_class}">
                            <div class="flashcard-content">
                                {card_content}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Study modes
        st.markdown("### 📚 Study Modes")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Quiz Mode", use_container_width=True):
                st.session_state.quiz_mode = True
                st.session_state.current_card = 0
                st.session_state.card_flipped = [False] * len(st.session_state.flashcards)
                st.rerun()
        
        with col2:
            if st.button("🔀 Shuffle Cards", use_container_width=True):
                import random
                random.shuffle(st.session_state.flashcards)
                st.session_state.card_flipped = [False] * len(st.session_state.flashcards)
                st.rerun()
        
        with col3:
            if st.button("🔄 Reset All", use_container_width=True):
                st.session_state.card_flipped = [False] * len(st.session_state.flashcards)
                st.rerun()
        
        # Quiz mode
        if hasattr(st.session_state, 'quiz_mode') and st.session_state.quiz_mode:
            st.markdown("### 🎯 Quiz Mode")
            
            if 'current_card' not in st.session_state:
                st.session_state.current_card = 0
            
            current_idx = st.session_state.current_card
            if current_idx < len(st.session_state.flashcards):
                card = st.session_state.flashcards[current_idx]
                
                st.markdown(f"**Card {current_idx + 1} of {len(st.session_state.flashcards)}**")
                
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    if st.session_state.card_flipped[current_idx]:
                        st.markdown(f"""
                        <div class="flashcard flashcard-back">
                            <div class="flashcard-content">
                                <strong>Answer:</strong><br>
                                {card['back']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="flashcard flashcard-front">
                            <div class="flashcard-content">
                                <strong>Question:</strong><br>
                                {card['front']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("⬅️ Previous") and current_idx > 0:
                        st.session_state.current_card -= 1
                        st.rerun()
                
                with col2:
                    if st.button("🔄 Flip"):
                        st.session_state.card_flipped[current_idx] = not st.session_state.card_flipped[current_idx]
                        st.rerun()
                
                with col3:
                    if st.button("➡️ Next") and current_idx < len(st.session_state.flashcards) - 1:
                        st.session_state.current_card += 1
                        st.rerun()
                
                with col4:
                    if st.button("❌ Exit Quiz"):
                        st.session_state.quiz_mode = False
                        st.rerun()
            else:
                st.success("🎉 Quiz completed!")
                if st.button("🔄 Restart Quiz"):
                    st.session_state.current_card = 0
                    st.session_state.card_flipped = [False] * len(st.session_state.flashcards)
                    st.rerun()

        st.markdown("---")

        # Export functions
        def export_pdf(flashcards):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 20)
            pdf.cell(0, 15, "Flashcards", ln=True, align="C")
            pdf.ln(10)
            
            for i, fc in enumerate(flashcards, 1):
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"Card {i}", ln=True)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(30, 8, "Question:", 0, 0)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 8, str(fc['front']), 0, 1)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(30, 8, "Answer:", 0, 0)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 8, str(fc['back']), 0, 1)
                pdf.ln(5)
                
            pdf_path = "flashcards.pdf"
            pdf.output(pdf_path)
            return pdf_path

        # Download buttons
        st.markdown("### 📥 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generate PDF", use_container_width=True):
                with st.spinner("Creating PDF..."):
                    pdf_path = export_pdf(st.session_state.flashcards)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "📥 Download PDF", 
                            f.read(), 
                            "flashcards.pdf",
                            "application/pdf",
                            use_container_width=True
                        )
        
        with col2:
            json_data = json.dumps(st.session_state.flashcards, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Download JSON", 
                json_data, 
                "flashcards.json",
                "application/json",
                use_container_width=True
            )
        
        with col3:
            text_content = "FLASHCARDS\n" + "="*50 + "\n\n"
            for i, card in enumerate(st.session_state.flashcards, 1):
                text_content += f"Card {i}:\n"
                text_content += f"Q: {card['front']}\n"
                text_content += f"A: {card['back']}\n\n"
            
            st.download_button(
                "📥 Download TXT",
                text_content,
                "flashcards.txt",
                "text/plain",
                use_container_width=True
            )

def notes_generator():
    configure_gemini()
    st.title("🗒️ Notes Maker")

    topic = st.text_input("Enter Topic", key="notes_topic")
    input_source = st.radio("Choose context source", ["None", "YouTube Video", "PDF Notes", "Manual Text"], key="notes_source")
    context = ""

    if input_source == "YouTube Video":
        url = st.text_input("Enter YouTube URL", key="notes_youtube")
        if url:
            with st.spinner("Extracting and summarizing transcript..."):
                transcript = extract_youtube_transcript(url)
                context = summarize_text(transcript, topic)
    elif input_source == "PDF Notes":
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="notes_pdf")
        if pdf_file:
            with st.spinner("Extracting and summarizing PDF content..."):
                text = extract_pdf_text(pdf_file)
                context = summarize_text(text, topic)
    elif input_source == "Manual Text":
        manual_text = st.text_area("Paste your content here", key="notes_manual")
        if manual_text:
            context = manual_text

    length = st.selectbox("Notes Length", ["Short", "Medium", "Detailed"], key="notes_length")
    language = st.selectbox("Language", ["English", "Hindi", "Kannada", "German", "French", "Japanese", "Spanish", "Tamil", "Telugu", "Malayalam", "Chinese", "Other"], key="notes_lang")
    if language == "Other":
        language = st.text_input("Enter your language", key="notes_other_lang")

    if st.button("📝 Generate Notes", key="generate_notes"):
        if not topic:
            st.warning("Please enter a topic.")
            return

        with st.spinner("Generating notes..."):
            notes_md = generate_notes_gemini(topic, length, context=context, language=language)
            notes_md_file = f"Notes_{topic.replace(' ', '_')}.md"
            with open(notes_md_file, "w", encoding="utf-8") as f:
                f.write(notes_md)

        st.subheader("📄 Generated Notes")
        st.markdown(notes_md)

        # Convert MD → TXT
        txt_file = notes_md_file.replace(".md", ".txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(notes_md)

        # Convert MD → PDF
        pdf_file = notes_md_file.replace(".md", ".pdf")
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", size=12)

        # Split by lines and write
        for line in notes_md.split("\n"):
            pdf.multi_cell(0, 8, line)

        pdf.output(pdf_file)

        # Downloads
        st.download_button("📥 Download Markdown", data=open(notes_md_file, "rb"), file_name=os.path.basename(notes_md_file))
        st.download_button("📥 Download TXT", data=open(txt_file, "rb"), file_name=os.path.basename(txt_file))
        st.download_button("📥 Download PDF", data=open(pdf_file, "rb"), file_name=os.path.basename(pdf_file))


# Navigation
PAGES = {
    "🏠 Home": homepage,
    "🎓 Lecture Generator": lecture_generator,
    "📝 Quiz Generator": quiz_generator,
    "📇 Flashcard Generator": flashcard_generator,
    "🗒️ Notes Maker": notes_generator
}

# Sidebar styling
st.markdown("""
<style>
    .css-1d391kg .stRadio > label {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .css-1d391kg .stRadio > label:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("# 📂 Navigation")
st.sidebar.markdown("---")
selection = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")


# Add some sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About CollegeAi")
st.sidebar.info("Transform your learning with AI-powered lectures and interactive content generation.")

st.sidebar.markdown("### 🎯 Features")
st.sidebar.markdown("- 🎬 Auto-generated lectures")
st.sidebar.markdown("- 🗣️ Professional voiceovers")
st.sidebar.markdown("- 📝 Smart quiz generation")
st.sidebar.markdown("- 📤 Multiple export formats")
st.sidebar.markdown("- 🌍 Multi-language support")
st.sidebar.markdown("- 📇 Efficient Flashcard generation")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📤 Export Formats Supported")
st.sidebar.markdown("- 📄 PDF (with results)")
st.sidebar.markdown("- 🎓 Moodle XML")
st.sidebar.markdown("- 📊 JSON (data analysis)")
st.sidebar.markdown("- 📋 Plain text")


PAGES[selection]()