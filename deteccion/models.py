from django.conf import settings
from django.db import models


class Deteccion(models.Model):
    OBJETOS = [
    ("CaÃ­da detectada", "CaÃ­da detectada"),
    ("Guantes", "Guantes"),
    ("Gafas de seguridad", "Gafas de seguridad"),
    ("Casco", "Casco"),
    ("Mascarilla", "Mascarilla"),
    ("Sin guantes", "Sin guantes"),
    ("Sin gafas", "Sin gafas"),
    ("Sin casco", "Sin casco"),
    ("Sin mascarilla", "Sin mascarilla"),
    ("Sin chaleco", "Sin chaleco"),
    ("Sin arnÃ©s", "Sin arnÃ©s"),
    ("Persona", "Persona"),
    ("Chaleco de seguridad", "Chaleco de seguridad"),
]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    objeto = models.CharField(max_length=30, choices=OBJETOS)
    confianza = models.FloatField()
    imagen = models.ImageField(upload_to="capturas/")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.objeto} ({self.confianza:.2f}) - {self.fecha:%d/%m/%Y %H:%M}"

