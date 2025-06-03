import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from faster_whisper import WhisperModel
import tempfile
import os
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fast-whisper")

app = FastAPI(title="Microservicio Fast Whisper")

logger.info("Inicializando modelo Whisper...")
try:
    model = WhisperModel("large-v3", compute_type="int8")
    logger.info("Modelo cargado correctamente")
except Exception as e:
    logger.error(f"Error al cargar el modelo: {e}")
    raise

@app.post("/transcribir/")
async def transcribir(audio: UploadFile = File(...)):
    logger.info(f"Recibido archivo: {audio.filename}, tipo: {audio.content_type}")
    
    suffix = os.path.splitext(audio.filename)[1]
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
        logger.info(f"Archivo temporal creado: {tmp_path} ({len(content)} bytes)")
    except Exception as e:
        logger.error(f"Error guardando archivo temporal: {e}")
        raise HTTPException(status_code=500, detail="Error guardando archivo temporal")

    start_time = time.time()
    try:
        segments, info = model.transcribe(tmp_path, language="es", beam_size=5)
        duration = time.time() - start_time
        logger.info(f"Transcripción completada en {duration:.2f}s, idioma detectado: {info.language}, duración audio: {info.duration:.2f}s")
    except Exception as e:
        logger.error(f"Error durante la transcripción: {e}")
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail="Error durante la transcripción")

    resultado = {
        "idioma_detectado": info.language,
        "duracion_segundos": info.duration,
        "segmentos": []
    }

    for segment in segments:
        logger.debug(f"Segmento {segment.start:.2f}s - {segment.end:.2f}s: {segment.text.strip()}")
        resultado["segmentos"].append({
            "inicio": round(segment.start, 2),
            "fin": round(segment.end, 2),
            "texto": segment.text.strip()
        })

    try:
        os.remove(tmp_path)
        logger.info(f"Archivo temporal eliminado: {tmp_path}")
    except Exception as e:
        logger.warning(f"No se pudo eliminar archivo temporal {tmp_path}: {e}")

    return resultado
