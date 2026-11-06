from django.shortcuts import render, get_object_or_404
from base_datos.models import *
from mapa.funciones import crear_mapa, agregar_marcador, agregar_linea

# Función de búsqueda
def busqueda(request):

    resultados = rutas.objects.none()

    filtro =  request.GET.get("busqueda","").strip()

    # Busca recorridos por código o nombre
    if filtro:
        resultados = rutas.objects.filter(codigo__icontains=filtro) | rutas.objects.filter(nombre__icontains=filtro)

        resultados = resultados.order_by("codigo")

    datos_busqueda = {
        "rutas": resultados,
        "busqueda": filtro,
    }

    return render(request, "index.html", datos_busqueda)


def recorrido(request, codigo):
    mapa = crear_mapa(-33.49024802460765, -70.61958173954261, 12)
    filtro = codigo
    lista = rutas.objects.filter(codigo=filtro).order_by('codigo')
    if not lista:
        return render(request, 'simulacion_busquedarecorrido.html', {'rutas': lista, 'mapa': mapa})
   
    # Elijo el viaje con más paradas (dirección principal) para dibujar el shape y los marcadores
    trip = None
    mayor = 0
    pares = Trip.objects.filter(ruta_id=filtro).values("sentido", "destino").distinct().order_by("sentido", "destino")
    for par in pares:
        candidato = Trip.objects.filter(ruta_id=filtro, sentido=par["sentido"], destino=par["destino"]).first()
        cantidad = StopTime.objects.filter(trip_id=candidato.trip_id).count()
        if cantidad > mayor:
            mayor = cantidad
            trip = candidato
    puntos = ShapePunto.objects.filter(shape_id=trip.shape_id).order_by('secuencia')
    
    stop = StopTime.objects.filter(trip_id=trip.trip_id)
    
    lista_puntos = []
    for l in puntos:
        lista_puntos.append([l.lat, l.lon])
    mapa = crear_mapa(lista_puntos[0][0], lista_puntos[0][1], 10.5)
    agregar_linea(mapa, lista_puntos, lista[0].color)
    for s in stop:
        parada = paradas.objects.filter(stop_id=s.parada_id)
        if filtro == "MTR":
            tramo_1 = ["Estación Central (Anden1)", "Estación San Bernardo (Anden1)"]
            tramo_2 = ["Estación BuinZoo", "Estación Buin", "Estación Linderos", "Estación Paine", "Estación Hospital"]
            tramo_3 = ["Estación San Francisco", "Estación Graneros", "Estación Rancagua"]
            if parada[0].nombre in tramo_1:
                nombre = "Tramo 1: "+parada[0].nombre
            elif parada[0].nombre in tramo_2:
                nombre = "Tramo 2: "+parada[0].nombre
            elif parada[0].nombre in tramo_3:
                nombre = "Tramo 3: "+parada[0].nombre
            agregar_marcador(mapa, parada[0].lat, parada[0].lon, nombre)
        else:
            agregar_marcador(mapa, parada[0].lat, parada[0].lon, parada[0].nombre)

    ruta = get_object_or_404(rutas, codigo=codigo)

    # Precios
    precios_recorrido = []
    tipo_precios = ""

    if ruta.agencia == "RM":
        precios_recorrido = precios_dtpm.objects.filter(tipo="bus")
        tipo_precios = "dtpm"

    elif ruta.agencia == "DTPR":
        precios_recorrido = precios_dtpr.objects.filter(codigo_recorrido=ruta.codigo)
        tipo_precios = "dtpr"

    elif ruta.agencia == "M":
        precios_recorrido = precios_dtpm.objects.filter(tipo__in=["metro_baja", "metro_valle", "metro_punta"])
        tipo_precios = "metro"
    elif ruta.agencia == "MT":
        precios_recorrido = precios_mtr.objects.all().order_by("tipo")
        tipo_precios = "mt"

    # Obtiene todos los viajes del recorrido
    viajes = Trip.objects.filter(ruta=ruta)

    paradas_por_sentido = []

    sentidos_viaje = viajes.values("sentido", "destino").distinct().order_by("sentido", "destino")

    # Por cada sentido me quedo solo con el destino que tiene más paradas (la dirección principal)
    principales = {}

    for sentido in sentidos_viaje:
        # Identifico el sentido
        viaje = viajes.filter(sentido=sentido["sentido"], destino=sentido["destino"]).first()

        # Tomo las paradas del recorrido para el viaje en específico (según el sentido)
        paradas_viaje = StopTime.objects.filter(trip=viaje).select_related("parada").order_by("secuencia")
        cantidad = paradas_viaje.count()

        if sentido["sentido"] not in principales or cantidad > principales[sentido["sentido"]]["cantidad"]:
            principales[sentido["sentido"]] = {
                "destino": sentido["destino"],
                "sentido": sentido["sentido"],
                "paradas": paradas_viaje,
                "cantidad": cantidad,
            }

    for clave in principales:
        paradas_por_sentido.append(principales[clave])


    # Hora de salida inicial y final del recorrido
    salida_inicial= Salida.objects.filter(trip__in=viajes).order_by("salida_seg").first()
    salida_final= Salida.objects.filter(trip__in=viajes).order_by("salida_seg").last()


    salidas = [salida_inicial, salida_final]
    horarios = []

    for salida in salidas:
        horas = salida.salida_seg // 3600
        resto = salida.salida_seg - horas * 3600
        minutos = resto // 60

        d = {
            "trip_id": salida.trip_id,
            "hora": f"{horas:02d}:{minutos:02d}",
        }

        horarios.append(d)

    # Obtener service_id
    servicios = viajes.values_list("service_id", flat=True).distinct()
    calendarios = calendario.objects.filter(service_id__in=servicios, red=ruta.red)

    dias_semana = [
    ("lunes", "lunes"),
    ("martes", "martes"),
    ("miercoles", "miércoles"),
    ("jueves", "jueves"),
    ("viernes", "viernes"),
    ("sabado", "sábado"),
    ("domingo", "domingo"),
]

    dias_activos = []

    for c in calendarios:
        for campo, nombre in dias_semana:
            if getattr(c, campo) == 1 and nombre not in dias_activos:
                dias_activos.append(nombre)

    if dias_activos:
        dias_funcionamiento = (
            f"Desde {dias_activos[0]} hasta {dias_activos[-1]}"
        )
    else:
        dias_funcionamiento = "Sin días de funcionamiento"
        

    

    # Tramos del MTR para mostrar en el details de paradas del html
    tramo_1 = ["Estación Central (Anden1)", "Estación San Bernardo (Anden1)"]
    tramo_2 = ["Estación BuinZoo", "Estación Buin", "Estación Linderos", "Estación Paine", "Estación Hospital"]
    tramo_3 = ["Estación San Francisco", "Estación Graneros", "Estación Rancagua"]

    datos_recorrido = {
        "ruta": ruta,
        "calendarios": calendarios,
        "horarios": horarios,
        "dias_funcionamiento": dias_funcionamiento,
        "paradas_por_sentido": paradas_por_sentido,
        "precios_recorrido": precios_recorrido,
        "tipo_precios": tipo_precios,
        "mapa": mapa,
        "tramo_1": tramo_1,
        "tramo_2": tramo_2,
        "tramo_3": tramo_3,
    }

    return render(request, "recorrido.html", datos_recorrido)
