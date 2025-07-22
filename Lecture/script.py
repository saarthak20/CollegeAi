from google.generativeai import GenerativeModel
import os

def generate_lecture_script(topic, length="Detailed"):
    """
    Generates a structured lecture script on the given topic with the specified length using Gemini.
    Returns the script as a Markdown string for easy reading and future slide generation.
    """
    prompt = f"""
You are an expert teacher. Generate a structured, clear, beginner-friendly lecture script on the topic: '{topic}'.
The lecture should be {length}.
Use the following Markdown format for the output:

# Title: <title>
## Introduction
<concise engaging introduction>

## Section 1: <Section Title>
<explanation>

## Section 2: <Section Title>
<explanation>

## Example
<real-life example related to the topic>

## Python Code Example (if applicable)
<code block or explanation>

## Summary
- Bullet point 1
- Bullet point 2
- Bullet point 3

Keep the tone engaging, easy to read aloud, and clear for students.
"""

    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text

def main():
    print("=== Lecture Generator (Gemini) ===")
    topic = input("Enter the topic for the lecture: ").strip()
    print("Select length:\n1. Short (Revision)\n2. Detailed\n3. Coursework")
    choice = input("Enter your choice (1/2/3): ").strip()
    length_map = {"1": "Short (Revision)", "2": "Detailed", "3": "Coursework"}
    length = length_map.get(choice, "Detailed")
    
    script = generate_lecture_script(topic, length)
    
    filename = f"Lecture_{topic.replace(' ', '_')}_{length.replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(script)
    
    print(f"\nLecture script generated and saved as {filename}.")
    print("\nPreview:\n")
    print(script[:1500] + "\n\n[Truncated]")

if __name__ == "__main__":
    main()
