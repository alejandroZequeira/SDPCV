from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import cv2
import shutil
from analizador import AnalizerYolo

app = FastAPI()

analizer = None

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    path = f"videos/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": path}

@app.get("/stream")
def stream_video(video_path: str):
    global analizer
    analizer = AnalizerYolo(video_path)
    analizer.abrir(video_path)

    def generate():
        while True:
            ret, frame = analizer.cap.read()
            if not ret:
                break
            frame = analizer.procesar(frame)
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   buffer.tobytes() + b'\r\n')

    return StreamingResponse(generate(),
        media_type='multipart/x-mixed-replace; boundary=frame')