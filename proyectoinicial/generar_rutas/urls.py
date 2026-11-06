from django.contrib import admin
from django.urls import path
from .views import generar_rutas, confirmar_lugares, generar_ruta_recorridos, ruta_generada


urlpatterns = [
    path('', generar_rutas, name='generar_rutas_formulario'),
    path('confirmar_lugares/', confirmar_lugares, name='confirmar_lugares'),
    path('busqueda_rutas', generar_ruta_recorridos, name='generar_ruta_recorridos'),
    path('resultados/', ruta_generada, name='ruta_generada'),
]
