"""
Este modulo contiene funciones para trabajar con mapas, permitiendo trabajar en estos desde python sin tener que user
Javascript, haciendo que el proceso sea más sensillo.
"""

#Función que ingresara dentro del HTML un mapa centrado en la lat y lon que se le ingrese a la funcion
def crear_mapa(lat, lon, zoom):
    return {"centro": [lat, lon], "zoom": zoom, "lineas": [], "marcadores": []}

#Función que agregara un marcador en el mapa
def agregar_marcador(mapa, lat, lon, texto):
    mapa["marcadores"].append({"lat": lat, "lon": lon, "texto": texto})

#Función que agrega una linea en el mapa.
def agregar_linea(mapa, puntos, color):
    mapa["lineas"].append({"puntos": puntos, "color": color})
