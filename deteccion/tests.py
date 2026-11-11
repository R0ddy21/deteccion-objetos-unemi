from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .detector import Detector
from .models import Deteccion


class PruebasDeteccion(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("demo", password="Clave12345")

    def test_historial_requiere_login(self):
        r = self.client.get(reverse("historial"))
        self.assertEqual(r.status_code, 302)

    def test_historial_con_sesion(self):
        self.client.login(username="demo", password="Clave12345")
        Deteccion.objects.create(usuario=self.user, objeto="Casco", confianza=0.9,
                                 imagen=SimpleUploadedFile("a.jpg", b"x"))
        r = self.client.get(reverse("historial"), {"objeto": "Casco"})
        self.assertContains(r, "Casco")

    def test_detector_sin_modelo_no_falla(self):
        import numpy as np
        with patch("deteccion.detector.settings") as s:
            s.MODELO_ONNX.exists.return_value = False
            s.MODELO_CLASES.exists.return_value = False
            self.assertEqual(Detector().detectar(np.zeros((480, 640, 3), np.uint8)), [])

    def test_guardar_sin_detecciones(self):
        self.client.login(username="demo", password="Clave12345")
        r = self.client.post(reverse("guardar"))
        self.assertEqual(r.status_code, 400)

    def test_exportar_csv(self):
        self.client.login(username="demo", password="Clave12345")
        r = self.client.get(reverse("exportar_csv"))
        self.assertEqual(r["Content-Type"].split(";")[0], "text/csv")
