import json
import re
from google.generativeai import GenerativeModel

def clean_json_response(response_text):
    """
    Clean the response text to extract valid JSON from markdown code blocks or other formatting.
    """
    # Remove markdown code blocks
    response_text = response_text.strip()
    
    # Pattern to match JSON inside markdown code blocks
    json_pattern = r'```(?:json)?\s*(.*?)\s*```'
    match = re.search(json_pattern, response_text, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # If no code blocks found, try to find JSON array pattern
    array_pattern = r'(\[.*\])'
    match = re.search(array_pattern, response_text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # Return original if no patterns match
    return response_text

def generate_quiz(topic, slide_md=None, context=None, num_questions=5, difficulty="Medium"):
    """
    Generates MCQ quiz questions using Gemini based on topic, slides, and context.
    Returns a Python list of dicts: [{question, options, correct, explanation}, ...]
    """
    slide_md = slide_md or "Not provided"
    context = context or "Not provided"

    prompt = f"""
You are an expert educator creating a multiple-choice quiz.

Topic: {topic}

Slide Content:
\"\"\"{slide_md}\"\"\"

Context Summary:
\"\"\"{context}\"\"\"

Generate {num_questions} {difficulty} MCQs in the following strict JSON format.
Return ONLY the JSON array, no additional text or formatting:

[
  {{
    "question": "Question text here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": "B",
    "explanation": "Short explanation why B is correct"
  }}
]

Rules:
- Keep questions clear and unambiguous.
- Only one correct answer per question.
- Match difficulty requested.
- Ensure factual accuracy.
- Return ONLY valid JSON, no markdown formatting or extra text.
"""

    try:
        model = GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            print("Error: Empty response from model")
            return []
        
        # Clean the response text
        cleaned_text = clean_json_response(response.text)
        
        # Parse JSON
        quiz_data = json.loads(cleaned_text)
        
        # Validate structure
        if isinstance(quiz_data, list) and all(isinstance(q, dict) for q in quiz_data):
            # Validate each question has required fields
            for i, question in enumerate(quiz_data):
                required_fields = ["question", "options", "correct", "explanation"]
                if not all(field in question for field in required_fields):
                    print(f"Warning: Question {i+1} missing required fields")
                    continue
                
                # Validate options is a list with 4 items
                if not isinstance(question["options"], list) or len(question["options"]) != 4:
                    print(f"Warning: Question {i+1} doesn't have exactly 4 options")
                    continue
                
                # Validate correct answer is A, B, C, or D
                if question["correct"] not in ["A", "B", "C", "D"]:
                    print(f"Warning: Question {i+1} has invalid correct answer format")
                    continue
            
            return quiz_data
        else:
            print("Error: Invalid quiz format - not a list of dictionaries")
            return []
            
    except json.JSONDecodeError as e:
        print(f"Error parsing quiz JSON: {e}")
        print(f"Cleaned text: {cleaned_text[:500]}...")  # Show first 500 chars for debugging
        return []
    except Exception as e:
        print(f"Error generating quiz: {e}")
        print(f"Raw model output: {response.text if 'response' in locals() else 'No response'}")
        return []

# ------------------ TEST ------------------
if __name__ == "__main__":
    topic = "Introduction to Machine Learning"
    slide_md = """
## Title: Introduction to Machine Learning
## Introduction
Machine learning is a field of AI focused on building systems that learn from data.
## Section 1: Types
- Supervised Learning
- Unsupervised Learning
- Reinforcement Learning
## Summary
- ML learns from data
- Three main types
"""
    context = "ML is used in spam filtering, recommendation systems, and autonomous driving."
    quiz = generate_quiz(topic, slide_md, context, num_questions=3, difficulty="Easy")
    print(json.dumps(quiz, indent=2, ensure_ascii=False))