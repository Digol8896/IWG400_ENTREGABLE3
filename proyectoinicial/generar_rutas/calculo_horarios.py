"""
Este archivo contiene las funciones que se encargan de calcular los tiempos de viaje y horarios, es muy importante para poder predecir tiempos estimados,
y para poder buscar la ruta más rapida.
"""

from base_datos.models import *
from .funciones import *

def buscar_salida(ruta_id, shape_id, subida, bajada, reloj, activos):
    desfases = {}
    secuencias = {}
    filas_subida = StopTime.objects.filter(parada_id=subida, trip__ruta_id=ruta_id, trip__shape_id=shape_id).select_related("trip")
    for f in filas_subida:
        servicio = f.trip.service_id + "|" + f.trip.red
        if servicio in activos:
            desfases[f.trip_id] = f.desfase_seg
            secuencias[f.trip_id] = f.secuencia

    if len(desfases) == 0:
        return None

    desfases_bajada = {}
    paradas_viaje = {}
    filas_bajada = StopTime.objects.filter(trip_id__in=list(desfases.keys()), parada_id=bajada)
    for fb in filas_bajada:
        if fb.secuencia > secuencias[fb.trip_id]:
            desfases_bajada[fb.trip_id] = fb.desfase_seg
            paradas_viaje[fb.trip_id] = fb.secuencia - secuencias[fb.trip_id]

    if len(desfases_bajada) == 0:
        return None

    mejor = None
    salidas = Salida.objects.filter(trip_id__in=list(desfases_bajada.keys()), salida_seg__gte=reloj - 10800)
    for sa in salidas:
        hora = sa.salida_seg + desfases[sa.trip_id]
        if hora >= reloj:
            if mejor == None or hora < mejor['hora_subida']:
                mejor = {
                    'trip_id': sa.trip_id,
                    'salida_seg': sa.salida_seg,
                    'hora_subida': hora,
                    'exacta': sa.exacta,
                }

    if mejor == None:
        return None

    mejor['hora_bajada'] = mejor['salida_seg'] + desfases_bajada[mejor['trip_id']]
    mejor['paradas'] = paradas_viaje[mejor['trip_id']]
    return mejor



def calcular_horario(camino, hora_inicio, caminar_origen, caminar_destino, activos):
    espera_maxima = 7200 
    seg_por_metro = 0.75
    reloj = hora_inicio + caminar_origen * seg_por_metro
    primera_subida = None
    aproximado = False
    horas_subida = []
    textos_subida = []
    textos_bajada = []
    paradas_recorridos = []

    for s in camino:
        reloj = reloj + s.get('caminar_antes', 0) * seg_por_metro
        salida = buscar_salida(s['ruta_id'], s['shape_id'], s['subida'], s['bajada'], reloj, activos)
        if salida == None:
            return None
        espera = salida['hora_subida'] - reloj
        if espera > espera_maxima:
            return None
        if primera_subida == None:
            primera_subida = salida['hora_subida']
        horas_subida.append(salida['hora_subida'])
        texto_sube = formato_hora(salida['hora_subida'])
        texto_baja = formato_hora(salida['hora_bajada'])
        if salida['exacta'] == 0:
            aproximado = True
            texto_sube = "~" + texto_sube
            texto_baja = "~" + texto_baja
        textos_subida.append(texto_sube)
        textos_bajada.append(texto_baja)
        paradas_recorridos.append(salida['paradas'])
        reloj = salida['hora_bajada']

    reloj = reloj + caminar_destino * seg_por_metro
    minutos = round((reloj - hora_inicio) / 60)

    texto_salida = formato_hora(hora_inicio)
    texto_llegada = formato_hora(reloj)
    if aproximado:
        texto_llegada = "~" + texto_llegada

    horario = {
        'salida': texto_salida,
        'llegada': texto_llegada,
        'duracion': formato_duracion(minutos),
        'minutos': minutos,
        'horas_subida': horas_subida,
        'textos_subida': textos_subida,
        'textos_bajada': textos_bajada,
        'paradas': paradas_recorridos,
    }
    return horario