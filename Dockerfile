# Imagen base ligera de Python
FROM python:3.11-slim

# Evitar preguntas interactivas al instalar paquetes
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

# Dar permisos de ejecución al start.sh
RUN chmod +x start.sh

# Abrir el puerto que Render asigna (aunque no usamos uvicorn)
EXPOSE 8080

# Ejecutar start.sh al iniciar el contenedor
CMD ["./start.sh"]
