from youtube_transcript_api import YouTubeTranscriptApi
import fitz  # PyMuPDF
from google.generativeai import GenerativeModel
from urllib.parse import urlparse, parse_qs
import os

def extract_youtube_transcript(youtube_url):
    print("Extracting YouTube transcript...")
    video_id = parse_qs(urlparse(youtube_url).query).get('v')
    if not video_id:
        # Handle youtu.be URLs
        video_id = youtube_url.split("/")[-1]
    else:
        video_id = video_id[0]
    ytt_api = YouTubeTranscriptApi()
    fetched = ytt_api.fetch(video_id)
    transcript = fetched.to_raw_data()  # 🔥 Fix here!
    text = " ".join([t['text'] for t in transcript])
    return text

def extract_pdf_text(pdf_path):
    print("Extracting PDF text...")
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def summarize_text(text, topic):
    prompt = f"""
You are an expert educator. Summarize the following extracted content into a clear, beginner-friendly, structured Markdown summary for revision:

Topic: {topic}

CONTENT:
\"\"\"
{text[:12000]}
\"\"\"

STRUCTURE:
# Title: <Topic>

## Introduction
<Concise introduction>

## Key Points
- point 1
- point 2
- point 3

## Summary
<Summary paragraph>

Keep it clean, clear, and structured in Markdown. Do not add any unnecessary sections.
"""
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def main():
    print("=== collegeAi Context Extractor ===")
    print("Choose input type:\n1) YouTube URL\n2) PDF Notes")
    choice = input("Enter your choice (1/2): ").strip()

    if choice == "1":
        youtube_url = input("Enter the YouTube video URL: ").strip()
        topic = input("Enter the topic name for context summary: ").strip()
        extracted_text = extract_youtube_transcript(youtube_url)

    elif choice == "2":
        pdf_path = input("Enter the path to your PDF notes: ").strip()
        if not os.path.exists(pdf_path):
            print("❌ File not found.")
            return
        topic = input("Enter the topic name for context summary: ").strip()
        extracted_text = extract_pdf_text(pdf_path)

    else:
        print("❌ Invalid choice.")
        return

    summarized_md = summarize_text(extracted_text, topic)
    filename = f"ContextSummary_{topic.replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(summarized_md)

    print(f"\n✅ Context summary saved as {filename}.")
    print("\nPreview:\n")
    print(summarized_md[:1500] + "\n\n[Truncated]")

if __name__ == "__main__":
    main()
