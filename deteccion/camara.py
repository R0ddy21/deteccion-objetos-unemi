"""Captura de video en tiempo real con OpenCV y transmisión por MJPEG."""
import threading

import cv2

from .detector import Detector, dibujar


class Camara:
    def __init__(self):
        self.cap = None
        self.detector = None
        self.lock = threading.Lock()
        self.ultimas = []      # últimas detecciones
        self.ultimo = None     # último fotograma con recuadros
        self.conf = 0.5

    def abrir(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if self.detector is None:
            self.detector = Detector()
        return self.cap.isOpened()

    def cerrar(self):
        if self.cap is not None:
            self.cap.release()
        self.cap = None
        with self.lock:
            self.ultimas, self.ultimo = [], None

    def frames(self, conf=0.5, cada=2):
        """Generador de fotogramas JPEG; detecta cada `cada` fotogramas para ganar FPS."""
        if not self.abrir():
            return
        self.conf = conf
        n, detecciones = 0, []
        while self.cap is not None and self.cap.isOpened():
            ok, frame = self.cap.read()
            if not ok:
                break
            n += 1
            if n % cada == 0:
                detecciones = self.detector.detectar(frame, conf)
            if not self.detector.listo:
                cv2.putText(frame, "Falta modelos/modelo.onnx", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            frame = dibujar(frame, detecciones)
            with self.lock:
                self.ultimas, self.ultimo = detecciones, frame.copy()
            ok, buf = cv2.imencode(".jpg", frame)
            if ok:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"

    def instantanea(self):
        with self.lock:
            return (None if self.ultimo is None else self.ultimo.copy()), list(self.ultimas)


camara = Camara()
