"""
En este archivo estan las funciones encargadas de generar posibles rutas.
"""

from .funciones import *
from django.db.models import Max

def expandir(rango, p_visitadas, serviciosactivos, p_previas, p_alternativas, ahora=None):
    
    activos = set(serviciosactivos)
    recorridos_subidos = {}

    
    filas = StopTime.objects.filter(parada__in=rango).values_list('trip_id', 'parada_id', 'secuencia', 'desfase_seg', 'trip__service_id', 'trip__red', 'trip__ruta_id', 'trip__shape_id')
    for fila in filas.iterator():
        servicio = fila[4] + "|" + fila[5]
        if servicio in activos:
            trip_id = fila[0]
            parada_id = fila[1]
            desfase = fila[3]
            guardar = False
            if trip_id not in recorridos_subidos:
                guardar = True
            else:
                
                actual = recorridos_subidos[trip_id]
                valor_nuevo = p_previas[parada_id]['tiempo'] - desfase
                valor_actual = p_previas[actual['parada_id']]['tiempo'] - actual['desfase_seg']
                if valor_nuevo < valor_actual:
                    guardar = True
            if guardar:
                recorridos_subidos[trip_id] = {
                    'trip_id': trip_id,
                    'parada_id': parada_id,
                    'secuencia': fila[2],
                    'desfase_seg': desfase,
                    'ruta_id': fila[6],
                    'shape_id': fila[7],
                }
    
    if ahora == None:
        ahora = segundos_ahora()
    proxima = {}
    filas_salidas = Salida.objects.filter(salida_seg__gte=ahora - 10800).values_list('trip_id', 'salida_seg')
    for fs in filas_salidas:
        trip_id = fs[0]
        if trip_id in recorridos_subidos:
            hora = fs[1] + recorridos_subidos[trip_id]['desfase_seg']
            if hora >= ahora:
                if trip_id not in proxima or hora < proxima[trip_id]:
                    proxima[trip_id] = hora

    
    ultima = {}
    filas_fin = StopTime.objects.filter(trip_id__in=list(proxima.keys())).values_list('trip_id').annotate(fin=Max('secuencia')).order_by()
    for ff in filas_fin:
        ultima[ff[0]] = ff[1]

   
    recorridos_vistos = {}
    for trip_id in proxima:
        fila = recorridos_subidos[trip_id]
        clave = fila['ruta_id'] + "|" + fila['shape_id'] + "|" + fila['parada_id'] + "|" + str(ultima[trip_id])
        if clave not in recorridos_vistos:
            recorridos_vistos[clave] = trip_id
        elif proxima[trip_id] < proxima[recorridos_vistos[clave]]:
            recorridos_vistos[clave] = trip_id
    trips_elegidos = list(recorridos_vistos.values())

    
    filas2 = StopTime.objects.filter(trip_id__in=trips_elegidos).values_list('trip_id', 'parada_id', 'secuencia', 'desfase_seg')

    nuevas = []

    
    for fila in filas2:
        trip_id = fila[0]
        parada_id = fila[1]
        secuencia = fila[2]
        desfase_bajada = fila[3]
        subida = recorridos_subidos[trip_id]
        if secuencia > subida['secuencia']:
            registro = {
                'subida': subida['parada_id'],
                'previa': p_previas[subida['parada_id']]['desde'],
                'caminar_antes': p_previas[subida['parada_id']]['distancia'],
                'trip_id': trip_id,
                'ruta_id': subida['ruta_id'],
                'shape_id': subida['shape_id'],
                'desfase_subida': subida['desfase_seg'],
                'desfase_bajada': desfase_bajada,
                'tiempo': p_previas[subida['parada_id']]['tiempo'] + (desfase_bajada - subida['desfase_seg']),
            }
            if parada_id not in p_visitadas:
                p_visitadas[parada_id] = registro
                p_alternativas[parada_id] = [registro]
                nuevas.append(parada_id)
            elif parada_id in p_alternativas:
                p_alternativas[parada_id].append(registro)
                if registro['tiempo'] < p_visitadas[parada_id]['tiempo']:
                    p_visitadas[parada_id] = registro
    return nuevas

def crear_grilla():
    grilla = {}
    por_id = {}
    for p in paradas.objects.all():
        por_id[p.stop_id] = p
        fila = math.floor(p.lat / 0.004)
        columna = math.floor(p.lon / 0.004)
        clave = (fila, columna)
        if clave not in grilla:
            grilla[clave] = []
        grilla[clave].append(p)
    return {'grilla': grilla, 'por_id': por_id}

