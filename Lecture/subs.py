import re
import wave
import os
from datetime import timedelta

def get_wav_duration(file_path):
    with wave.open(file_path, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    return duration

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    return str(td)[:-3].replace(".", ",").rjust(12, '0')

def generate_subtitles(md_file, output_srt="subtitles.srt"):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split sections based on markdown headers
    sections = re.split(r'\n## ', content)
    subtitles = []

    current_time = 0.0
    index = 1

    for i, sec in enumerate(sections):
        lines = sec.strip().split('\n')
        if not lines:
            continue

        if i == 0:
            # First section might contain "# Title"
            section_text = "\n".join(lines[1:]).strip()
        else:
            section_text = "\n".join(lines[1:]).strip()

        audio_file = f"slide_{i+1}.wav"
        if not os.path.exists(audio_file):
            print(f"❌ Missing audio file: {audio_file}, skipping...")
            continue

        duration = get_wav_duration(audio_file)
        start = format_timestamp(current_time)
        end = format_timestamp(current_time + duration)
        current_time += duration

        subtitles.append(f"{index}")
        subtitles.append(f"{start} --> {end}")
        subtitles.append(section_text.strip())
        subtitles.append("")  # blank line
        index += 1

    with open(output_srt, 'w', encoding='utf-8') as f:
        f.write("\n".join(subtitles))

    print(f"✅ Subtitles generated and saved as {output_srt}")

if __name__ == "__main__":
    print("=== Subtitle Generator ===")
    md_file = input("Enter the path to your professor narration .md file: ").strip()
    generate_subtitles(md_file)
