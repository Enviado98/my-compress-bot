import os

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_NAME = os.environ.get("SESSION_NAME", "userbot_session")
DEFAULT_VIDEO_QUALITY = os.environ.get("DEFAULT_VIDEO_QUALITY", "360p")
