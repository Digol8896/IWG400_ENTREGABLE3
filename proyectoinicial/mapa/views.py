from django.shortcuts import render
from .funciones import *

# Create your views here.

def mapa(request):
    mapa = crear_mapa(-33.49018527152, -70.6195230959199, 15)
    marcador1 = agregar_marcador(mapa, -33.49018527152, -70.6195230959199, "Marcador 1")
    puntos = [
        [-33.49018527152, -70.6195230959199], [-33.49518527152, -70.6145230959199]
    ]
    agregar_linea(mapa, puntos, "DA1111")
    return render(request, 'mapa.html', {'mapa': mapa})