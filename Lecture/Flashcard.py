import json
import re
from google.generativeai import GenerativeModel

def clean_json_response(response_text):
    response_text = response_text.strip()
    json_pattern = r'```(?:json)?\s*(.*?)\s*```'
    match = re.search(json_pattern, response_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    array_pattern = r'(\[.*\])'
    match = re.search(array_pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_text

def generate_flashcards(topic, num_cards=10, difficulty="Medium", language="English", slide_md=None, context=None):
    slide_md = slide_md or "Not provided"
    context = context or "Not provided"

    prompt = f"""
You are an expert educator creating concise and effective flashcards.

Topic: {topic}
Difficulty: {difficulty}
Language: {language}

Slide Content:
\"\"\"{slide_md}\"\"\"

Additional Context:
\"\"\"{context}\"\"\"

Generate {num_cards} flashcards in this exact JSON format:

[
  {{
    "front": "Question or prompt text",
    "back": "Answer or explanation text"
  }}
]

Rules:
- Keep front short and clear.
- Back should be concise, factual, and in the chosen language.
- Avoid numbering or extra formatting.
- Return ONLY the JSON array.
"""

    try:
        model = GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        if not response or not response.text:
            print("Error: Empty response from model")
            return []

        cleaned_text = clean_json_response(response.text)
        flashcards = json.loads(cleaned_text)

        if isinstance(flashcards, list) and all("front" in fc and "back" in fc for fc in flashcards):
            return flashcards
        else:
            print("Error: Invalid flashcard format")
            return []
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return []
