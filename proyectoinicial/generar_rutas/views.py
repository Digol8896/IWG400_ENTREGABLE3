import time
from django.shortcuts import render, redirect
from base_datos.models import rutas, ShapePunto
from mapa.funciones import crear_mapa, agregar_marcador, agregar_linea
from .funciones import *
from .busquedas_lugares import *
from .paradas import *
from .generacion_de_rutas import *
from .tarjetas import *

def generar_rutas(request):
    mapa = crear_mapa(-33.49154625123182, -70.61773734675901, 12)
    return render(request, 'generar_rutas.html', {'mapa': mapa, 'fecha_hoy': texto_fecha_actual(), 'hora_ahora': texto_hora_actual()})

def confirmar_lugares(request):
    if request.method != 'POST':
        return redirect("generar_rutas_formulario")
    if request.method == 'POST':
        origen = request.POST.get('origen')
        destino = request.POST.get('destino')

        origenes = buscar_lugar(origen)
        destinos = buscar_lugar(destino)


        if not origenes or not destinos:
            mapa = crear_mapa(-33.49154625123182, -70.61773734675901, 12)
            return render(request, 'confirmar_lugares.html', {'error': 'No se encontraron lugares para el origen o destino, por favor intente con más detalles.', 'mapa': mapa})

        mapa = crear_mapa(origenes[0]['lat'], origenes[0]['lon'], 12)
        numero = 1
        for o in origenes:
            agregar_marcador(mapa, o['lat'], o['lon'], "Origen "+str(numero)+": "+o['nombre'])
            numero = numero + 1
        numero = 1
        for d in destinos:
            agregar_marcador(mapa, d['lat'], d['lon'], "Destino "+str(numero)+": "+d['nombre'])
            numero = numero + 1
        return render(request, "confirmar_lugares.html", {'mapa': mapa, 'origenes': origenes, 'destinos': destinos, 'tipo_usuario': request.POST.get('tipo_usuario', 'regular'), 'fecha_viaje': request.POST.get('fecha_viaje', ''), 'hora_viaje': request.POST.get('hora_viaje', '')})
    return render(request, 'confirmar_lugares.html')

def generar_ruta_recorridos(request):
    if request.method != 'POST':
        return redirect("generar_rutas_formulario")

    if request.method == 'POST':
        origen = request.POST.get('origen')
        destino = request.POST.get('destino')
        tipo_usuario = request.POST.get('tipo_usuario', 'regular')
        inicio_viaje = leer_inicio(request.POST.get('fecha_viaje', ''), request.POST.get('hora_viaje', ''))
        if origen == None or destino == None:
            return redirect("generar_rutas_formulario")

        datos_origen = origen.split("|", 2)
        datos_destino = destino.split("|", 2)

        #Datos del origen
        lat_origen = float(datos_origen[0])
        lon_origen = float(datos_origen[1])
        nombre_origen = datos_origen[2]

        #Datos del destino
        lat_destino = float(datos_destino[0])
        lon_destino = float(datos_destino[1])
        nombre_destino = datos_destino[2]

        mapa = crear_mapa(lat_origen, lon_origen, 12)
        #Marcador del origen
        agregar_marcador(mapa, lat_origen, lon_origen, "Origen: "+nombre_origen)
        #Marcador del destino
        agregar_marcador(mapa, lat_destino, lon_destino, "Destino: "+nombre_destino)
        t0 = time.time()
        cercanas_origen = paradas_cercanas_adaptativo(lat_origen, lon_origen)
        cercanas_destino = paradas_cercanas_adaptativo(lat_destino, lon_destino)
        t1 = time.time()
        distancia_directa = distancia_entre_puntos(lat_origen, lon_origen, lat_destino, lon_destino)
        caminos = buscar_rutas(cercanas_origen, cercanas_destino, 3, 20, 3600, inicio_viaje)
        t2 = time.time()
        tarjetas = armar_tarjetas(caminos, cercanas_origen, cercanas_destino, tipo_usuario, inicio_viaje, distancia_directa)
        t3 = time.time()
        print("TIEMPOS | paradas:", round(t1 - t0, 1), "| buscar_rutas:", round(t2 - t1, 1), "| tarjetas:", round(t3 - t2, 1), "| TOTAL:", round(t3 - t0, 1), "| caminos:", len(caminos), "| tarjetas:", len(tarjetas), "| salida:", inicio_viaje['texto'])
        return render(request, "busqueda_rutas.html", {"mapa": mapa, "lat_o": lat_origen, "lon_o": lon_origen, 'lat_d': lat_destino, "lon_d": lon_destino, "nombre_origen": nombre_origen, "nombre_destino":nombre_destino, "opciones": tarjetas, "inicio_texto": inicio_viaje['texto']})

