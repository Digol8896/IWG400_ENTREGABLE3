"""
Este programa contiene las funciones que elaboran la información que va al HTML, son importantes ya que hacen el diccionario que recibe el HTML
para mostrar las posibles rutas.
"""


from base_datos.models import *
from .funciones import *
from .calculo_horarios import *
from .precios import *

#Esta función prepara los datos en un diccionario para las tarjetas que se muestran como posibles rutas.
#Se uso ayuda de Claude
def armar_tarjetas(caminos, cercanas_origen, cercanas_destino, tipo_usuario=None, inicio=None, distancia_directa=None):
    
    if inicio == None:
        inicio = leer_inicio("", "")
    
    dist_origen = {}
    for c in cercanas_origen:
        dist_origen[c['parada'].stop_id] = c['distancia']

    dist_destino = {}
    for c in cercanas_destino:
        dist_destino[c['parada'].stop_id] = c['distancia']


    mejores = {}
    for camino in caminos:
        clave = ""
        for s in camino:
            clave = clave + s['ruta_id'] + "|" + s['subida'] + "|"
        ultima = camino[len(camino) - 1]
        if clave not in mejores:
            mejores[clave] = camino
        else:
            actual = mejores[clave]
            ultima_actual = actual[len(actual) - 1]
            if dist_destino[ultima['bajada']] < dist_destino[ultima_actual['bajada']]:
                mejores[clave] = camino


    hora_inicio = inicio['segundos']
    activos = servicios_activos(inicio['fecha'])

    candidatos = []
    for camino in mejores.values():
        ultima = camino[len(camino) - 1]
        estimado = ultima['tiempo'] + dist_destino[ultima['bajada']] * 0.75
        candidatos.append({'camino': camino, 'estimado': estimado})
    candidatos.sort(key=obtener_estimado)
    candidatos = candidatos[:80]

    opciones = []
    for candidato in candidatos:
        camino = candidato['camino']
        primera = camino[0]
        ultima = camino[len(camino) - 1]
        caminata = dist_origen[primera['subida']] + dist_destino[ultima['bajada']]
        for s in camino:
            caminata = caminata + s['caminar_antes']
        horario = calcular_horario(camino, hora_inicio, dist_origen[primera['subida']], dist_destino[ultima['bajada']], activos)
        if horario != None:
            opciones.append({'camino': camino, 'caminata': caminata, 'horario': horario})
    opciones.sort(key=obtener_minutos)

    
    if distancia_directa != None and distancia_directa < 600:
        minutos_caminando = distancia_directa * 1.3 * 0.75 / 60
        mas_rapidas = []
        for o in opciones:
            if o['horario']['minutos'] < minutos_caminando:
                mas_rapidas.append(o)
        opciones = mas_rapidas

    
    if len(opciones) > 0:
        limite = opciones[0]['horario']['minutos'] * 2 + 30
        utiles = []
        for o in opciones:
            if o['horario']['minutos'] <= limite:
                utiles.append(o)
        opciones = utiles
    opciones = opciones[:15]

    
    ids = []
    for o in opciones:
        for s in o['camino']:
            ids.append(s['subida'])
            ids.append(s['bajada'])
    datos_paradas = {}
    for p in paradas.objects.filter(stop_id__in=ids):
        datos_paradas[p.stop_id] = p

    tarjetas = []
    for o in opciones:
        camino = o['camino']
        tramos = ["Caminar"]
        segmentos = []
        numero_segmento = 0
        for s in camino:
            sube = datos_paradas[s['subida']]
            baja = datos_paradas[s['bajada']]
            rango = rango_shape(s['shape_id'], sube.lat, sube.lon, baja.lat, baja.lon)
            segmento = {
                'ruta': s['ruta_id'],
                'trip_id': s['trip_id'],
                'shape_id': s['shape_id'],
                'shape_desde': rango['desde'],
                'shape_hasta': rango['hasta'],
                'stop_subida': sube.stop_id,
                'subida': sube.nombre,
                'lat_subida': sube.lat,
                'lon_subida': sube.lon,
                'stop_bajada': baja.stop_id,
                'bajada': baja.nombre,
                'lat_bajada': baja.lat,
                'lon_bajada': baja.lon,
                'caminar_antes': s['caminar_antes'],
                'hora_subida': o['horario']['textos_subida'][numero_segmento],
                'hora_bajada': o['horario']['textos_bajada'][numero_segmento],
                'paradas': o['horario']['paradas'][numero_segmento],
            }
            numero_segmento = numero_segmento + 1
            segmentos.append(segmento)
            tramos.append(s['ruta_id'])
        tramos.append("Caminar")

        caminar_transbordo = 0
        if len(camino) == 2:
            caminar_transbordo = camino[1]['caminar_antes']

        precio = calcular_precios(camino, tipo_usuario, o['horario']['horas_subida'], inicio['fecha'])
        if precio == None:
            texto_precio = "No hay información"
        else:
            texto_precio = "$" + str(precio)

        tarjeta = {
            'salida': o['horario']['salida'],
            'llegada': o['horario']['llegada'],
            'duracion': o['horario']['duracion'],
            'precio': texto_precio,
            'tramos': tramos,
            'segmentos': segmentos,
            'caminar_origen': dist_origen[camino[0]['subida']],
            'caminar_destino': dist_destino[camino[len(camino) - 1]['bajada']],
            'caminar_transbordo': caminar_transbordo
        }
        tarjetas.append(tarjeta)
    return tarjetas

def rango_shape(shape_id, lat_subida, lon_subida, lat_bajada, lon_bajada):
    puntos = list(ShapePunto.objects.filter(shape_id=shape_id).order_by('secuencia'))

    desde = 0
    menor = 999999
    for p in puntos:
        distancia = distancia_entre_puntos(lat_subida, lon_subida, p.lat, p.lon)
        if distancia < menor:
            menor = distancia
            desde = p.secuencia

    hasta = desde
    menor = 999999
    for p in puntos:
        if p.secuencia > desde:
            distancia = distancia_entre_puntos(lat_bajada, lon_bajada, p.lat, p.lon)
            if distancia < menor:
                menor = distancia
                hasta = p.secuencia

    return {'desde': desde, 'hasta': hasta}