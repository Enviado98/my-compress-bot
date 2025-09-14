from moviepy.editor import VideoFileClip

def compress_video(input_path, output_path, quality="720p"):
    clip = VideoFileClip(input_path)

    # Elegimos resolución según la calidad deseada
    if quality == "480p":
        clip_resized = clip.resize(height=480)
    elif quality == "720p":
        clip_resized = clip.resize(height=720)
    elif quality == "1080p":
        clip_resized = clip.resize(height=1080)
    else:
        clip_resized = clip  # Mantener la original si no se reconoce

    clip_resized.write_videofile(output_path, codec="libx264", audio_codec="aac")
    clip.close()

def extract_audio(input_path, output_path):
    clip = VideoFileClip(input_path)
    clip.audio.write_audiofile(output_path)
    clip.close()
