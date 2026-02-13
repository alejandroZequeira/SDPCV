from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import cv2
import base64
import os

from analizador.analizer import AnalizerYolo  # 👈 IMPORT CORRECTO

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

analizer = AnalizerYolo()
video_path = None


# -----------------------------
# MODELOS
# -----------------------------

class SpeedData(BaseModel):
    speed: float


class ZoneData(BaseModel):
    x: int
    y: int
    width: int
    height: int


# -----------------------------
# CONTROL VELOCIDAD
# -----------------------------
@app.post("/set_speed")
async def set_speed(data: SpeedData):
    analizer.speed = data.speed
    return {"ok": True}


# -----------------------------
# SET ZONA RECTANGULAR
# -----------------------------
@app.post("/set_zone")
async def set_zone(data: ZoneData):
    analizer.zone = {
        "x": data.x,
        "y": data.y,
        "width": data.width,
        "height": data.height
    }
    return {"ok": True}


# -----------------------------
# SUBIR VIDEOS
# -----------------------------
@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):

    os.makedirs("videos", exist_ok=True)

    nombres = []

    for file in files:
        path = f"videos/{file.filename}"
        with open(path, "wb") as buffer:
            buffer.write(await file.read())
        nombres.append(file.filename)

    return {"videos": nombres}


# -----------------------------
# SELECCIONAR VIDEO
# -----------------------------
@app.post("/select")
def select_video(name: str):
    global video_path
    video_path = f"videos/{name}"
    analizer.reset()
    return {"status": "ok"}


# -----------------------------
# WEBSOCKET STREAMING
# -----------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    cap = cv2.VideoCapture(video_path)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = analizer.procesar(frame)

        _, buffer = cv2.imencode(".jpg", frame)
        jpg_as_text = base64.b64encode(buffer).decode()

        await websocket.send_json({
            "frame": jpg_as_text,
            "suben": analizer.suben,
            "bajan": analizer.bajan
        })

    cap.release()


# -----------------------------
# EXPORTAR CSV
# -----------------------------
@app.get("/export")
def export():
    analizer.exportar_csv()
    return FileResponse(
        "data/reporte.csv",
        filename="reporte.csv"
    )