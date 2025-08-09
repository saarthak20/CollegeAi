import streamlit as st
import os
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from extractor import extract_pdf_text, extract_youtube_transcript, summarize_text
from script import generate_slide_content, generate_professor_script
from slides import generate_slides_from_markdown
from TTS import generate_tts_per_slide
from advance import generate_advanced_synced_video
from video import convert_pptx_to_pdf, convert_pdf_to_images
from quiz import generate_quiz

st.set_page_config(
    page_title="CollegeAi - AI-Powered Learning", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)
# Export Functions
def export_quiz_to_pdf(quiz_data, quiz_topic, user_answers=None, score=None):
    """Export quiz to PDF format"""
    filename = f"Quiz_{quiz_topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor='#667eea'
    )
    story.append(Paragraph(f"Quiz: {quiz_topic}", title_style))
    
    if score is not None:
        story.append(Paragraph(f"Score: {score}/{len(quiz_data)} ({(score/len(quiz_data)*100):.1f}%)", styles['Heading2']))
    
    story.append(Spacer(1, 12))
    
    # Questions
    for i, q in enumerate(quiz_data):
        # Question
        story.append(Paragraph(f"<b>Question {i+1}:</b> {q['question']}", styles['Normal']))
        story.append(Spacer(1, 6))
        
        # Options
        for j, option in enumerate(q['options']):
            letter = chr(65 + j)  # A, B, C, D
            is_correct = letter == q['correct']
            user_selected = user_answers and user_answers.get(i) == option
            
            style_text = option
            if is_correct:
                style_text = f"<b>{letter}. {option} ✓ (Correct)</b>"
            elif user_selected:
                style_text = f"{letter}. {option} ✗ (Your Answer)"
            else:
                style_text = f"{letter}. {option}"
                
            story.append(Paragraph(style_text, styles['Normal']))
        
        # Explanation
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Explanation:</b> {q['explanation']}", styles['Normal']))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    return filename

def export_quiz_to_moodle_xml(quiz_data, quiz_topic):
    """Export quiz to Moodle XML format"""
    quiz_elem = ET.Element("quiz")
    
    for i, q in enumerate(quiz_data):
        question_elem = ET.SubElement(quiz_elem, "question", type="multichoice")
        
        name_elem = ET.SubElement(question_elem, "name")
        text_elem = ET.SubElement(name_elem, "text")
        text_elem.text = f"Question {i+1}"
        
        questiontext_elem = ET.SubElement(question_elem, "questiontext", format="html")
        text_elem = ET.SubElement(questiontext_elem, "text")
        text_elem.text = f"<![CDATA[{q['question']}]]>"
        
        generalfeedback_elem = ET.SubElement(question_elem, "generalfeedback", format="html")
        text_elem = ET.SubElement(generalfeedback_elem, "text")
        text_elem.text = f"<![CDATA[{q['explanation']}]]>"
        
        # Options
        for j, option in enumerate(q['options']):
            answer_elem = ET.SubElement(question_elem, "answer", 
                                      fraction="100" if chr(65 + j) == q['correct'] else "0",
                                      format="html")
            text_elem = ET.SubElement(answer_elem, "text")
            text_elem.text = f"<![CDATA[{option}]]>"
    
    filename = f"Quiz_{quiz_topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    tree = ET.ElementTree(quiz_elem)
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    return filename

def export_quiz_to_json(quiz_data, quiz_topic, metadata=None):
    """Export quiz to JSON format"""
    export_data = {
        "topic": quiz_topic,
        "created_at": datetime.now().isoformat(),
        "metadata": metadata or {},
        "questions": quiz_data
    }
    
    filename = f"Quiz_{quiz_topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    return filename

def get_timer_seconds(time_limit):
    """Convert time limit string to seconds"""
    if "30 seconds" in time_limit:
        return 30
    elif "1 minute" in time_limit:
        return 60
    elif "2 minutes" in time_limit:
        return 120
    return 60  # default

# Custom CSS
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
                <li>Detailed explanations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea; font-size: 1.5rem; margin-bottom: 1rem;">🎨 Custom Themes</h3>
            <p>Choose from beautiful presentation themes and personalized professor personas for engaging content.</p>
            <ul style="color: #666;">
                <li>Multiple slide themes</li>
                <li>Professor personas</li>
                <li>Custom styling</li>
                <li>Professional layouts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting Started Section
    st.markdown("---")
    st.markdown("### 🚀 Ready to Get Started?")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("📚 Navigate to **Lecture Generator** to create your first AI-powered lecture, or try the **Quiz Generator** to test your knowledge!")

def lecture_generator():
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
        slide_md = ""
        uploaded_md = st.file_uploader("Upload Slide Markdown", type=["md"])
        if uploaded_md:
            slide_md = uploaded_md.read().decode("utf-8")
        

    # Initialize session state
    quiz_state_vars = [
        ("quiz", []), ("score", 0), ("q_index", 0), ("answers", {}),
        ("quiz_generated", False), ("quiz_completed", False),
        ("start_time", None), ("time_remaining", None), ("timed_mode", False),
        ("incorrect_questions", []), ("review_mode", False), ("quiz_topic", ""),
        ("quiz_metadata", {})
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
                                "mode": quiz_mode
                            }
                            
                            if timed_mode and not st.session_state.review_mode:
                                st.session_state.time_remaining = get_timer_seconds(time_limit)
                                st.session_state.start_time = time.time()
                            
                            st.success("✅ Quiz generated successfully! Start answering below.")
                        else:
                            st.error("❌ Failed to generate quiz. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Error generating quiz: {str(e)}")

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
                        st.markdown(f"**Your Answer:** {user_answer}")
                    with col2:
                        st.markdown(f"**Correct Answer:** {correct_answer}")
                    st.markdown(f"**Explanation:** {q['explanation']}")
            
            # Actions
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Take Another Quiz", use_container_width=True):
                    st.session_state.quiz = []
                    st.session_state.score = 0
                    st.session_state.q_index = 0
                    st.session_state.answers = {}
                    st.session_state.quiz_generated = False
                    st.session_state.quiz_completed = False
                    st.rerun()

# Navigation
PAGES = {
    "🏠 Home": homepage,
    "🎓 Lecture Generator": lecture_generator,
    "📝 Quiz Generator": quiz_generator
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
selection = st.sidebar.radio("", list(PAGES.keys()), label_visibility="collapsed")

# Add some sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About CollegeAi")
st.sidebar.info("Transform your learning with AI-powered lectures and interactive content generation.")

st.sidebar.markdown("### 🎯 Features")
st.sidebar.markdown("- 🎬 Auto-generated lectures")
st.sidebar.markdown("- 🗣️ Professional voiceovers")
st.sidebar.markdown("- 📝 Smart quiz generation")
st.sidebar.markdown("- 🌍 Multi-language support")
st.sidebar.markdown("- 🎨 Beautiful themes")

PAGES[selection]()