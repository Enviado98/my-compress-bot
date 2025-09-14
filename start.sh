#!/bin/bash

# Iniciar el bot de Telegram en segundo plano
python3 bot.py &

# Mantener el contenedor activo con un servidor HTTP mínimo
python3 -m http.server 8080
