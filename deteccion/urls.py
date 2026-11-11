from django.urls import path
from . import views

urlpatterns = [
    path("", views.deteccion, name="deteccion"),
    path("registro/", views.registro, name="registro"),
    path("video/", views.video_feed, name="video_feed"),
    path("detener/", views.detener, name="detener"),
    path("estado/", views.estado, name="estado"),
    path("guardar/", views.guardar, name="guardar"),
    path("historial/", views.historial, name="historial"),
    path("historial/csv/", views.exportar_csv, name="exportar_csv"),
]
