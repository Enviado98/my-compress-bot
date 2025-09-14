#!/bin/bash

# Iniciar el bot de Telegram en segundo plano
python3 bot.py &

# Iniciar el servidor FastAPI para que Render no lo detenga
uvicorn main:app --host 0.0.0.0 --port 8080
