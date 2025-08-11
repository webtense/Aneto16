# Libro a Audio

Aplicación web sencilla para convertir libros en formato **TXT** o **DOCX** en un archivo de audio **MP3**. Utiliza [Flask](https://flask.palletsprojects.com/) para la interfaz y [edge-tts](https://pypi.org/project/edge-tts/) para generar voces con entonación natural.

## Requisitos
- Python 3.10 o superior

## Instalación
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Necesitas tener instalado **ffmpeg** en tu sistema para que `pydub` pueda combinar los fragmentos de audio.

## Uso
```bash
python app.py
```
Luego abre `http://localhost:5000` en tu navegador y:
1. Sube un archivo `.txt` o `.docx`.
2. Elige voz **femenina** o **masculina** y la velocidad de lectura.
3. Indica la carpeta donde se guardará el MP3.
4. Presiona **Procesar** y observa la barra de progreso con el tiempo estimado.

El libro completo se guarda como un único archivo MP3 con el mismo nombre del archivo de entrada en la carpeta elegida.
