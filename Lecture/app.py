import streamlit as st
import os
from extractor import extract_pdf_text, extract_youtube_transcript, summarize_text
from script import generate_slide_content, generate_professor_script
from slides import generate_slides_from_markdown
from TTS import generate_tts_per_slide
from advance import generate_advanced_synced_video
from video import convert_pptx_to_pdf, convert_pdf_to_images
from quiz import generate_quiz


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

def quiz_generator():
    st.title("📝 Quiz Generator")

    # Input section
    topic = st.text_input("Enter Topic")
    slide_md = ""
    uploaded_md = st.file_uploader("Upload Slide Markdown (optional)", type=["md"])
    if uploaded_md:
        slide_md = uploaded_md.read().decode("utf-8")

    context = st.text_area("Optional Context")

    num_questions = st.slider("Number of Questions", 1, 20, 5)
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    time_limit = st.selectbox("Time per Question", ["30 seconds", "1 minute", "2 minutes"])

    # Initialize session state
    if "quiz" not in st.session_state:
        st.session_state.quiz = []
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "quiz_generated" not in st.session_state:
        st.session_state.quiz_generated = False
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False

    # Generate quiz button
    if st.button("Generate Quiz"):
        if not topic:
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Generating quiz..."):
                try:
                    quiz_data = generate_quiz(topic, slide_md, context, num_questions, difficulty)
                    if quiz_data:
                        st.session_state.quiz = quiz_data
                        st.session_state.score = 0
                        st.session_state.q_index = 0
                        st.session_state.answers = {}
                        st.session_state.quiz_generated = True
                        st.session_state.quiz_completed = False
                        st.success("Quiz generated successfully! Start answering below.")
                    else:
                        st.error("Failed to generate quiz. Please try again.")
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")

    # Quiz interface
    if st.session_state.quiz_generated and st.session_state.quiz:
        quiz = st.session_state.quiz
        q_index = st.session_state.q_index

        st.markdown("---")
        
        if q_index < len(quiz) and not st.session_state.quiz_completed:
            current_q = quiz[q_index]
            
            # Progress bar
            progress = (q_index) / len(quiz)
            st.progress(progress)
            
            st.subheader(f"Question {q_index + 1} of {len(quiz)}")
            st.write(current_q["question"])
            
            # Answer options
            choice = st.radio(
                "Select your answer:", 
                current_q["options"], 
                key=f"q_{q_index}_{st.session_state.quiz_generated}"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Submit Answer", key=f"submit_{q_index}"):
                    # Store the answer
                    st.session_state.answers[q_index] = choice
                    
                    # Check if correct
                    correct_option = current_q["options"][ord(current_q["correct"]) - 65]
                    if choice == correct_option:
                        st.session_state.score += 1
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. The correct answer was: {correct_option}")
                    
                    # Show explanation
                    st.info(f"💡 **Explanation:** {current_q['explanation']}")
                    
                    # Move to next question
                    st.session_state.q_index += 1
                    
                    # Check if quiz is completed
                    if st.session_state.q_index >= len(quiz):
                        st.session_state.quiz_completed = True
                    
                    # Add a small delay and rerun
                    st.rerun()

        elif st.session_state.quiz_completed:
            # Quiz completed - show results
            st.balloons()
            st.success(f"🎉 Quiz Complete! Your Score: {st.session_state.score}/{len(quiz)}")
            
            # Calculate percentage
            percentage = (st.session_state.score / len(quiz)) * 100
            st.metric("Score Percentage", f"{percentage:.1f}%")
            
            # Show detailed results
            st.subheader("📊 Detailed Results")
            for i, q in enumerate(quiz):
                user_answer = st.session_state.answers.get(i, "No answer")
                correct_answer = q['options'][ord(q['correct'])-65]
                is_correct = user_answer == correct_answer
                
                with st.expander(f"Question {i+1} {'✅' if is_correct else '❌'}"):
                    st.write(f"**Question:** {q['question']}")
                    st.write(f"**Your Answer:** {user_answer}")
                    st.write(f"**Correct Answer:** {correct_answer}")
                    st.write(f"**Explanation:** {q['explanation']}")
            
            # Reset quiz button
            if st.button("🔄 Take Another Quiz"):
                st.session_state.quiz = []
                st.session_state.score = 0
                st.session_state.q_index = 0
                st.session_state.answers = {}
                st.session_state.quiz_generated = False
                st.session_state.quiz_completed = False
                st.rerun()


PAGES = {
    "🏠 Home": homepage,
    "🎓 Lecture Generator": lecture_generator,
    "📝 Quiz Generator": quiz_generator
}

st.sidebar.title("📂 Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
PAGES[selection]()