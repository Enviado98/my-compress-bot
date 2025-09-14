from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot activo"}

# Endpoint opcional para revisar la cola de tareas
@app.get("/status")
def status():
    return {"status": "Bot activo", "message": "Lista de tareas activa"}
