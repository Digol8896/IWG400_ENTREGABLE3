"""
En este archivo se encuentran las funciones que permiten procesar los precios de los distintos transportes y rutas.
"""

from base_datos.models import *
from datetime import datetime

#Función para determinar precios en base a la hora para el metro y metrotren NOS
def franja_por_hora(segundos, fecha=None):
    if fecha == None:
        fecha = datetime.now()
    dia = fecha.weekday()
    minutos = (int(segundos) % 86400) // 60
    if dia >= 5:
        return "valle"
    if minutos >= 420 and minutos < 540:
        return "punta"
    if minutos >= 1080 and minutos < 1200:
        return "punta"
    if minutos >= 540 and minutos < 1080:
        return "valle"
    if minutos >= 1200 and minutos < 1245:
        return "valle"
    return "baja"

#Función para determinar el tramo horario en el Metro Tren Rancagua
def franja_mtr_por_hora(segundos, fecha=None):
    if fecha == None:
        fecha = datetime.now()
    dia = fecha.weekday()
    minutos = (int(segundos) % 86400) // 60
    if dia >= 5:
        if minutos >= 600 and minutos < 1260:
            return "alta"
        return "baja"

    if minutos >= 300 and minutos < 510:
        return "alta"
    if minutos >= 1080 and minutos < 1230:
        return "alta"
    return "baja"

#Función a que tramo corresponde una estación del Metrotren Rancagua
def tramo_de_estacion(nombre):
    tramo_1 = ["Estación Central (Anden1)", "Estación San Bernardo (Anden1)"]
    tramo_2 = ["Estación BuinZoo", "Estación Buin", "Estación Linderos", "Estación Paine", "Estación Hospital"]
    tramo_3 = ["Estación San Francisco", "Estación Graneros", "Estación Rancagua"]
    
    nombre_limpio = nombre.split(" (")[0]
    for e in tramo_1:
        if e.split(" (")[0] == nombre_limpio:
            return 1
    for e in tramo_2:
        if e.split(" (")[0] == nombre_limpio:
            return 2
    for e in tramo_3:
        if e.split(" (")[0] == nombre_limpio:
            return 3
    return None


def precio_segun_usuario(fila, tipo_usuario):
    if tipo_usuario == "regular":
        return int(fila.regular)
    if tipo_usuario == "estudiante":
        return int(fila.estudiante)
    if tipo_usuario == "adulto_mayor":
        return int(fila.adulto_mayor)
    return None

def calcular_precios(camino, tipo_usuario, horas_subida, fecha=None):
    
    total = 0
    rec_dtpm = []
    hora_metro = None
    for i in range(len(camino)):
        s = camino[i]
        hora_abordaje = horas_subida[i]
        for r in rutas.objects.filter(codigo=s['ruta_id']):
            if r.red == "DTPM":
                if r.tipo == 1:
                    
                    if len(rec_dtpm) == 0 or rec_dtpm[len(rec_dtpm) - 1] != "metro":
                        rec_dtpm.append("metro")
                    
                    if hora_metro == None:
                        hora_metro = hora_abordaje
                elif r.tipo == 0:
                    if r.codigo == "MTN":
                        rec_dtpm.append("metrotren")
                        if hora_metro == None:
                            hora_metro = hora_abordaje
                    elif r.codigo == "MTR":
                        
                        sube = paradas.objects.filter(stop_id=s['subida']).first()
                        baja = paradas.objects.filter(stop_id=s['bajada']).first()
                        if sube == None or baja == None:
                            return None
                        tramo_sube = tramo_de_estacion(sube.nombre)
                        tramo_baja = tramo_de_estacion(baja.nombre)
                        if tramo_sube == None or tramo_baja == None:
                            return None
                        menor = min(tramo_sube, tramo_baja)
                        mayor = max(tramo_sube, tramo_baja)
                        clave_mtr = str(menor) + "-" + str(mayor) + "-" + franja_mtr_por_hora(hora_abordaje, fecha)
                        fila_mtr = precios_mtr.objects.filter(tipo=clave_mtr).first()
                        if fila_mtr == None:
                            return None
                        precio_mtr = precio_segun_usuario(fila_mtr, tipo_usuario)
                        if precio_mtr == None:
                            return None
                        total = total + precio_mtr
                    else:
                        return None
                elif r.tipo == 3:
                    if r.agencia == "BAA":
                        
                        return None
                    rec_dtpm.append("bus")
                else:
                    return None
            else:
                
                fila_rural = precios_dtpr.objects.filter(codigo_recorrido=r.codigo).first()
                if fila_rural == None:
                    return None
                precio_rural = precio_segun_usuario(fila_rural, tipo_usuario)
                if precio_rural == None:
                    return None
                total = total + precio_rural

    if len(rec_dtpm) > 0:
        clave = "_".join(rec_dtpm)
        if "metro" in rec_dtpm or "metrotren" in rec_dtpm:
            clave = clave + "_" + franja_por_hora(hora_metro, fecha)
        fila = precios_dtpm.objects.filter(tipo=clave).first()
        if fila == None:
            return None
        precio_dtpm = precio_segun_usuario(fila, tipo_usuario)
        if precio_dtpm == None:
            return None
        total = total + precio_dtpm

    if total == 0:
        return None
    return total