from fastapi import FastAPI
from bot import app as userbot_app

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "UserBot activo 🚀"}

@app.get("/status")
def status():
    return {"status": "UserBot activo", "queue_length": "Por implementar"}
