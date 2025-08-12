import os
import asyncio
from typing import Set

from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from docx import Document
import edge_tts


ALLOWED_EXTENSIONS: Set[str] = {"txt", "docx"}
MAX_FILE_SIZE_MB = 16

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_MB * 1024 * 1024


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(par.text for par in doc.paragraphs)


async def synthesize(
    text: str,
    out_path: str,
    voice: str = "es-ES-SergioNeural",
    style: str = "newscast-casual",
):
    communicate = edge_tts.Communicate(text, voice=voice, style=style)
    await communicate.save(out_path)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("archivo")
        if file is None or file.filename == "" or not allowed_file(file.filename):
            return "Formato no soportado", 400

        output_dir = secure_filename(request.form.get("salida") or "salidas")
        os.makedirs(output_dir, exist_ok=True)

        temp_dir = "tmp"
        os.makedirs(temp_dir, exist_ok=True)
        filename = secure_filename(file.filename)
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)

        if filename.endswith(".txt"):
            text = read_txt(temp_path)
        else:  # filename is guaranteed to end with .txt or .docx
            text = read_docx(temp_path)

        base_name = os.path.splitext(filename)[0]
        output_file = os.path.join(output_dir, f"{base_name}.mp3")
        asyncio.run(synthesize(text, output_file))

        os.remove(temp_path)

        return redirect(url_for("exito", carpeta=output_dir))

    return render_template("index.html")


@app.route("/exito")
def exito():
    carpeta = request.args.get("carpeta")
    return render_template("exito.html", carpeta=carpeta)


if __name__ == "__main__":
    app.run()
