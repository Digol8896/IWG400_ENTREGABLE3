from base_datos.models import *
import json
import urllib.parse
import urllib.request
import math
from datetime import datetime

"""
En este archivos estan las funciones varias, que pueden llegar a usarse en más de una funcion de la funcionalidad corazon.
"""

#Calcula la distancia de coordenadas
def distancia_entre_puntos(y1,x1,y2,x2):
    dy = (y2-y1)*111000
    dx = (x2-x1)*111000*math.cos(math.radians(y1))
    distancia = math.sqrt((dx**2)+(dy**2))
    return distancia

def obtener_distancia(item):
    return item['distancia']

def obtener_caminata(item):
    return item['caminata']

def obtener_minutos(item):
    return item['horario']['minutos']

def obtener_estimado(item):
    return item['estimado']

def formato_hora(segundos):
    segundos = int(segundos) % 86400
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    texto = str(horas).zfill(2) + ":" + str(minutos).zfill(2)
    return texto

def formato_duracion(minutos):
    if minutos < 60:
        texto = str(minutos) + " min"
    else:
        horas = minutos // 60
        resto = minutos % 60
        texto = str(horas) + " h " + str(resto) + " min"
    return texto

def segundos_ahora():
    ahora = datetime.now()
    segundos = ahora.hour * 3600 + ahora.minute * 60 + ahora.second
    return segundos

def texto_fecha_actual():
    return datetime.now().strftime("%Y-%m-%d")

def texto_hora_actual():
    return datetime.now().strftime("%H:%M")


#Esta función comprueba en base a la info de La tabla schedules de la base de datos si un servicio esta disponible o no.
def servicios_activos(fecha=None):
    hoy = fecha
    if hoy == None:
        hoy = datetime.now()
    fecha = hoy.strftime("%Y%m%d")
    dia = hoy.weekday()

    activos = []
    filas = calendario.objects.all()
    for f in filas:
        valores = [f.lunes, f.martes, f.miercoles, f.jueves, f.viernes, f.sabado, f.domingo]
        if valores[dia] == 1:
            activos.append(f.service_id + "|" + f.red)
    return activos


#Función hecha por claude para poder procesar los tiempos, lo que hace es procesar la hora ingresada por el usuario y la convierte a lo que requieren las otras funciones.
#Si la fecha no funciona o es invalida se usara el tiempo actual a travez del except.
def leer_inicio(fecha_texto, hora_texto):
    fecha = datetime.now()
    segundos = segundos_ahora()
    if fecha_texto:
        try:
            fecha = datetime.strptime(fecha_texto, "%Y-%m-%d")
        except ValueError:
            fecha = datetime.now()
    if hora_texto:
        try:
            hora = datetime.strptime(hora_texto, "%H:%M")
            segundos = hora.hour * 3600 + hora.minute * 60
        except ValueError:
            segundos = segundos_ahora()
    texto = fecha.strftime("%d/%m/%Y") + " " + formato_hora(segundos)
    return {'fecha': fecha, 'segundos': segundos, 'texto': texto}