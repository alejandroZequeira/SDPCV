import cv2
import time

class ContadorEscaleras:
    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)
        time.sleep(2)

        if not self.cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")

        self.fgbg = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=50,
            detectShadows=False
        )

        # --- Línea de decisión ---
        self.line_y = None   # se inicializa con el primer frame
        self.line_step = 5   # píxeles por tecla

        # --- Contadores ---
        self.suben = 0
        self.bajan = 0

        self.objetos = {}
        self.obj_id = 0

        # --- Filtros de cuerpo completo (CALIBRABLES) ---
        self.MIN_AREA = 2500
        self.MIN_HEIGHT = 60
        self.ASPECT_MIN = 0.3
        self.ASPECT_MAX = 1.2

        cv2.namedWindow("Camara", cv2.WINDOW_NORMAL)

    def centroid(self, x, y, w, h):
        return int(x + w / 2), int(y + h / 2)

    def is_all_body(self, w, h, area):
        aspect = w / float(h)
        if area < self.MIN_AREA:
            return False
        if h < self.MIN_HEIGHT:
            return False
        if not (self.ASPECT_MIN <= aspect <= self.ASPECT_MAX):
            return False
        return True

    def process_frame(self, frame):
        h, w, _ = frame.shape

        if self.line_y is None:
            self.line_y = h // 2

        fgmask = self.fgbg.apply(frame)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        fgmask = cv2.dilate(fgmask, None, iterations=2)

        contours, _ = cv2.findContours(
            fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        detecciones = []

        for c in contours:
            area = cv2.contourArea(c)
            x, y, w_box, h_box = cv2.boundingRect(c)

            if not self.is_all_body(w_box, h_box, area):
                continue

            cx, cy = self.centroid(x, y, w_box, h_box)
            detecciones.append((cx, cy))

            cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

        self.update_tracking(detecciones)
        self._ui(frame)

        return frame

    def update_tracking(self, detecciones):
        nuevos_objetos = {}

        for cx, cy in detecciones:
            encontrado = False

            for oid, (px, py, estado) in self.objetos.items():
                if abs(cx - px) < 40 and abs(cy - py) < 40:
                    encontrado = True

                    if estado == "abajo" and cy < self.line_y:
                        self.suben += 1
                        estado = "arriba"

                    elif estado == "arriba" and cy > self.line_y:
                        self.bajan += 1
                        estado = "abajo"

                    nuevos_objetos[oid] = (cx, cy, estado)
                    break

            if not encontrado:
                estado = "abajo" if cy > self.line_y else "arriba"
                nuevos_objetos[self.obj_id] = (cx, cy, estado)
                self.obj_id += 1

        self.objetos = nuevos_objetos

    def _ui(self, frame):
        h, w, _ = frame.shape

        cv2.line(frame, (0, self.line_y), (w, self.line_y), (255, 0, 0), 2)

        cv2.putText(frame, f"SUBEN: {self.suben}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, f"BAJAN: {self.bajan}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.putText(frame, "⬆⬇ Mover linea | Q salir",
                    (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    def key_manager(self, key):
        if key == 82:   # Flecha arriba
            self.line_y -= self.line_step
        elif key == 84: # Flecha abajo
            self.line_y += self.line_step

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = self.process_frame(frame)
            cv2.imshow("Camara", frame)

            key = cv2.waitKey(1) & 0xFF
            self.key_manager(key)

            if key == ord("q"):
                break

        self.liberar()

    def liberar(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    contador = ContadorEscaleras(cam_index=0)
    contador.run()

