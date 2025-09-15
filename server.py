from fastapi import FastAPI
import os
import asyncio
from pyrogram import Client

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot activo 🚀"}

# Nuevo método para iniciar el UserBot
async def start_userbot():
    userbot_app = Client("userbot", api_id=os.getenv("API_ID"), api_hash=os.getenv("API_HASH"))
    
    # Se utiliza asyncio.run() para asegurar el bucle de eventos
    await userbot_app.start()

    print("UserBot iniciado exitosamente.")
    await userbot_app.idle()  # Mantiene el UserBot en funcionamiento hasta que se detenga manualmente.

# Endpoint para iniciar el UserBot en un evento async
@app.on_event("startup")
async def on_startup():
    # Se inicia el UserBot de forma asíncrona cuando el servidor arranca
    await start_userbot()
