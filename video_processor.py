from moviepy.editor import VideoFileClip
import os

def compress_video(input_path, output_path, quality="720p", progress_callback=None):
    """
    Comprime un video a la calidad deseada.
    quality: "144p", "480p", "720p", "1080p"
    progress_callback: función opcional para reportar progreso
    """
    clip = VideoFileClip(input_path)
    
    resolutions = {
        "144p": (256, 144),
        "480p": (854, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
    }
    target_res = resolutions.get(quality, (1280, 720))
    
    clip_resized = clip.resize(newsize=target_res)

    # MoviePy no tiene progreso real, simulamos 0-25-50-75-100%
    steps = [0, 25, 50, 75, 100]
    for pct in steps[:-1]:
        if progress_callback:
            progress_callback(pct)

    clip_resized.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        threads=4,
        preset="ultrafast",
        verbose=False,
        logger=None
    )

    if progress_callback:
        progress_callback(100)

    clip.close()
    clip_resized.close()


def extract_audio(input_path, output_path, progress_callback=None):
    """
    Extrae el audio de un video y lo guarda en formato mp3.
    progress_callback: función opcional para reportar progreso
    """
    clip = VideoFileClip(input_path)

    # Simular progreso 0%, 50%, 100%
    if progress_callback:
        progress_callback(0)
        progress_callback(50)

    clip.audio.write_audiofile(output_path, codec="mp3")

    if progress_callback:
        progress_callback(100)

    clip.close()
