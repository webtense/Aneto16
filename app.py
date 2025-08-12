import os
import re
import asyncio
from flask import Flask, request, render_template, redirect, url_for
from docx import Document
import textract
import edge_tts
from pydub import AudioSegment

app = Flask(__name__)

def read_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(par.text for par in doc.paragraphs)

def read_doc(path: str) -> str:
    return textract.process(path).decode('utf-8')

def split_into_chapters(text: str) -> list[str]:
    pattern = re.compile(r"(?im)^cap[ií]tulo\s+\d+.*$|^chapter\s+\d+.*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if not matches:
        return [text]
    chapters = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapters.append(text[start:end].strip())
    return chapters

CHUNK_SIZE = 3000  # characters
CHUNK_DELAY = 1    # seconds

async def synthesize(
    text: str,
    out_path: str,
    voice: str = "es-ES-SergioNeural",
    rate: str = "0%",
    style: str = "general",
):
    chunks = [text[i : i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    temp_files = []
    for idx, chunk in enumerate(chunks):
        temp_file = f"temp_{idx}.mp3"
        style_arg = None if style == 'general' else style
        communicate = edge_tts.Communicate(chunk, voice=voice, style=style_arg, rate=rate)
        await communicate.save(temp_file)
        temp_files.append(temp_file)
        await asyncio.sleep(CHUNK_DELAY)

    audio = AudioSegment.empty()
    for f in temp_files:
        audio += AudioSegment.from_file(f)
        os.remove(f)
    audio.export(out_path, format="mp3")

async def synthesize_book(text: str, out_dir: str, base: str, voice: str, rate: str, style: str) -> list[str]:
    chapters = split_into_chapters(text)
    files = []
    for idx, chap in enumerate(chapters, start=1):
        out = os.path.join(out_dir, f"{base}_capitulo_{idx}.mp3")
        await synthesize(chap, out, voice=voice, rate=rate, style=style)
        files.append(os.path.basename(out))
    return files

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['archivo']
        output_dir = request.form.get('salida') or 'salidas'
        os.makedirs(output_dir, exist_ok=True)
        gender = request.form.get('voz', 'femenina')
        speed = request.form.get('velocidad', '0')
        style_sel = request.form.get('estilo', 'general')

        voice_map = {
            'femenina': 'es-ES-ElviraNeural',
            'masculina': 'es-ES-SergioNeural',
        }
        rate_map = {
            'lenta': '-20%',
            'normal': '0%',
            'rapida': '+20%',
        }
        style_map = {
            'general': 'general',
            'narracion': 'narration-professional',
            'alegre': 'cheerful',
        }

        temp_dir = 'tmp'
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)

        if file.filename.endswith('.txt'):
            text = read_txt(temp_path)
        elif file.filename.endswith('.docx'):
            text = read_docx(temp_path)
        elif file.filename.endswith('.doc'):
            text = read_doc(temp_path)
        else:
            return 'Formato no soportado', 400

        base_name = os.path.splitext(file.filename)[0]
        voice_id = voice_map.get(gender, 'es-ES-ElviraNeural')
        rate_val = rate_map.get(speed, '0%')
        style_val = style_map.get(style_sel, 'general')
        files = asyncio.run(synthesize_book(text, output_dir, base_name, voice_id, rate_val, style_val))
        return redirect(url_for('exito', carpeta=output_dir, archivos=','.join(files)))

    return render_template('index.html')

@app.route('/exito')
def exito():
    carpeta = request.args.get('carpeta')
    archivos = request.args.get('archivos', '')
    lista = archivos.split(',') if archivos else []
    return render_template('exito.html', carpeta=carpeta, archivos=lista)

if __name__ == '__main__':
    app.run(debug=True)
