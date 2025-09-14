from moviepy.editor import VideoFileClip
import os

def compress_video(input_path, output_path, quality="720p"):
    """
    Comprime un video a la calidad deseada.
    quality: "480p", "720p", "1080p" o "144p"
    """
    clip = VideoFileClip(input_path)
    
    # Determinar resolución objetivo
    resolutions = {
        "144p": (256, 144),
        "480p": (854, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
    }
    target_res = resolutions.get(quality, (1280, 720))
    
    # Redimensionar
    clip_resized = clip.resize(newsize=target_res)
    
    # Guardar video comprimido
    clip_resized.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        threads=4,
        preset="ultrafast"
    )
    clip.close()
    clip_resized.close()

def extract_audio(input_path, output_path):
    """
    Extrae el audio de un video y lo guarda en formato mp3
    """
    clip = VideoFileClip(input_path)
    clip.audio.write_audiofile(output_path, codec="mp3")
    clip.close()
