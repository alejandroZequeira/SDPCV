import cv2
import time

url = "rtsp://172.28.128.1:8554/cam"

cap = cv2.VideoCapture(0)

# espera a que el stream se estabilice
time.sleep(2)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

cv2.namedWindow("Camara", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()

    if not ret or frame is None:
        print("No se recibió frame")
        continue

    h, w, _ = frame.shape

    # --- CUADRO DE DETECCIÓN (ejemplo) ---
    x1, y1 = int(w*0.3), int(h*0.3)
    x2, y2 = int(w*0.7), int(h*0.7)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
    cv2.putText(frame, "DETECCION",
                (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0,255,0), 2)

    cv2.imshow("Camara", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
