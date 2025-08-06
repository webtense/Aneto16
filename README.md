# Libro a Audio

Aplicación web sencilla para convertir libros en formato **TXT** o **DOCX** en archivos de audio **MP3**, uno por capítulo. Utiliza [Flask](https://flask.palletsprojects.com/) para la interfaz y [edge-tts](https://pypi.org/project/edge-tts/) para generar voces con entonación natural.

## Requisitos
- Python 3.10 o superior

## Instalación
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso
```bash
python app.py
```
Luego abre `http://localhost:5000` en tu navegador y:
1. Sube un archivo `.txt` o `.docx`.
2. Indica la carpeta donde se guardarán los MP3.
3. Presiona **Procesar** y espera a que termine.

Cada capítulo detectado se guardará como `capitulo_1.mp3`, `capitulo_2.mp3`, etc. en la carpeta elegida.
