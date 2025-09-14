#!/bin/bash

# Evitar que el contenedor se detenga si hay error
set -e

# Puerto que Render asigna
PORT=${PORT:-8080}

echo "Iniciando bot de Telegram..."
# Ejecutar el bot en segundo plano
python3 bot.py &

# Iniciar servidor FastAPI (opcional si usas webhooks)
echo "Iniciando servidor FastAPI en el puerto $PORT..."
uvicorn main:app --host 0.0.0.0 --port $PORT
