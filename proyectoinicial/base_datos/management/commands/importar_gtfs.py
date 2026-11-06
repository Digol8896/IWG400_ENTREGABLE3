"""
Comando de Django para cargar a la base los 8 CSV unidos (carpeta datos/).
Ubicacion: tu_app/management/commands/importar_gtfs.py
Se ejecuta con:  python3 manage.py importar_gtfs   (desde la carpeta donde esta manage.py)

Cambia "tu_app" por el nombre de tu app, y los nombres de los modelos si los renombraste.
"""
import time
from django.core.management.base import BaseCommand
from base_datos.models import paradas, rutas, calendario, CalendarioExcepcion, Trip, Salida, StopTime, ShapePunto


class Command(BaseCommand):
    def handle(self, *args, **opciones):
        inicio = time.perf_counter()

        # 0) Borrar todo lo anterior, para no duplicar.
        # Primero las tablas que dependen de otras (las que tienen llave foranea).
        StopTime.objects.all().delete()
        Salida.objects.all().delete()
        Trip.objects.all().delete()
        CalendarioExcepcion.objects.all().delete()
        calendario.objects.all().delete()
        rutas.objects.all().delete()
        paradas.objects.all().delete()
        ShapePunto.objects.all().delete()

        # ------------------------------------------------------------------
        # 1) paradas: archivo grande -> se guarda por lotes (bulk_create)
        # ------------------------------------------------------------------
        lote = []
        arch = open("datos/paradas.csv", "r", encoding="utf-8")
        primera = True
        for l in arch:
            if not primera:
                l = l.strip().split(";")
                lote.append(paradas(stop_id=l[0], codigo=l[1], nombre=l[2],
                                    lat=l[3], lon=l[4], red=l[5]))
                if len(lote) == 5000:
                    paradas.objects.bulk_create(lote)
                    lote = []
            else:
                primera = False
        arch.close()
        if len(lote) > 0:
            paradas.objects.bulk_create(lote)
        print("paradas:", paradas.objects.count())

        # ------------------------------------------------------------------
        # 2) rutas: el codigo esta en la TERCERA columna del CSV (l[2])
        # ------------------------------------------------------------------
        lote = []
        arch = open("datos/rutas.csv", "r", encoding="utf-8")
        primera = True
        for l in arch:
            if not primera:
                l = l.strip().split(";")
                lote.append(rutas(codigo=l[2], route_id=l[0], red=l[1], nombre=l[3],
                                  color=l[4], agencia=l[5], tipo=int(l[6])))
                if len(lote) == 5000:
                    rutas.objects.bulk_create(lote)
                    lote = []
            else:
                primera = False
        arch.close()
        if len(lote) > 0:
            rutas.objects.bulk_create(lote)
        print("rutas:", rutas.objects.count())

        # ------------------------------------------------------------------
        # 3) calendario: archivo chico (9 filas) -> create, fila por fila
        # ------------------------------------------------------------------
        arch = open("datos/calendario.csv", "r", encoding="utf-8")
        primera = True
        for l in arch:
            if not primera:
                l = l.strip().split(";")
                calendario.objects.create(service_id=l[0], red=l[1], lunes=int(l[2]),
                    martes=int(l[3]), miercoles=int(l[4]), jueves=int(l[5]),
                    viernes=int(l[6]), sabado=int(l[7]), domingo=int(l[8]),
                    inicio=l[9], fin=l[10])
            else:
                primera = False
        arch.close()
        print("calendario:", calendario.objects.count())

        # ------------------------------------------------------------------
        # 4) calendario_excepciones: archivo chico (22 filas) -> create
        # ------------------------------------------------------------------
        arch = open("datos/calendario_excepciones.csv", "r", encoding="utf-8")
        primera = True
        for l in arch:
            if not primera:
                l = l.strip().split(";")
                CalendarioExcepcion.objects.create(service_id=l[0], red=l[1],
                                                   fecha=l[2], tipo=int(l[3]))
            else:
                primera = False
        arch.close()
        print("calendario excepciones:", CalendarioExcepcion.objects.count())

        # ------------------------------------------------------------------
        # 5) Trip: necesita el codigo de la ruta.
        # trips.csv trae route_id y red; el diccionario los traduce a codigo.
        # ------------------------------------------------------------------
        codigos = {}
        arch = open("datos/rutas.csv", "r", encoding="utf-8")
        primera = True
        for l in arch:
            if not primera:
                l = l.strip().split(";")
                codigos[(l[0], l[1])] = l[2]      # (route_id, red) -> codigo
            else:
                primera = False
        arch.close()

        lote = []
        arch = open("datos/trips.csv", "r", encoding="utf-8")
        primera = True
        for l in arch:
            if not primera:
                l = l.strip().split(";")
                lote.append(Trip(trip_id=l[0], red=l[1], ruta_id=codigos[(l[2], l[1])],
                                 service_id=l[3], shape_id=l[4], sentido=int(l[5]),
                                 destino=l[6]))
                if len(lote) == 5000:
                    Trip.objects.bulk_create(lote)
                    lote = []
            else:
                primera = False
        arch.close()
        if len(lote) > 0:
            Trip.objects.bulk_create(lote)
        print("trips:", Trip.objects.count())

        # ------------------------------------------------------------------
        # 6) Salida: llave foranea a Trip -> se pasa trip_id con el texto directo
        # ------------------------------------------------------------------
        lote = []
        arch = open("datos/salidas.csv", "r", encoding="utf-8")
        primera = True
        for l in arch:
            if not primera:
                l = l.strip().split(";")
                lote.append(Salida(trip_id=l[0], salida_seg=int(l[1]), exacta=int(l[2])))
                if len(lote) == 5000:
                    Salida.objects.bulk_create(lote)
                    lote = []
            else:
                primera = False
        arch.close()
        if len(lote) > 0:
            Salida.objects.bulk_create(lote)
        print("salidas:", Salida.objects.count())

        # ------------------------------------------------------------------
        # 7) StopTime: la tabla mas grande (2,4 millones de filas).
        # Dos llaves foraneas: trip_id y parada_id, con el texto directo.
        # ------------------------------------------------------------------
        lote = []
        arch = open("datos/stop_times.csv", "r", encoding="utf-8")
        primera = True
        for l in arch:
            if not primera:
                l = l.strip().split(";")
                lote.append(StopTime(trip_id=l[0], parada_id=l[1], secuencia=int(l[2]),
                                     desfase_seg=int(l[3])))
                if len(lote) == 5000:
                    StopTime.objects.bulk_create(lote)
                    lote = []
            else:
                primera = False
        arch.close()
        if len(lote) > 0:
            StopTime.objects.bulk_create(lote)
        print("stop_times:", StopTime.objects.count())

        # ------------------------------------------------------------------
        # 8) ShapePunto: los puntos del trazado de cada recorrido
        # ------------------------------------------------------------------
        lote = []
        arch = open("datos/trazados_shapes.csv", "r", encoding="utf-8")
        primera = True
        for l in arch:
            if not primera:
                l = l.strip().split(";")
                lote.append(ShapePunto(shape_id=l[0], lat=l[1], lon=l[2],
                                       secuencia=int(l[3])))
                if len(lote) == 5000:
                    ShapePunto.objects.bulk_create(lote)
                    lote = []
            else:
                primera = False
        arch.close()
        if len(lote) > 0:
            ShapePunto.objects.bulk_create(lote)
        print("shapes:", ShapePunto.objects.count())

        fin = time.perf_counter()
        print(f"Tiempo total: {fin - inicio:.1f} segundos")