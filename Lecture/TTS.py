from google import genai
from google.genai import types
import wave
import re
import os

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def generate_tts_per_slide(md_file, voice_name="Kore"):
    client = genai.Client()

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split at each slide marker (## )
    sections = re.split(r'\n## ', content)

    # Preprocess to ensure the first section has a clean title
    cleaned_sections = []
    for idx, section in enumerate(sections):
        lines = section.strip().split('\n')
        if idx == 0:
            # Try to extract title or fallback
            title_match = re.match(r'# Title: (.+)', lines[0])
            section_title = title_match.group(1) if title_match else "Introduction"
            section_text = '\n'.join(lines[1:]).strip()
        else:
            section_title = lines[0].strip()
            section_text = '\n'.join(lines[1:]).strip()
        
        # Remove empty sections
        if section_text:
            cleaned_sections.append((section_title, section_text))

    for idx, (section_title, section_text) in enumerate(cleaned_sections):
        print(f"Generating TTS for Slide {idx+1}: {section_title}")

        # Truncate to 6000 chars if needed
        if len(section_text) > 6000:
            section_text = section_text[:6000]
            print(f"Note: Truncated Slide {idx+1} text to 6000 characters.")

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=section_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                ),
            )
        )

        data = response.candidates[0].content.parts[0].inline_data.data

        output_file = f"slide_{idx+1}.wav"
        wave_file(output_file, data)
        print(f"✅ Saved: {output_file} for Slide {idx+1}: {section_title}")

if __name__ == "__main__":
    print("=== Gemini Advanced TTS Per Slide Generator ===")
    md_file = input("Enter the path to your markdown lecture file: ").strip()
    print("Available voices: Kore, Puck, Leda, Zephyr, Charon, Fenrir, Aoede, etc.")
    voice = input("Enter voice name (default 'Kore'): ").strip() or "Kore"
    generate_tts_per_slide(md_file, voice_name=voice)
