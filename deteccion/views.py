import csv

import cv2
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .camara import camara
from .models import Deteccion


def registro(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("deteccion")
    return render(request, "registration/registro.html", {"form": form})


@login_required
def deteccion(request):
    return render(request, "deteccion.html")


@login_required
def video_feed(request):
    try:
        conf = min(max(float(request.GET.get("conf", 0.5)), 0.1), 0.95)
    except ValueError:
        conf = 0.5
    return StreamingHttpResponse(camara.frames(conf),
                                 content_type="multipart/x-mixed-replace; boundary=frame")


@login_required
@require_POST
def detener(request):
    camara.cerrar()
    return JsonResponse({"ok": True})


@login_required
def estado(request):
    _, detecciones = camara.instantanea()
    conteo = {"Mascarilla": 0, "Casco": 0, "Celular": 0}
    for etiqueta, _, _ in detecciones:
        conteo[etiqueta] = conteo.get(etiqueta, 0) + 1
    return JsonResponse(conteo)


@login_required
@require_POST
def guardar(request):
    frame, detecciones = camara.instantanea()
    if frame is None or not detecciones:
        return JsonResponse({"ok": False, "mensaje": "No hay objetos detectados para guardar."}, status=400)
    ok, buf = cv2.imencode(".jpg", frame)
    ruta = default_storage.save(f"capturas/{timezone.now():%Y%m%d_%H%M%S}.jpg", ContentFile(buf.tobytes()))
    Deteccion.objects.bulk_create([
        Deteccion(usuario=request.user, objeto=e, confianza=c, imagen=ruta) for e, c, _ in detecciones
    ])
    return JsonResponse({"ok": True, "mensaje": f"Se guardaron {len(detecciones)} detecciones."})


def _filtrar(request):
    qs = Deteccion.objects.select_related("usuario")
    if request.GET.get("objeto"):
        qs = qs.filter(objeto=request.GET["objeto"])
    if request.GET.get("fecha"):
        qs = qs.filter(fecha__date=request.GET["fecha"])
    return qs


@login_required
def historial(request):
    pagina = Paginator(_filtrar(request), 10).get_page(request.GET.get("page"))
    filtros = request.GET.copy()
    filtros.pop("page", None)
    return render(request, "historial.html", {
        "pagina": pagina, "objetos": Deteccion.OBJETOS, "filtros": filtros.urlencode(),
    })


@login_required
def exportar_csv(request):
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="detecciones.csv"'
    w = csv.writer(resp)
    w.writerow(["ID", "Fecha", "Objeto", "Confianza", "Usuario"])
    for d in _filtrar(request):
        w.writerow([d.id, timezone.localtime(d.fecha).strftime("%d/%m/%Y %H:%M:%S"),
                    d.objeto, f"{d.confianza:.2f}", d.usuario.username])
    return resp
