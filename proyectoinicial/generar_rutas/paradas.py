"""
En este archivo se encuentran las funciones encargadas de permitir la busqueda de paradas cercanas a una coordenada, estas son importantes para
la generación de las posibles rutas.
"""

from base_datos.models import *
from .funciones import *
from .precios import *

#Busca las paradas cercanas en base a un radio, es decir a cierta distancia de la coordenada ingresada
def paradas_cercanas(lat, lon, radio):
    r = radio/111000
    lat_min = lat-r
    lon_min = lon-r
    lat_max = lat+r
    lon_max = lon+r
    encontradas = paradas.objects.filter(lat__gte=lat_min, lat__lte=lat_max, lon__gte=lon_min, lon__lte=lon_max)
    cercanas = []
    for p in encontradas:
        distancia = distancia_entre_puntos(lat, lon, p.lat, p.lon)
        if distancia <= radio:
            cercanas.append({'parada': p, 'distancia': distancia})
    cercanas.sort(key=obtener_distancia)
    return cercanas

#Esta función lo que hace es gestionar la busqueda de paradas, amplia el radio de busqueda en caso de no encontrar, el radio maximo de busqueda depende de si es rural o no.
def paradas_cercanas_adaptativo(lat, lon):
    cercanas = paradas_cercanas(lat, lon, 2000)
    es_rural = False
    minimo_urbanas = 10
    if len(cercanas) == 0:
        es_rural = True
    else:
        urbanas = 0
        for c in cercanas:
            if c['parada'].red != "DTPR":
                urbanas = urbanas + 1
        if urbanas < minimo_urbanas:
            es_rural = True
    if es_rural:
        cercanas = paradas_cercanas(lat, lon, 7000)
    else:
        lejanas = paradas_cercanas(lat, lon, 7000)
        for c in lejanas:
            if c['distancia'] > 2000:
                if tramo_de_estacion(c['parada'].nombre) != None:
                    cercanas.append(c)
    return cercanas