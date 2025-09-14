#!/bin/bash
# Inicia bot en background
python3 bot.py &

# Inicia server para mantener el contenedor activo
uvicorn server:app --host 0.0.0.0 --port $PORT
