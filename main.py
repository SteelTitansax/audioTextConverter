from docx import Document
from PyPDF2 import PdfReader
from TTS.api import TTS
from tqdm import tqdm
from pydub import AudioSegment
import os
import tempfile
import time

# Cargar el modelo de TTS (puedes cambiar el nombre por otro si deseas)
tts = TTS(model_name="tts_models/es/mai/tacotron2-DDC", progress_bar=True, gpu=False)

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

def dividir_texto(texto, max_length=4000):
    palabras = texto.split()
    fragmentos, fragmento = [], ""
    for palabra in palabras:
        if len(fragmento) + len(palabra) + 1 < max_length:
            fragmento += palabra + " "
        else:
            fragmentos.append(fragmento.strip())
            fragmento = palabra + " "
    if fragmento:
        fragmentos.append(fragmento.strip())
    return fragmentos

def generar_audio_coqui(texto, path_temp):
    try:
        tts.tts_to_file(text=texto, file_path=path_temp)
        return True
    except Exception as e:
        print(f"Error al generar audio con Coqui TTS: {e}")
        return False

def text_to_speech_chunks(text, output_file="output.mp3"):
    fragmentos = dividir_texto(text)
    print(f"Convirtiendo texto a audio por fragmentos... Total: {len(fragmentos)}")

    audio_final = AudioSegment.empty()

    for i, fragmento in enumerate(tqdm(fragmentos, desc="Procesando fragmentos", unit="fragmento")):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            exito = generar_audio_coqui(fragmento, temp_audio.name)
            if exito:
                audio = AudioSegment.from_wav(temp_audio.name)
                audio_final += audio
            else:
                print(f"Error en el fragmento {i}, se omitirá.")
            os.remove(temp_audio.name)
            time.sleep(0.1)

    audio_final.export(output_file, format="mp3")
    print(f"Audio final guardado como: {output_file}")

def convert_file_to_audio(file_path):
    if file_path.endswith(".docx"):
        text = docx_to_text(file_path)
    elif file_path.endswith(".pdf"):
        text = pdf_to_text(file_path)
    else:
        raise ValueError("Formato no compatible. Solo se aceptan .docx y .pdf")

    if text.strip():
        output_name = os.path.splitext(os.path.basename(file_path))[0] + "_coqui.mp3"
        text_to_speech_chunks(text, output_file=output_name)
    else:
        print("No se pudo extraer texto legible del archivo.")

if __name__ == "__main__":
    archivo = input("Introduce la ruta del archivo .docx o .pdf: ").strip()
    convert_file_to_audio(archivo)
