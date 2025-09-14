from moviepy.editor import VideoFileClip
import os
import time

def compress_video(input_path, output_path, quality="720p", progress_callback=None):
    """
    Comprime un video a la calidad deseada.
    quality: "144p", "480p", "720p", "1080p"
    progress_callback: función que recibe el % de progreso
    """
    try:
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
        # Simulación de progreso para el usuario
        for i, pct in enumerate([0, 25, 50, 75, 100]):
            if progress_callback:
                progress_callback(pct)
            time.sleep(0.5)  # Simulación, ya que moviepy no da callback real

        clip_resized.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            threads=4,
            preset="ultrafast"
        )

    except Exception as e:
        print(f"Error al comprimir video: {e}")
        raise e
    finally:
        clip.close()
        clip_resized.close()


def extract_audio(input_path, output_path, progress_callback=None):
    """
    Extrae el audio de un video y lo guarda en formato mp3
    progress_callback: función que recibe el % de progreso
    """
    try:
        clip = VideoFileClip(input_path)

        for pct in [0, 25, 50, 75, 100]:
            if progress_callback:
                progress_callback(pct)
            time.sleep(0.3)  # Simulación

        clip.audio.write_audiofile(output_path, codec="mp3")

    except Exception as e:
        print(f"Error al extraer audio: {e}")
        raise e
    finally:
        clip.close()
