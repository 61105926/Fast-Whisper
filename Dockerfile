FROM python:3.10-slim

WORKDIR /app

# Instalar ffmpeg para procesamiento de audio (es necesario para faster-whisper)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar paquetes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY main.py .

# Exponer puerto 8001 (el que usas en uvicorn)
EXPOSE 8001

# Ejecutar la app con uvicorn en el puerto 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