def agregar_vecinas(nuevas, p_visitadas, p_previas, datos, radio):
    for stop_id in nuevas:
        p = datos['por_id'][stop_id]
        fila = math.floor(p.lat / 0.004)
        columna = math.floor(p.lon / 0.004)
        for f in [fila - 1, fila, fila + 1]:
            for c in [columna - 1, columna, columna + 1]:
                clave = (f, c)
                if clave in datos['grilla']:
                    for q in datos['grilla'][clave]:
                        if q.stop_id not in p_visitadas:
                            distancia = distancia_entre_puntos(p.lat, p.lon, q.lat, q.lon)
                            if distancia <= radio:
                                tiempo_nuevo = p_previas[stop_id]['tiempo'] + distancia * 0.75
                                if q.stop_id not in p_previas or tiempo_nuevo < p_previas[q.stop_id]['tiempo']:
                                    p_previas[q.stop_id] = {'desde': stop_id, 'distancia': distancia, 'tiempo': tiempo_nuevo}

def buscar_rutas(cercanas_origen, cercanas_destino, max_niveles, minimo=5, largo=3600, inicio=None):
   
    if inicio == None:
        inicio = leer_inicio("", "")
    activos = servicios_activos(inicio['fecha'])
    datos = crear_grilla()
    visitadas = {}
    previas = {}
    destino_paradas = {}

    for c in cercanas_destino:
        stop_id = c['parada'].stop_id
        destino_paradas[stop_id] = c['distancia']

    for c in cercanas_origen:
        stop_id = c['parada'].stop_id
        if stop_id in destino_paradas and c['distancia'] > 1000:
            continue
        visitadas[stop_id] = None
        previas[stop_id] = {'desde': stop_id, 'distancia': 0, 'tiempo': c['distancia'] * 0.75}

    soluciones = []
    combinaciones = {}
    mejor_estimado = None
    nivel = 1

    
    while nivel <= max_niveles and (nivel <= 2 or len(combinaciones) < minimo or mejor_estimado == None or mejor_estimado > largo):
        rango = list(previas.keys())
        alternativas = {}
        nuevas = expandir(rango, visitadas, activos, previas, alternativas, inicio['segundos'])
        for p in nuevas:
            if p in destino_paradas:
                mejor = visitadas[p]
                for registro in alternativas[p]:
                    visitadas[p] = registro
                    camino = reconstruir(p, visitadas)
                    soluciones.append(camino)
                    estimado = registro['tiempo'] + destino_paradas[p] * 0.75
                    if mejor_estimado == None or estimado < mejor_estimado:
                        mejor_estimado = estimado
                    nombre = ""
                    for s in camino:
                        nombre = nombre + s['ruta_id'] + "+"
                    combinaciones[nombre] = 1
                visitadas[p] = mejor
        previas = {}
        for p in nuevas:
            previas[p] = {'desde': p, 'distancia': 0, 'tiempo': visitadas[p]['tiempo']}
        if nivel < max_niveles:
            agregar_vecinas(nuevas, visitadas, previas, datos, 300)
        nivel = nivel + 1

    return soluciones

def reconstruir(parada_final, p_visitadas):
    segmentos = []
    actual = parada_final

    while p_visitadas[actual] != None:
        registro = p_visitadas[actual]
        segmento = {
            'trip_id': registro['trip_id'],
            'ruta_id': registro['ruta_id'],
            'shape_id': registro['shape_id'],
            'subida': registro['subida'],
            'bajada': actual,
            'desfase_subida': registro['desfase_subida'],
            'desfase_bajada': registro['desfase_bajada'],
            'caminar_antes': registro['caminar_antes'],
            'tiempo': registro['tiempo'],
        }
        segmentos.append(segmento)
        actual = registro['previa']

    segmentos.reverse()
    return segmentos

#Esta función usa una API para trazar las caminatas en base a los caminos del mapa, en caso de que la API no responda se traza una linea recta, la función utilizo ayuda de
#claude para poder implementar correctamente la API y trazar bien las lineas.
def trazado_caminando(lat1, lon1, lat2, lon2):
    
    recta = [[lat1, lon1], [lat2, lon2]]
    url = "https://routing.openstreetmap.de/routed-foot/route/v1/foot/" + str(lon1) + "," + str(lat1) + ";" + str(lon2) + "," + str(lat2) + "?overview=full&geometries=geojson"
    try:
        peticion = urllib.request.Request(url, headers={'User-Agent': 'proyecto-iwg400'})
        respuesta = urllib.request.urlopen(peticion, timeout=5)
        datos = json.loads(respuesta.read().decode('utf-8'))
        coordenadas = datos['routes'][0]['geometry']['coordinates']
    except Exception:
        return recta
    puntos = []
    for c in coordenadas:
        lon = c[0]
        lat = c[1]
        puntos.append([lat, lon])
    puntos.insert(0, [lat1, lon1])
    puntos.append([lat2, lon2])
    return puntos