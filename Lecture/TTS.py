from google import genai
from google.genai import types
import wave

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def generate_tts_from_markdown(md_file, voice_name="Kore"):
    client = genai.Client()

    with open(md_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Optional: truncate for safety
    if len(text) > 6000:
        print("Note: Truncating text to first 6000 characters for TTS.")
        text = text[:6000]

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
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

    output_file = md_file.replace('Lecture', 'Lecture_TTS').replace('.md', '.wav')
    wave_file(output_file, data)
    print(f"TTS audio saved as {output_file} using voice '{voice_name}'.")

if __name__ == "__main__":
    print("=== Gemini 2.5 Flash TTS Generator ===")
    md_file = input("Enter path to your lecture markdown file: ").strip()
    print("Available voices: Kore, Puck, Leda, Zephyr, Puck, Charon, Fenrir, Aoede, etc.")
    voice = input("Enter voice name to use (default 'Kore'): ").strip() or "Kore"
    generate_tts_from_markdown(md_file, voice_name=voice)
