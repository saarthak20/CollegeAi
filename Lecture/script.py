from google.generativeai import GenerativeModel

def translate_text(text, target_language="Hindi"):
    prompt = f"""
Translate the following professor lecture narration to {target_language}. 
Keep the formatting (Markdown sections like ## Title, ## Introduction, etc.) the same.
Do not add extra commentary.

TEXT:
\"\"\"
{text}
\"\"\"
"""
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def generate_slide_content(topic, length="Detailed", context="", language="English"):
    prompt = f"""
You are an expert educator tasked with creating clear, structured slide content for a lecture on '{topic}'.
Use the context below to improve factual accuracy and relevance:
Generate this in: {language}

CONTEXT:
\"\"\"
{context}
\"\"\"

Use the following Markdown structure:

## Title: {topic}

## Introduction
<concise, clear intro>

## Section 1: <Title>
<clear explanation>

## Section 2: <Title>
<clear explanation>

## Example
<real-world example>

## Python Code Example (if applicable)
<code snippet or explanation>

## Summary
- Bullet 1
- Bullet 2
- Bullet 3

Keep it factual, beginner-friendly, and slide-ready.
Length: {length}.
"""
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def generate_professor_script(topic, md_content, persona="enthusiastic professor", context="", language="English"):
    prompt = f"""
You are an {persona} giving a lecture on '{topic}' to college students in English.

Use the slide content and context provided below to generate a personal, spoken script.
Add light jokes, questions, transitions, and make it sound like a real teacher.

SLIDE CONTENT:
\"\"\"
{md_content}
\"\"\"

CONTEXT (if helpful):
\"\"\"
{context}
\"\"\"

Return a narration with the same section headers so each section aligns with a slide.
Use the same ## section formatting for each.
"""
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    english_script = response.text

    # Add ## Title manually if not present
    if "## Title" not in english_script:
        english_script = f"## Title: {topic}\n\n" + english_script.strip()

    if language.strip().lower() != "english":
        translated_script = translate_text(english_script, target_language=language)
        return translated_script
    else:
        return english_script
