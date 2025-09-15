#!/bin/bash
set -e

echo "Iniciando UserBot con FastAPI..."

# Ejecutar el servidor
uvicorn server:app --host 0.0.0.0 --port 8080
