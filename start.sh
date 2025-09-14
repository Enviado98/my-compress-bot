#!/bin/bash

# Iniciar el bot de Telegram
python3 bot.py &

# Iniciar el servidor FastAPI
uvicorn main:app --host 0.0.0.0 --port 8080
