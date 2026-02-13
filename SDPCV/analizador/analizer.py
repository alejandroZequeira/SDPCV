import cv2
import time
from ultralytics import YOLO

class AnalizerYolo:
    def __init__(self, source):
        self.source = source
        self.cap = None
        self.model = YOLO("yolov8n.pt")  # rápido y suficiente

        self.line_y = None
        self.dragging = False

        self.suben = 0
        self.bajan = 0

        self.objetos = {}
        self.obj_id = 0

        self.MIN_HEIGHT = 80

        cv2.namedWindow("Camara", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Camara", self.mouse)

    # -----------------------------------
    def mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if abs(y - self.line_y) < 10:
                self.dragging = True
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.line_y = y
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False

    # -----------------------------------
    def abrir(self, src):
        self.cap = cv2.VideoCapture(src)
        time.sleep(1)
        if not self.cap.isOpened():
            raise RuntimeError("No se pudo abrir la fuente")

        self.reset()

    def reset(self):
        self.suben = 0
        self.bajan = 0
        self.objetos = {}
        self.obj_id = 0
        self.line_y = None

    # -----------------------------------
    def centroide(self, x1,y1,x2,y2):
        return int((x1+x2)/2), int((y1+y2)/2)

    # -----------------------------------
    def procesar(self, frame):
        h,w,_ = frame.shape
        if self.line_y is None:
            self.line_y = h//2

        results = self.model(frame, conf=0.4, classes=[0], verbose=False)

        detecciones = []

        for r in results:
            for box in r.boxes:
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                altura = y2 - y1
                if altura < self.MIN_HEIGHT:
                    continue

                cx,cy = self.centroide(x1,y1,x2,y2)
                detecciones.append((cx,cy))

                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.circle(frame,(cx,cy),4,(0,0,255),-1)

        self.tracking(detecciones)
        self.ui(frame)
        return frame

    # -----------------------------------
    def tracking(self, detecciones):
        nuevos = {}

        for cx,cy in detecciones:
            encontrado=False
            for oid,(px,py,estado) in self.objetos.items():
                if abs(cx-px)<50 and abs(cy-py)<50:
                    encontrado=True

                    if estado=="abajo" and cy<self.line_y:
                        self.suben+=1
                        estado="arriba"
                    elif estado=="arriba" and cy>self.line_y:
                        self.bajan+=1
                        estado="abajo"

                    nuevos[oid]=(cx,cy,estado)
                    break

            if not encontrado:
                estado="abajo" if cy>self.line_y else "arriba"
                nuevos[self.obj_id]=(cx,cy,estado)
                self.obj_id+=1

        self.objetos = nuevos

    # -----------------------------------
    def ui(self, frame):
        h,w,_ = frame.shape

        cv2.line(frame,(0,self.line_y),(w,self.line_y),(255,0,0),2)

        cv2.putText(frame,f"SUBEN: {self.suben}",(10,30),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        cv2.putText(frame,f"BAJAN: {self.bajan}",(10,70),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)

        cv2.putText(frame,
            f"ALTURA MIN (H/N): {self.MIN_HEIGHT}",
            (10,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)

    # -----------------------------------
    def teclado(self, key):
        if key==82: self.line_y-=5
        elif key==84: self.line_y+=5
        elif key==ord("h"): self.MIN_HEIGHT+=5
        elif key==ord("n"): self.MIN_HEIGHT=max(30,self.MIN_HEIGHT-5)
        elif key==ord("r"): self.reset()

    # -----------------------------------
    def ejecutar_fuente(self, src):
        self.abrir(src)
        print(f"▶ Analizando: {src}")

        while True:
            ret,frame = self.cap.read()
            if not ret:
                break

            frame = self.procesar(frame)
            cv2.imshow("Camara", frame)

            key = cv2.waitKey(30) & 0xFF
            self.teclado(key)

            if key==ord("q"):
                exit()

        self.cap.release()

    # -----------------------------------
    def run(self):
        if isinstance(self.source,list):
            for v in self.source:
                self.ejecutar_fuente(v)
        else:
            self.ejecutar_fuente(self.source)

        cv2.destroyAllWindows()
