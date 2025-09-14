from moviepy.editor import VideoFileClip
import os

def compress_video(input_path: str, output_path: str, quality: str = "720p"):
    """
    Comprime un video y ajusta su resolución según la calidad deseada.
    - input_path: ruta del video original
    - output_path: ruta del video comprimido
    - quality: "480p", "720p" o "1080p"
    """
    clip = VideoFileClip(input_path)

    # Ajustar resolución según la calidad
    if quality == "480p":
        clip_resized = clip.resize(height=480)
    elif quality == "720p":
        clip_resized = clip.resize(height=720)
    elif quality == "1080p":
        clip_resized = clip.resize(height=1080)
    else:
        clip_resized = clip  # Mantener original si no se reconoce

    # Guardar video comprimido
    clip_resized.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        threads=4,           # para procesar más rápido
        preset="fast",       # velocidad de codificación
        logger=None          # sin logs detallados
    )
    clip.close()
    if clip_resized != clip:
        clip_resized.close()

def extract_audio(input_path: str, output_path: str):
    """
    Extrae el audio de un video y lo guarda en formato mp3.
    - input_path: ruta del video original
    - output_path: ruta del archivo de audio
    """
    clip = VideoFileClip(input_path)
    if clip.audio is None:
        raise ValueError("El video no tiene pista de audio")
    clip.audio.write_audiofile(output_path, logger=None)
    clip.close()
