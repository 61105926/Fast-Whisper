from fastapi import FastAPI, File, UploadFile
from faster_whisper import WhisperModel
import tempfile
import os

app = FastAPI(title="Microservicio Fast Whisper")

# Cargar el modelo al iniciar
model = WhisperModel("large-v3", compute_type="int8")  # int8 para CPU eficiente

@app.post("/transcribir/")
async def transcribir(audio: UploadFile = File(...)):
    suffix = os.path.splitext(audio.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    segments, info = model.transcribe(tmp_path, language="es", beam_size=5)

    resultado = {
        "idioma_detectado": info.language,
        "duracion_segundos": info.duration,
        "segmentos": []
    }

    for segment in segments:
        resultado["segmentos"].append({
            "inicio": round(segment.start, 2),
            "fin": round(segment.end, 2),
            "texto": segment.text.strip()
        })

    # Limpiar archivo temporal
    os.remove(tmp_path)

    return resultado
