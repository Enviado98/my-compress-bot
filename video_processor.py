import ffmpeg
import os

# Resoluciones disponibles
RESOLUTIONS = {
    "144p": "256x144",
    "240p": "426x240",
    "360p": "640x360",
    "480p": "854x480",
    "720p": "1280x720",
    "1080p": "1920x1080"
}

def compress_video(input_path, output_path, quality="720p"):
    """
    Comprime un video a la resolución deseada usando ffmpeg.
    """
    target_res = RESOLUTIONS.get(quality, "1280x720")
    
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, vcodec='libx264', crf=28, preset='fast', s=target_res, acodec='aac', strict='experimental')
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error al comprimir video: {e}")

def extract_audio(input_path, output_path):
    """
    Extrae el audio de un video y lo guarda en mp3 usando ffmpeg.
    """
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format='mp3', acodec='libmp3lame', vn=None)
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error al extraer audio: {e}")
