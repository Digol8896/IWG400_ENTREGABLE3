"""
En este archivo van las funciones que permiten buscar lugares, esto permite que cuando el usuario ingresa un lugar el programa pueda obtener sus coordenadas.
"""

from base_datos.models import *
import json
import urllib.parse
import urllib.request

#Busca las paradas con nombre parecido al lugar ingresado
def buscar_paradas(nombre):
    lugares = []
    encontradas = paradas.objects.filter(nombre__icontains=nombre)
    for p in encontradas:
        lugares.append({'nombre': "Parada: "+p.nombre, 'lat': float(p.lat), 'lon': float(p.lon)})
    return lugares

#Busca los lugares que coinciden con el lugar ingresado, la función fue hecha con ayuda de Claude para la correcta implementación de la API de OSM
def buscar_osm(nombre):
    lugares = []
    consulta = urllib.parse.urlencode({
        "q": nombre,
        "format": "json",
        "limit": 5,
        "countrycodes": "cl",
        "viewbox": "-71.5,-32.9,-69.8,-34.3",
        "bounded": 1
    })
    url = f"https://nominatim.openstreetmap.org/search?" + consulta
    pedido = urllib.request.Request(url, headers={"User-Agent": "IWG400P212_04"})
    try:
        respuesta = urllib.request.urlopen(pedido, timeout=5)
        datos = json.loads(respuesta.read().decode("utf-8"))
    except Exception:
        return []
    for d in datos:
        lugares.append({'nombre': d["display_name"], 'lat': float(d["lat"]), 'lon': float(d["lon"])})
    return lugares

#Procesa el lugar que se ingreso para buscar en la base de datos de paradas y en internet
def buscar_lugar(texto):
    texto = texto.strip()
    if texto == "":
        return []
    lista = buscar_paradas(texto) + buscar_osm(texto)
    return lista
