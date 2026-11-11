"""Detección de objetos con OpenCV (cv2.dnn) usando un modelo YOLO en formato ONNX."""
import cv2
import numpy as np
from django.conf import settings
TAM = 640

# Nombre de la clase en el modelo (minúsculas) -> etiqueta que ve el usuario
ALIAS = {
    "fall-detected": "Caída detectada",
    "gloves": "Guantes",
    "goggles": "Gafas de seguridad",
    "hardhat": "Casco",
    "mask": "Mascarilla",
    "no-gloves": "Sin guantes",
    "no-goggles": "Sin gafas",
    "no-hardhat": "Sin casco",
    "no-mask": "Sin mascarilla",
    "no-safety vest": "Sin chaleco",
    "no_harness": "Sin arnés",
    "person": "Persona",
    "safety vest": "Chaleco de seguridad",
}

COLORES = {
    "Caída detectada": (0, 0, 255),
    "Guantes": (80, 200, 60),
    "Gafas de seguridad": (220, 140, 40),
    "Casco": (220, 140, 40),
    "Mascarilla": (80, 200, 60),
    "Sin guantes": (0, 0, 255),
    "Sin gafas": (0, 0, 255),
    "Sin casco": (0, 0, 255),
    "Sin mascarilla": (0, 0, 255),
    "Sin chaleco": (0, 0, 255),
    "Sin arnés": (0, 0, 255),
    "Persona": (255, 255, 255),
    "Chaleco de seguridad": (80, 200, 60),
}


class Detector:
    def __init__(self):
        self.net, self.clases = None, []
        if settings.MODELO_ONNX.exists() and settings.MODELO_CLASES.exists():
            ruta_modelo = settings.MODELO_ONNX.resolve()
            self.net = cv2.dnn.readNetFromONNX(str(ruta_modelo))
            with open(settings.MODELO_CLASES, encoding="utf-8") as f:
                self.clases = [l.strip().lower() for l in f if l.strip()]

    @property
    def listo(self):
        return self.net is not None

    def detectar(self, frame, conf_min=0.5, nms=0.45):
        """Devuelve una lista de (etiqueta, confianza, (x, y, w, h))."""
        if not self.listo:
            return []
        alto, ancho = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (TAM, TAM), swapRB=True, crop=False)
        self.net.setInput(blob)
        salida = self.net.forward()[0].T                  # (anclas, 4 + n_clases)
        puntajes = salida[:, 4:]
        ids, confs = puntajes.argmax(axis=1), puntajes.max(axis=1)

        cajas, confianzas, etiquetas = [], [], []
        for i in np.where(confs >= conf_min)[0]:
            nombre = self.clases[ids[i]] if ids[i] < len(self.clases) else ""
            etiqueta = ALIAS.get(nombre)
            if etiqueta is None:
                continue
            cx, cy, w, h = salida[i, :4]
            cajas.append([int((cx - w / 2) * ancho / TAM), int((cy - h / 2) * alto / TAM),
                          int(w * ancho / TAM), int(h * alto / TAM)])
            confianzas.append(float(confs[i]))
            etiquetas.append(etiqueta)
        if not cajas:
            return []
        keep = np.array(cv2.dnn.NMSBoxes(cajas, confianzas, conf_min, nms)).flatten()
        return [(etiquetas[i], confianzas[i], tuple(cajas[i])) for i in keep]


def dibujar(frame, detecciones):
    """Dibuja recuadros y etiquetas sobre el fotograma."""
    for etiqueta, conf, (x, y, w, h) in detecciones:
        color = COLORES.get(etiqueta, (255, 255, 255))
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        texto = f"{etiqueta} {conf:.2f}"
        cv2.putText(frame, texto, (x, max(y - 8, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame
