# Detección de objetos en tiempo real (Django + OpenCV)

Aplicativo web que captura video desde la cámara, detecta **mascarillas, cascos y celulares** con OpenCV (`cv2.dnn` + modelo YOLO en formato ONNX), muestra los resultados sobre el video y guarda un historial en PostgreSQL.

**Práctica Nº 3 – Construcción de Software – UNEMI**
Autores: Benjamin Josué Cabrera Yepez, Roddy Antonio Marcos Franco.

## Funcionalidades
- Registro e inicio de sesión de usuarios.
- Video en vivo con recuadros, etiquetas y nivel de confianza.
- Conteo en tiempo real y umbral de confianza ajustable.
- Guardado de detecciones (con captura) en PostgreSQL.
- Historial con filtros por objeto y fecha, paginación y exportación a CSV.

## Requisitos
Python 3.10+, PostgreSQL 14+, una cámara web y Git.

## Instalación
```bash
git clone <URL_DEL_REPOSITORIO>
cd <carpeta>
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

1. Cree la base de datos en PostgreSQL: `CREATE DATABASE deteccion_db;`
2. Copie `.env.example` a `.env` y complete sus credenciales.
3. Agregue el modelo (ver siguiente sección).
4. Ejecute:
```bash
python manage.py makemigrations deteccion
python manage.py migrate
python manage.py createsuperuser   # opcional
python manage.py runserver
```
Abra http://127.0.0.1:8000/

## Modelo de detección
El sistema carga `modelos/modelo.onnx` y `modelos/clases.txt` (una clase por línea, en el mismo orden del entrenamiento). Ambos archivos **no se suben a GitHub**.

- Debe ser un modelo **YOLOv8** exportado a ONNX con entrada 640x640:
  `yolo export model=best.pt format=onnx imgsz=640`
- Para mascarillas y cascos use pesos entrenados con un dataset de Roboflow o Kaggle (clases tipo `mask`, `helmet`/`hardhat`).
- El modelo COCO estándar (`yolov8n`) detecta `cell phone` (celulares), pero no mascarillas ni cascos.
- Las equivalencias de nombres de clase están en `ALIAS` dentro de `deteccion/detector.py`.

## Pruebas
```bash
python manage.py test
```

## Estructura
```
config/       configuración del proyecto Django
deteccion/    app: modelos, vistas, cámara (camara.py) y detector OpenCV (detector.py)
templates/    interfaz web (Bootstrap)
modelos/      modelo.onnx y clases.txt (local)
```

## Notas
- La cámara se abre en el computador donde corre `runserver` (uso local en el laboratorio).
- Si el video va lento, aumente `cada` en `Camara.frames` (`camara.py`) o suba el umbral de confianza.
