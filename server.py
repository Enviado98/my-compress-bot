import asyncio
from fastapi import FastAPI
from threading import Thread
from bot import app as userbot_app, task_queue, is_processing

app = FastAPI()

# --- Función para correr el UserBot en segundo plano ---
def run_userbot():
    userbot_app.run()  # Esto arranca Pyrogram (bloqueante)

# Iniciar UserBot en un hilo separado
thread = Thread(target=run_userbot, daemon=True)
thread.start()

# --- Endpoints HTTP ---

@app.get("/")
def read_root():
    return {"status": "UserBot activo 🚀"}

@app.get("/status")
async def status():
    """
    Endpoint para revisar la cola de tareas
    """
    queue_length = 0
    if task_queue:
        queue_length = task_queue.qsize() if hasattr(task_queue, "qsize") else "Desconocido"
    return {
        "status": "UserBot activo",
        "processing": is_processing,
        "queue_length": queue_length
    }
