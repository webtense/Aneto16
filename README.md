# Libro a Audio

Aplicación web que convierte libros en formato **TXT**, **DOCX** o **DOC** en archivos de audio **MP3**. Utiliza [Flask](https://flask.palletsprojects.com/) para la interfaz y [edge-tts](https://pypi.org/project/edge-tts/) para generar voces con entonación natural.

## Requisitos
- Python 3.10 o superior

## Instalación
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Necesitas tener instalado **ffmpeg** en tu sistema para que `pydub` pueda combinar los fragmentos de audio. Para archivos `.doc` se usa [textract](https://textract.readthedocs.io/), que requiere utilidades como `antiword` en el sistema.

## Uso
```bash
python app.py
```
Luego abre `http://localhost:5000` en tu navegador y:
1. Sube un archivo `.txt`, `.docx` o `.doc`.
2. Elige voz **femenina** o **masculina**, la **velocidad** y el **estilo** (neutral, narración o alegre).
3. Indica la carpeta donde se guardarán los MP3.
4. Presiona **Procesar** y observa la barra de progreso con el tiempo estimado.

El libro se divide en capítulos y se genera un archivo MP3 por cada uno en la carpeta indicada.
