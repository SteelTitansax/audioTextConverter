    from docx import Document
from PyPDF2 import PdfReader
from gtts import gTTS
import os

def docx_to_text(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def pdf_to_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def text_to_speech(text, output_file="output.mp3", lang="es"):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_file)
    print(f"Audio saved as: {output_file}")

def convert_file_to_audio(file_path):
    if file_path.endswith(".docx"):
        text = docx_to_text(file_path)
    elif file_path.endswith(".pdf"):
        text = pdf_to_text(file_path)
    else:
        raise ValueError("Format not compatible. Only .docx and .pdf are accepted")
    
    if text.strip():
        output_name = os.path.splitext(os.path.basename(file_path))[0] + ".mp3"
        text_to_speech(text, output_file=output_name)
    else:
        print("Not readable text.")

if __name__ == "__main__":
    archivo = "ejemplo.pdf"  
    convert_file_to_audio(archivo)