def ruta_generada(request):
    if request.method != 'POST':
        return redirect("generar_rutas_formulario")
    if request.POST.get('cantidad') == None:
        return redirect("generar_rutas_formulario")

    #Origen y destino
    nombre_origen = request.POST.get('nombre_origen')
    lat_origen = float(request.POST.get('lat_o'))
    lon_origen = float(request.POST.get('lon_o'))
    nombre_destino = request.POST.get('nombre_destino')
    lat_destino = float(request.POST.get('lat_d'))
    lon_destino = float(request.POST.get('lon_d'))

    #Datos generales de la opcion elegida
    cantidad = int(request.POST.get('cantidad'))
    caminar_origen = float(request.POST.get('caminar_origen'))
    caminar_destino = float(request.POST.get('caminar_destino'))
    caminar_transbordo = float(request.POST.get('caminar_transbordo'))
    precio = request.POST.get('precio')
    salida = request.POST.get('salida')
    llegada = request.POST.get('llegada')
    duracion = request.POST.get('duracion')

    mapa = crear_mapa(lat_origen, lon_origen, 13)
    agregar_marcador(mapa, lat_origen, lon_origen, "Origen: "+nombre_origen)
    agregar_marcador(mapa, lat_destino, lon_destino, "Destino: "+nombre_destino)

    segmentos = []
    for k in range(1, cantidad + 1):
        n = str(k)
        ruta = request.POST.get('ruta_' + n)
        shape = request.POST.get('shape_' + n)
        desde = int(request.POST.get('desde_' + n))
        hasta = int(request.POST.get('hasta_' + n))
        nombre_subida = request.POST.get('nombre_subida_' + n)
        lat_subida = float(request.POST.get('lat_subida_' + n))
        lon_subida = float(request.POST.get('lon_subida_' + n))
        nombre_bajada = request.POST.get('nombre_bajada_' + n)
        lat_bajada = float(request.POST.get('lat_bajada_' + n))
        lon_bajada = float(request.POST.get('lon_bajada_' + n))
        caminar_antes = float(request.POST.get('caminar_antes_' + n))
        hora_subida = request.POST.get('hora_subida_' + n)
        hora_bajada = request.POST.get('hora_bajada_' + n)
        paradas = request.POST.get('paradas_' + n)

        #Puntos del trazado entre subida y bajada
        puntos = []
        trazado = ShapePunto.objects.filter(shape_id=shape, secuencia__gte=desde, secuencia__lte=hasta).order_by('secuencia')
        for p in trazado:
            puntos.append([p.lat, p.lon])

        #Color de la ruta, si no encuentra ninguno en la base usa azul.
        color = "0000FF"
        datos_ruta = rutas.objects.filter(codigo=ruta).first()
        if datos_ruta:
            if datos_ruta.color:
                color = datos_ruta.color

        #Como los Shapes no siempre incluyen la coordenada de una parada se traza una linea hacia ella en caso de ser necesario.
        puntos.insert(0, [lat_subida, lon_subida])
        puntos.append([lat_bajada, lon_bajada])
        agregar_linea(mapa, puntos, color)

        agregar_marcador(mapa, lat_subida, lon_subida, "Subida "+ruta+": "+nombre_subida)
        agregar_marcador(mapa, lat_bajada, lon_bajada, "Bajada "+ruta+": "+nombre_bajada)

        segmento = {
            'nombre_ruta': ruta,
            'subida': nombre_subida,
            'bajada': nombre_bajada,
            'lat_subida': lat_subida,
            'lon_subida': lon_subida,
            'lat_bajada': lat_bajada,
            'lon_bajada': lon_bajada,
            'min_antes': int(caminar_antes / 80) + 1,
            'hora_subida': hora_subida,
            'hora_bajada': hora_bajada,
            'paradas': paradas,
        }
        segmentos.append(segmento)

    #Tramos que se hacen caminando
    primero = segmentos[0]
    ultimo = segmentos[len(segmentos) - 1]
    agregar_linea(mapa, trazado_caminando(lat_origen, lon_origen, primero['lat_subida'], primero['lon_subida']), "000000")
    agregar_linea(mapa, trazado_caminando(ultimo['lat_bajada'], ultimo['lon_bajada'], lat_destino, lon_destino), "000000")
    for k in range(1, len(segmentos)):
        anterior = segmentos[k - 1]
        actual = segmentos[k]
        agregar_linea(mapa, trazado_caminando(anterior['lat_bajada'], anterior['lon_bajada'], actual['lat_subida'], actual['lon_subida']), "000000")

    min_origen = int(caminar_origen / 80) + 1
    min_destino = int(caminar_destino / 80) + 1
    min_transbordo = int(caminar_transbordo / 80) + 1

    return render(request, "ruta_generada.html", {
        "mapa": mapa,
        "nombre_origen": nombre_origen,
        "nombre_destino": nombre_destino,
        "min_origen": min_origen,
        "min_destino": min_destino,
        "min_transbordo": min_transbordo,
        "segmentos": segmentos,
        "precio": precio,
        "salida": salida,
        "llegada": llegada,
        "duracion": duracion,
    })