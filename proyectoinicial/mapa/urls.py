from django.contrib import admin
from django.urls import path
from inicio.views import inicio
from .views import mapa

urlpatterns = [
    path('', mapa, name='mapa_prueba')
]
