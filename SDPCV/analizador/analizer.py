from ultralytics import YOLO
import cv2

import cv2
import time
from ultralytics import YOLO


class AnalizerYolo:

    def __init__(self):
        self.model = YOLO("models/yolov8n.pt")
        self.speed = 1.0
        self.reset()

    def reset(self):
        self.suben = 0
        self.bajan = 0
        self.historial = {}
        self.registros = []

        # 🔲 Zona rectangular editable
        self.zone = {
            "x": 200,
            "y": 150,
            "width": 300,
            "height": 200
        }

    def punto_en_zona(self, cx, cy):
        z = self.zone
        return (
            z["x"] < cx < z["x"] + z["width"] and
            z["y"] < cy < z["y"] + z["height"]
        )

    def procesar(self, frame):

        results = self.model.track(
            frame,
            persist=True,
            classes=[0],
            conf=0.4,
            tracker="bytetrack.yaml"
        )

        if results[0].boxes.id is None:
            self.dibujar_zona(frame)
            return frame

        for box, track_id in zip(results[0].boxes.xyxy,
                                 results[0].boxes.id):

            x1, y1, x2, y2 = map(int, box)
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            track_id = int(track_id)

            dentro = self.punto_en_zona(cx, cy)

            if track_id not in self.historial:
                self.historial[track_id] = dentro

            prev_dentro = self.historial[track_id]

            # 🔼 Entró a la zona
            if not prev_dentro and dentro:
                self.suben += 1

            # 🔽 Salió de la zona
            elif prev_dentro and not dentro:
                self.bajan += 1

            self.historial[track_id] = dentro

            # Dibujar bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, f"ID {track_id}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0,255,0), 2)

        self.dibujar_zona(frame)

        return frame

    def dibujar_zona(self, frame):
        z = self.zone

        cv2.rectangle(
            frame,
            (z["x"], z["y"]),
            (z["x"] + z["width"], z["y"] + z["height"]),
            (0,0,255),
            2
        )

        time.sleep(0.03 / self.speed)