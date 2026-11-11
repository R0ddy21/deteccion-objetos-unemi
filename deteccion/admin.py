from django.contrib import admin
from .models import Deteccion


@admin.register(Deteccion)
class DeteccionAdmin(admin.ModelAdmin):
    list_display = ("id", "objeto", "confianza", "usuario", "fecha")
    list_filter = ("objeto", "fecha")
