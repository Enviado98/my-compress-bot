import moviepy.editor as mp

def compress_video(input_path: str, output_path: str, quality: str = "480p"):
    """
    Comprime un video a la calidad deseada.
    quality: '144p', '240p', '480p', '720p', '1080p'
    """
    clip = mp.VideoFileClip(input_path)
    
    # Definir resolución según calidad
    resolutions = {
        "144p": (256, 144),
        "240p": (426, 240),
        "480p": (854, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080)
    }
    target_res = resolutions.get(quality, (854, 480))
    
    clip_resized = clip.resize(newsize=target_res)
    clip_resized.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=4, logger=None)
    clip.close()
    clip_resized.close()

def extract_audio(input_path: str, output_path: str):
    """
    Extrae el audio de un video y lo guarda como mp3.
    """
    clip = mp.VideoFileClip(input_path)
    clip.audio.write_audiofile(output_path, logger=None)
    clip.close()
