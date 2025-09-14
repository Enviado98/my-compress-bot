from dotenv import load_dotenv
import os

load_dotenv()  # Esto lee el archivo .env

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEFAULT_VIDEO_QUALITY = os.getenv("DEFAULT_VIDEO_QUALITY", "720p")
