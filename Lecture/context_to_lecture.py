import os
from extractor import extract_youtube_transcript, extract_pdf_text, summarize_text
from script import generate_slide_content, generate_professor_script

def get_context(topic):
    print("\nSelect context source:\n1) YouTube Video\n2) PDF Notes\n3) None")
    choice = input("Enter choice (1/2/3): ").strip()

    if choice == "1":
        url = input("Enter YouTube URL: ").strip()
        transcript = extract_youtube_transcript(url)
        context = summarize_text(transcript, topic)
    elif choice == "2":
        path = input("Enter path to PDF notes: ").strip()
        if not os.path.exists(path):
            print("❌ PDF not found.")
            return None
        pdf_text = extract_pdf_text(path)
        context = summarize_text(pdf_text, topic)
    elif choice == "3":
        return None
    else:
        print("❌ Invalid choice.")
        return None

    context_path = f"ContextSummary_{topic.replace(' ', '_')}.md"
    with open(context_path, "w", encoding="utf-8") as f:
        f.write(context)
    print(f"✅ Context saved to {context_path}")
    return context

def main():
    print("=== collegeAi: Context-Aware Lecture Generator ===")
    topic = input("Enter topic: ").strip()
    context = get_context(topic)

    print("\nChoose lecture length:\n1) Short (Revision)\n2) Detailed\n3) Coursework")
    length_map = {"1": "Short (Revision)", "2": "Detailed", "3": "Coursework"}
    length = length_map.get(input("Choice (1/2/3): ").strip(), "Detailed")
    language = input("Enter target language (default: English): ").strip() or "English"

    # Generate Slide Markdown
    slide_md = generate_slide_content(topic, length, context=context, language=language)
    slide_file = f"Lecture_{topic.replace(' ', '_')}_{length.replace(' ', '_')}.md"
    with open(slide_file, "w", encoding="utf-8") as f:
        f.write(slide_md)
    print(f"✅ Slide content saved to {slide_file}")

    # Persona Selection
    persona_map = {
        "1": "enthusiastic professor",
        "2": "calm and clear mentor",
        "3": "friendly senior explaining with stories",
        "4": "strict examiner, focused and concise"
    }
    print("\nChoose professor persona:\n1) Enthusiastic\n2) Calm Mentor\n3) Friendly Senior\n4) Strict")
    persona = persona_map.get(input("Choice (1-4): ").strip(), "enthusiastic professor")

    # Generate Professor Script
    prof_script = generate_professor_script(topic, slide_md, persona, context, language)
    prof_file = slide_file.replace(".md", f"_{language}_ProfessorScript.md")
    with open(prof_file, "w", encoding="utf-8") as f:
        f.write(prof_script)
    print(f"✅ Professor script saved to {prof_file}")

if __name__ == "__main__":
    main()
