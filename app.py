import os
import re
import asyncio
from flask import Flask, request, render_template, redirect, url_for
from docx import Document
import edge_tts

app = Flask(__name__)

def read_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(par.text for par in doc.paragraphs)

def split_into_chapters(text: str):
    pattern = r'(?i)(?=cap[ií]tulo\s+\d+\b|chapter\s+\d+\b)'
    chapters = re.split(pattern, text)
    return [c.strip() for c in chapters if c.strip()]

async def synthesize(text: str, out_path: str, voice: str = "es-ES-SergioNeural", style: str = "newscast-casual"):
    communicate = edge_tts.Communicate(text, voice=voice, style=style)
    await communicate.save(out_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['archivo']
        output_dir = request.form.get('salida') or 'salidas'
        os.makedirs(output_dir, exist_ok=True)

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

        chapters = split_into_chapters(text)
        for idx, chapter in enumerate(chapters, start=1):
            output_file = os.path.join(output_dir, f'capitulo_{idx}.mp3')
            asyncio.run(synthesize(chapter, output_file))

        return redirect(url_for('exito', carpeta=output_dir))

    return render_template('index.html')

@app.route('/exito')
def exito():
    carpeta = request.args.get('carpeta')
    return render_template('exito.html', carpeta=carpeta)

if __name__ == '__main__':
    app.run(debug=True)
