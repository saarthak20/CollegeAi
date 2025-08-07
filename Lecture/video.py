import os
import subprocess
from pdf2image import convert_from_path
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from pydub.utils import mediainfo

def convert_pptx_to_pdf(pptx_file):
    """
    Convert PPTX to PDF using LibreOffice on macOS
    """
    if not os.path.exists(pptx_file):
        print(f"Error: File {pptx_file} does not exist")
        return None
    
    pdf_file = pptx_file.replace('.pptx', '.pdf')
    output_dir = os.path.dirname(os.path.abspath(pptx_file))
    
    # Check if LibreOffice is installed
    libreoffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    if not os.path.exists(libreoffice_path):
        print("LibreOffice not found. Install with: brew install --cask libreoffice")
        return None
    
    try:
        print(f"Converting {pptx_file} to PDF...")
        cmd = [
            libreoffice_path,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            pptx_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"Successfully converted to: {pdf_file}")
            return pdf_file
        else:
            print(f"Conversion failed: {result.stderr}")
            # Try alternative LibreOffice paths
            alternative_paths = [
                '/usr/bin/libreoffice',
                '/usr/local/bin/libreoffice',
                'libreoffice'  # If in PATH
            ]
            
            for alt_path in alternative_paths:
                try:
                    cmd[0] = alt_path
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        print(f"Successfully converted using {alt_path}")
                        return pdf_file
                except FileNotFoundError:
                    continue
            
            print("Could not find working LibreOffice installation")
            return None
            
    except subprocess.TimeoutExpired:
        print("Conversion timed out")
        return None
    except FileNotFoundError:
        print("LibreOffice not found. Please install with: brew install --cask libreoffice")
        return None
    except Exception as e:
        print(f"Error during conversion: {e}")
        return None


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



def main():
    print("=== Lecture Video Generator ===")
    pptx_file = input("Enter the path to your slides .pptx file: ").strip()

    print("Converting PPTX to PDF...")
    pdf_file = convert_pptx_to_pdf(pptx_file)

    print("Converting PDF to slide images...")
    slide_images = convert_pdf_to_images(pdf_file, output_folder="slides_images")

    output_file = pptx_file.replace('.pptx', '.mp4')


if __name__ == "__main__":
    main()