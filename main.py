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

def split_text(text, max_chars=4000):
    """Divide el texto en bloques de tamaño razonable para gTTS."""
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) + 1 < max_chars:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def text_to_speech_chunks(text, output_file="output.mp3", lang="es"):
    print("Convirtiendo texto a audio por fragmentos...")
    chunks = split_text(text)
    temp_files = []

    for i, chunk in enumerate(tqdm(chunks, desc="Convirtiendo a audio", unit="fragmento")):
        tts = gTTS(text=chunk, lang=lang)
        temp_path = tempfile.mktemp(suffix=".mp3")
        tts.save(temp_path)
        temp_files.append(temp_path)

    print("Unificando fragmentos de audio...")
    combined = AudioSegment.empty()
    for temp_file in temp_files:
        combined += AudioSegment.from_mp3(temp_file)
        os.remove(temp_file)

    combined.export(output_file, format="mp3")
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
    archivo = "ejemplo2.pdf"  # Cambia por tu archivo
    convert_file_to_audio(archivo)
