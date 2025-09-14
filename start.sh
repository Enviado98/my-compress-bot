#!/bin/bash

# Iniciar el bot de Telegram
python3 bot.py &

# Mantener puerto abierto para Render (aunque no uses FastAPI)
while true; do sleep 1000; done
