#!/bin/bash

# Iniciar el bot de Telegram en segundo plano
python3 bot.py &

# Iniciar el servidor FastAPI en el puerto que Render asigna
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
