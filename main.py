from docx import Document
from PyPDF2 import PdfReader
from gtts import gTTS
from tqdm import tqdm
import os
import tempfile
from pydub import AudioSegment

def docx_to_text(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in tqdm(doc.paragraphs, desc="Leyendo DOCX", unit="párrafo")])

def pdf_to_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in tqdm(reader.pages, desc="Leyendo PDF", unit="página"):
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def text_to_speech_chunks(text, output_file="output.mp3", lang="es"):
    print("Convirtiendo texto a audio por fragmentos...")

    tts = gTTS(text=text, lang=lang)
    temp_path = tempfile.mktemp(suffix=".mp3")
    tts.save(temp_path)
    file = AudioSegment.from_mp3(temp_path)
    file.export(output_file, format="mp3")

    print(f"Audio final guardado como: {output_file}")

def convert_file_to_audio(file_path):
    if file_path.endswith(".docx"):
        text = docx_to_text(file_path)
    elif file_path.endswith(".pdf"):
        text = pdf_to_text(file_path)
    else:
        raise ValueError("Formato no compatible. Solo se aceptan .docx y .pdf")

    if text.strip():
        output_name = os.path.splitext(os.path.basename(file_path))[0] + ".mp3"
        text_to_speech_chunks(text, output_file=output_name)
    else:
        print("No se pudo extraer texto legible del archivo.")

if __name__ == "__main__":
    archivo = "marcos_ana.pdf"  # Cambia por tu archivo
    convert_file_to_audio(archivo)
