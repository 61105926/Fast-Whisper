FROM python:3.10-slim

WORKDIR /app

# Instalar ffmpeg necesario para procesamiento audio
RUN pip install --no-cache-dir fastapi uvicorn faster-whisper python-multipart

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
