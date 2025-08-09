import json
import re
import streamlit as st
from google.generativeai import GenerativeModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from datetime import datetime
import xml.etree.ElementTree as ET

def export_quiz_to_pdf(quiz_data, quiz_topic, user_answers=None, score=None):
    """Export quiz to PDF format with enhanced formatting"""
    try:
        filename = f"Quiz_{quiz_topic.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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
        
        # Quiz metadata
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        story.append(Paragraph(f"Total Questions: {len(quiz_data)}", styles['Normal']))
        
        if score is not None:
            percentage = (score/len(quiz_data)*100) if len(quiz_data) > 0 else 0
            story.append(Paragraph(f"Score: {score}/{len(quiz_data)} ({percentage:.1f}%)", styles['Heading2']))
        
        story.append(Spacer(1, 20))
        
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
                
                if is_correct and user_selected:
                    style_text = f"<b>{letter}. {option} ✓ (Correct - Your Answer)</b>"
                elif is_correct:
                    style_text = f"<b>{letter}. {option} ✓ (Correct Answer)</b>"
                elif user_selected:
                    style_text = f"{letter}. {option} ✗ (Your Answer)"
                else:
                    style_text = f"{letter}. {option}"
                    
                story.append(Paragraph(style_text, styles['Normal']))
            
            # Explanation
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>Explanation:</b> {q['explanation']}", styles['Normal']))
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return filename
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def export_quiz_to_moodle_xml(quiz_data, quiz_topic):
    """Export quiz to Moodle XML format with proper escaping"""
    try:
        quiz_elem = ET.Element("quiz")
        
        for i, q in enumerate(quiz_data):
            question_elem = ET.SubElement(quiz_elem, "question", type="multichoice")
            
            # Question name
            name_elem = ET.SubElement(question_elem, "name")
            text_elem = ET.SubElement(name_elem, "text")
            text_elem.text = f"{quiz_topic} - Question {i+1}"
            
            # Question text
            questiontext_elem = ET.SubElement(question_elem, "questiontext", format="html")
            text_elem = ET.SubElement(questiontext_elem, "text")
            text_elem.text = f"<![CDATA[<p>{q['question']}</p>]]>"
            
            # General feedback (explanation)
            generalfeedback_elem = ET.SubElement(question_elem, "generalfeedback", format="html")
            text_elem = ET.SubElement(generalfeedback_elem, "text")
            text_elem.text = f"<![CDATA[<p>{q['explanation']}</p>]]>"
            
            # Default grade
            defaultgrade_elem = ET.SubElement(question_elem, "defaultgrade")
            defaultgrade_elem.text = "1"
            
            # Penalty
            penalty_elem = ET.SubElement(question_elem, "penalty")
            penalty_elem.text = "0.1"
            
            # Hidden
            hidden_elem = ET.SubElement(question_elem, "hidden")
            hidden_elem.text = "0"
            
            # Answer numbering
            answernumbering_elem = ET.SubElement(question_elem, "answernumbering")
            answernumbering_elem.text = "abc"
            
            # Options
            for j, option in enumerate(q['options']):
                fraction = "100" if chr(65 + j) == q['correct'] else "0"
                answer_elem = ET.SubElement(question_elem, "answer", 
                                          fraction=fraction, format="html")
                text_elem = ET.SubElement(answer_elem, "text")
                text_elem.text = f"<![CDATA[<p>{option}</p>]]>"
                
                # Feedback for each answer
                feedback_elem = ET.SubElement(answer_elem, "feedback", format="html")
                feedback_text_elem = ET.SubElement(feedback_elem, "text")
                if chr(65 + j) == q['correct']:
                    feedback_text_elem.text = "<![CDATA[<p>Correct!</p>]]>"
                else:
                    feedback_text_elem.text = "<![CDATA[<p>Incorrect.</p>]]>"
        
        filename = f"Quiz_{quiz_topic.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        tree = ET.ElementTree(quiz_elem)
        ET.indent(tree, space="  ", level=0)  # Pretty formatting
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        return filename
    except Exception as e:
        st.error(f"Error creating Moodle XML: {str(e)}")
        return None

def export_quiz_to_json(quiz_data, quiz_topic, metadata=None, user_answers=None, score=None):
    """Export quiz to JSON format with comprehensive data"""
    try:
        export_data = {
            "quiz_info": {
                "topic": quiz_topic,
                "created_at": datetime.now().isoformat(),
                "total_questions": len(quiz_data),
                "version": "1.0"
            },
            "metadata": metadata or {},
            "questions": quiz_data
        }
        
        # Add results if available
        if user_answers is not None and score is not None:
            export_data["results"] = {
                "score": score,
                "total_questions": len(quiz_data),
                "percentage": (score/len(quiz_data)*100) if len(quiz_data) > 0 else 0,
                "user_answers": user_answers,
                "completed_at": datetime.now().isoformat()
            }
        
        filename = f"Quiz_{quiz_topic.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        return filename
    except Exception as e:
        st.error(f"Error creating JSON: {str(e)}")
        return None

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