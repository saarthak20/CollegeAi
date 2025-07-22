import os
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from pydub import AudioSegment
import wave

def get_wav_duration(file_path):
    with wave.open(file_path, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    return duration

def generate_advanced_synced_video(slide_images, slide_audio_files, output_file):
    clips = []

    for img_path, audio_path in zip(slide_images, slide_audio_files):
        duration = get_wav_duration(audio_path)
        print(f"Slide: {img_path}, Duration: {duration:.2f} sec")

        clip = ImageClip(img_path).with_duration(duration)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    # Combine all audio files into one track
    combined_audio = AudioSegment.empty()
    for audio_file in slide_audio_files:
        segment = AudioSegment.from_wav(audio_file)
        combined_audio += segment

    combined_audio.export("combined_audio.wav", format="wav")
    audio_clip = AudioFileClip("combined_audio.wav")
    video = video.with_audio(audio_clip)

    video.write_videofile(output_file, fps=1)
    print(f"✅ Lecture video saved as {output_file}")

def main():
    print("=== Advanced Synced Lecture Video Generator ===")

    slides_folder = input("Enter path to folder containing slide images: ").strip()
    slide_images = sorted(
        [os.path.join(slides_folder, f) for f in os.listdir(slides_folder) if f.endswith(".png")]
    )

    slide_audio_files = sorted(
        [f for f in os.listdir(".") if f.startswith("slide_") and f.endswith(".wav")]
    )

    if len(slide_images) != len(slide_audio_files):
        print(f"❌ Mismatch: {len(slide_images)} slides but {len(slide_audio_files)} audio files.")
        print("Ensure the number of slides and audio segments match.")
        return

    output_file = "Lecture_Advanced_Synced.mp4"
    generate_advanced_synced_video(slide_images, slide_audio_files, output_file)

if __name__ == "__main__":
    main()
