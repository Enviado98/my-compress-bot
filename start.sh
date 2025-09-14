#!/bin/bash

# Evitar que el contenedor se detenga
set -e

echo "Iniciando Telegram Userbot..."

# Ejecutar el bot
python3 bot.py
