#!/bin/bash
# start.sh - Script para iniciar el bot y el server en Render

# Puerto que Render asigna automáticamente
PORT=${PORT:-8080}

# Ejecutar bot en background
echo "Iniciando bot de Telegram..."
python3 bot.py &

# Ejecutar FastAPI con uvicorn en el puerto asignado
echo "Iniciando FastAPI server en el puerto $PORT..."
uvicorn server:app --host 0.0.0.0 --port $PORT &

# Mantener el contenedor activo
wait
