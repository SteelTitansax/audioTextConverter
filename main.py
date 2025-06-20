import os
import textwrap
from gtts import gTTS
from docx import Document
import PyPDF2
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup

LIMITE_PALABRAS = 20000  

def extraer_texto_pdf(ruta):
    texto = ""
    with open(ruta, 'rb') as f:
        lector = PyPDF2.PdfReader(f)
        for pagina in lector.pages:
            texto += pagina.extract_text() + "\n"
    return texto

def extraer_texto_docx(ruta):
    doc = Document(ruta)
    return "\n".join([p.text for p in doc.paragraphs])

def extraer_texto_epub(ruta):
    texto = ""
    libro = epub.read_epub(ruta)
    for item in libro.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            texto += soup.get_text() + "\n"
    return texto

def dividir_en_volumenes(texto):
    palabras = texto.split()
    volumenes = []
    for i in range(0, len(palabras), LIMITE_PALABRAS):
        volumen = " ".join(palabras[i:i+LIMITE_PALABRAS])
        volumenes.append(volumen)
    return volumenes

def guardar_volumenes(volumenes, nombre_base):
    for i, vol in enumerate(volumenes):
        nombre_archivo = f"{nombre_base}_volumen_{i+1}.txt"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(vol)
        print(f"Guardado: {nombre_archivo}")

def obtener_siguiente_parte(base_nombre):
    i = 1
    while os.path.exists(f"{base_nombre}_parte_{i}.mp3"):
        i += 1
    return i

def convertir_a_audio(archivo_txt):
    with open(archivo_txt, "r", encoding="utf-8") as f:
        texto = f.read()

    trozos = textwrap.wrap(texto, 4000)
    base_salida = archivo_txt.replace(".txt", "")
    siguiente_parte = obtener_siguiente_parte(base_salida)

    for i, t in enumerate(trozos):
        tts = gTTS(text=t, lang='es', slow=False)
        salida = f"{base_salida}_parte_{siguiente_parte + i}.mp3"
        tts.save(salida)
        print(f"Audio guardado: {salida}")

    os.remove(archivo_txt)
    print(f"Archivo eliminado: {archivo_txt}")

def menu():
    while True:
        print("\n--- Conversor de Texto a Audio ---")
        print("1. Dividir PDF, DOCX o EPUB en volúmenes de texto")
        print("2. Convertir archivo .txt en audio")
        print("3. Salir")
        opcion = input("Elige una opción (1/2/3): ")

        if opcion == "1":
            ruta = input("Ruta al archivo PDF, DOCX o EPUB: ").strip()
            if not os.path.isfile(ruta):
                print("Archivo no encontrado.")
                continue

            texto = ""
            if ruta.lower().endswith(".pdf"):
                texto = extraer_texto_pdf(ruta)
            elif ruta.lower().endswith(".docx"):
                texto = extraer_texto_docx(ruta)
            elif ruta.lower().endswith(".epub"):
                texto = extraer_texto_epub(ruta)
            else:
                print("Formato no compatible.")
                continue

            if not texto.strip():
                print("El archivo no contiene texto legible.")
                continue

            volumenes = dividir_en_volumenes(texto)
            base = os.path.splitext(os.path.basename(ruta))[0]
            guardar_volumenes(volumenes, base)
            print(f"{len(volumenes)} volúmenes guardados.")

        elif opcion == "2":
            ruta_txt = input("Ruta al archivo .txt: ").strip()
            if not os.path.isfile(ruta_txt) or not ruta_txt.endswith(".txt"):
                print("Archivo inválido.")
                continue
            convertir_a_audio(ruta_txt)

        elif opcion == "3":
            print("Saliendo del programa.")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()
