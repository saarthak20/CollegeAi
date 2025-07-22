from google.generativeai import GenerativeModel
import os

def generate_slide_content(topic, length="Detailed"):
    """
    Generates clean, structured, beginner-friendly slide content using Gemini.
    """
    prompt = f"""
You are an expert educator tasked with creating clear, structured slide content for a lecture on '{topic}'.

You will generate content to be directly used for slide generation, so avoid unnecessary conversational style.

Follow this Markdown structure exactly:

# Title: <title>

## Introduction
<concise, clear introduction for slides>

## Section 1: <Section Title>
<concise, clear explanation for slides>

## Section 2: <Section Title>
<concise, clear explanation for slides>

## Example
<real-life example for slides>

## Python Code Example (if applicable)
<clean code block or snippet>

## Summary
- Bullet 1
- Bullet 2
- Bullet 3

Keep it factual, clear, and easy to convert into slides.
Length: {length}.
"""
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def generate_professor_script(topic, md_content, persona="enthusiastic professor"):
    """
    Generates a personalized, engaging professor script aligned section-wise with the provided slide content.
    """
    prompt = f"""
You are an {persona} explaining the topic '{topic}' to undergraduates.

Using the following slide content, generate a section-wise spoken script that is engaging, personal, and easy to listen to, while retaining clarity and accuracy.

You can add rhetorical questions, light jokes, small relatable stories, and spoken transitions.

Keep the structure aligned with the section headers so each section corresponds directly to a slide for TTS generation.

SLIDE CONTENT:
\"\"\"
{md_content}
\"\"\"

Return the script in this structure using the same section headers for alignment.
"""
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def main():
    print("=== collegeAi Lecture Generator ===")
    print("1) Generate Slide Content (.md for slides)\n2) Generate Professor Script (.md for narration)")

    choice = input("Enter your choice (1/2): ").strip()

    if choice == "1":
        topic = input("Enter the topic for the lecture: ").strip()
        print("Select length:\n1. Short (Revision)\n2. Detailed\n3. Coursework")
        length_choice = input("Enter your choice (1/2/3): ").strip()
        length_map = {"1": "Short (Revision)", "2": "Detailed", "3": "Coursework"}
        length = length_map.get(length_choice, "Detailed")

        script = generate_slide_content(topic, length)
        filename = f"Lecture_{topic.replace(' ', '_')}_{length.replace(' ', '_')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(script)
        
        print(f"\n✅ Slide content generated and saved as {filename}.")
        print("\nPreview:\n")
        print(script[:1500] + "\n\n[Truncated]")

    elif choice == "2":
        md_file = input("Enter the path to the slide .md file: ").strip()
        if not os.path.exists(md_file):
            print("❌ File not found.")
            return

        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()

        topic_line = next((line for line in md_content.split('\n') if line.startswith('# Title:')), "Unknown Topic")
        topic = topic_line.replace('# Title:', '').strip()

        persona_map = {
            "1": "enthusiastic professor",
            "2": "calm and clear mentor",
            "3": "friendly senior explaining with stories",
            "4": "strict examiner, focused and concise"
        }

        print("Choose professor persona:\n1) Enthusiastic Professor\n2) Calm Mentor\n3) Friendly Senior\n4) Strict Examiner")
        persona_choice = input("Enter choice (default 1): ").strip() or "1"
        persona = persona_map.get(persona_choice, persona_map["1"])

        script = generate_professor_script(topic, md_content, persona)

        filename = md_file.replace(".md", "_ProfessorScript.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(script)

        print(f"\n✅ Professor script generated and saved as {filename}.")
        print("\nPreview:\n")
        print(script[:1500] + "\n\n[Truncated]")

    else:
        print("❌ Invalid choice. Please select 1 or 2.")

if __name__ == "__main__":
    main()
