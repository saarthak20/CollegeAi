import os
import subprocess
from pdf2image import convert_from_path
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from pydub.utils import mediainfo

def convert_pptx_to_pdf(pptx_file):
    pdf_file = pptx_file.replace('.pptx', '.pdf')
    #subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", pptx_file], check=True)
    return pdf_file

def convert_pdf_to_images(pdf_file, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    images = convert_from_path(pdf_file, dpi=200)
    image_paths = []
    for idx, image in enumerate(images):
        path = os.path.join(output_folder, f"slide_{idx+1}.png")
        image.save(path, "PNG")
        image_paths.append(path)
    return image_paths

def get_audio_duration(audio_file):
    info = mediainfo(audio_file)
    duration = float(info['duration'])
    return duration

def generate_video(slide_images, audio_file, output_file):
    audio_duration = get_audio_duration(audio_file)
    num_slides = len(slide_images)
    slide_duration = audio_duration / num_slides

    clips = []
    for image_path in slide_images:
        clip = ImageClip(image_path).with_duration(slide_duration)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_file)
    video = video.with_audio(audio)

    video.write_videofile(output_file, fps=1)

def main():
    print("=== Lecture Video Generator ===")
    pptx_file = input("Enter the path to your slides .pptx file: ").strip()
    audio_file = input("Enter the path to your TTS .wav file: ").strip()

    print("Converting PPTX to PDF...")
    pdf_file = convert_pptx_to_pdf(pptx_file)

    print("Converting PDF to slide images...")
    slide_images = convert_pdf_to_images(pdf_file, output_folder="slides_images")

    output_file = pptx_file.replace('.pptx', '.mp4')
    print("Generating video...")
    generate_video(slide_images, audio_file, output_file)

    print(f"Lecture video saved as {output_file}")

if __name__ == "__main__":
    main()
