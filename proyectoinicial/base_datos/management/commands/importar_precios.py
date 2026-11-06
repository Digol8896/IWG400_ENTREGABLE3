from django.core.management.base import BaseCommand
from base_datos.models import precios_dtpm, precios_dtpr, precios_mtr


def leer_lineas(ruta):
    with open(ruta, encoding="utf-8-sig") as archivo:
        lineas = archivo.readlines()
    return lineas[1:]


def importar_dtpm():
    lineas = leer_lineas("datos/precios_dtpm.csv")
    precios_dtpm.objects.all().delete()
    total = 0
    for linea in lineas:
        if linea.strip() != "":
            partes = linea.strip().split(";")
            precios_dtpm(
                tipo=partes[0],
                regular=partes[1],
                estudiante=partes[2],
                adulto_mayor=partes[3],
            ).save()
            total = total + 1
    return total


def importar_dtpr():
    lineas = leer_lineas("datos/precios_dtpr.csv")
    precios_dtpr.objects.all().delete()
    total = 0
    for linea in lineas:
        if linea.strip() != "":
            partes = linea.strip().split(";")
            precios_dtpr(
                codigo_recorrido=partes[0],
                regular=partes[1],
                estudiante=partes[2],
                adulto_mayor=partes[3],
            ).save()
            total = total + 1
    return total


def importar_mtr():
    lineas = leer_lineas("datos/precios_mtr.csv")
    precios_mtr.objects.all().delete()
    total = 0
    for linea in lineas:
        if linea.strip() != "":
            partes = linea.strip().split(";")
            precios_mtr(
                tipo=partes[0],
                regular=partes[1],
                estudiante=partes[2],
                adulto_mayor=partes[3],
                discapacidad=partes[4],
            ).save()
            total = total + 1
    return total


class Command(BaseCommand):
    help = "Importa los precios de DTPM, DTPR y EFE (MTR) desde los CSV de base_datos/datos"

    def handle(self, *args, **options):
        total_dtpm = importar_dtpm()
        print("DTPM:", total_dtpm, "filas")
        total_dtpr = importar_dtpr()
        print("DTPR:", total_dtpr, "filas")
        total_mtr = importar_mtr()
        print("MTR (EFE):", total_mtr, "filas")
