# Imagen base ligera de Python
FROM python:3.11-slim

# Evitar preguntas interactivas
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y actualizar pip
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Dar permisos al start.sh
RUN chmod +x start.sh

# Abrir el puerto asignado por Render
EXPOSE 8080

# Ejecutar start.sh
CMD ["./start.sh"]
