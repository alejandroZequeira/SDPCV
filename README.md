# Sistema de Deteccion de Personas en Tiempo Real

Sistema web para conteo de pasajeros usando YOLOv8 + ByteTrack con interfaz moderna en Vue 3 y comunicación en tiempo real mediante WebSockets.

---

## Tecnologías utilizadas

### Backend
- Python 3.10+
- FastAPI
- OpenCV
- Ultralytics YOLOv8 (ByteTrack)
- Uvicorn

### Frontend
- Vue 3 (Vite)
- WebSockets
- Canvas API

---

# Instalación Backend

```bash
    poetry lock
    poetry env activate
```
# Levantamiento del Backend 
```bash
    poetry run uvicorn server:app --reload
```
# levantar el servicio web
```bash
cd SDPCV-UI
npm run dev
```