import os
import asyncio
from flask import Flask, request, render_template, redirect, url_for
from docx import Document
import edge_tts
from pydub import AudioSegment

app = Flask(__name__)

def read_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(par.text for par in doc.paragraphs)

CHUNK_SIZE = 3000  # characters
CHUNK_DELAY = 1    # seconds

async def synthesize(
    text: str,
    out_path: str,
    voice: str = "es-ES-SergioNeural",
    rate: str = "0%",
    style: str = "newscast-casual",
):
    chunks = [text[i : i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    temp_files = []
    for idx, chunk in enumerate(chunks):
        temp_file = f"temp_{idx}.mp3"
        communicate = edge_tts.Communicate(chunk, voice=voice, style=style, rate=rate)
        await communicate.save(temp_file)
        temp_files.append(temp_file)
        await asyncio.sleep(CHUNK_DELAY)

    audio = AudioSegment.empty()
    for f in temp_files:
        audio += AudioSegment.from_file(f)
        os.remove(f)
    audio.export(out_path, format="mp3")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['archivo']
        output_dir = request.form.get('salida') or 'salidas'
        os.makedirs(output_dir, exist_ok=True)
        gender = request.form.get('voz', 'femenina')
        speed = request.form.get('velocidad', '0')

        voice_map = {
            'femenina': 'es-ES-ElviraNeural',
            'masculina': 'es-ES-SergioNeural',
        }
        rate_map = {
            'lenta': '-20%',
            'normal': '0%',
            'rapida': '+20%',
        }

        temp_dir = 'tmp'
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)

        if file.filename.endswith('.txt'):
            text = read_txt(temp_path)
        elif file.filename.endswith('.docx'):
            text = read_docx(temp_path)
        else:
            return 'Formato no soportado', 400

        base_name = os.path.splitext(file.filename)[0]
        output_file = os.path.join(output_dir, f'{base_name}.mp3')
        voice_id = voice_map.get(gender, 'es-ES-ElviraNeural')
        rate_val = rate_map.get(speed, '0%')
        asyncio.run(synthesize(text, output_file, voice=voice_id, rate=rate_val))

        return redirect(url_for('exito', carpeta=output_dir))

    return render_template('index.html')

@app.route('/exito')
def exito():
    carpeta = request.args.get('carpeta')
    return render_template('exito.html', carpeta=carpeta)

if __name__ == '__main__':
    app.run(debug=True)
