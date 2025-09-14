#!/bin/bash

# Usar puerto que Render asigna
export PORT=${PORT:-8080}

# Iniciar el Userbot
python3 bot.py
