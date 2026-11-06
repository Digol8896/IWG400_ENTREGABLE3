from django.db import models

# Create your models here.

class precios_dtpm(models.Model):
    tipo = models.CharField(max_length=100, primary_key=True)
    regular = models.DecimalField(max_digits=10, decimal_places=2)
    estudiante = models.DecimalField(max_digits=10, decimal_places=2)
    adulto_mayor = models.DecimalField(max_digits=10, decimal_places=2)

class precios_dtpr(models.Model):
    codigo_recorrido = models.CharField(max_length=100, primary_key=True)
    regular = models.DecimalField(max_digits=10, decimal_places=2)
    estudiante = models.DecimalField(max_digits=10, decimal_places=2)
    adulto_mayor = models.DecimalField(max_digits=10, decimal_places=2)

class precios_mtr(models.Model):
    tipo = models.CharField(max_length=100, primary_key=True)
    regular = models.DecimalField(max_digits=10, decimal_places=2)
    estudiante = models.DecimalField(max_digits=10, decimal_places=2)
    adulto_mayor = models.DecimalField(max_digits=10, decimal_places=2)
    discapacidad = models.DecimalField(max_digits=10, decimal_places=2)

class paradas(models.Model):
    stop_id = models.CharField(max_length=20, primary_key=True)
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    lat = models.FloatField()
    lon = models.FloatField()
    red = models.CharField(max_length=4)

class rutas(models.Model):
    codigo = models.CharField(max_length=20, primary_key=True)
    route_id = models.CharField(max_length=10)
    red = models.CharField(max_length=4)
    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=6)
    agencia = models.CharField(max_length=10)
    tipo = models.SmallIntegerField()

class calendario(models.Model):
    service_id = models.CharField(max_length=10)
    red = models.CharField(max_length=4)
    lunes = models.SmallIntegerField()
    martes = models.SmallIntegerField()
    miercoles = models.SmallIntegerField()
    jueves = models.SmallIntegerField()
    viernes = models.SmallIntegerField()
    sabado = models.SmallIntegerField()
    domingo = models.SmallIntegerField()
    inicio = models.CharField(max_length=8)
    fin = models.CharField(max_length=8)

class CalendarioExcepcion(models.Model):
    service_id = models.CharField(max_length=10)
    red = models.CharField(max_length=4)
    fecha = models.CharField(max_length=8)
    tipo = models.IntegerField()


class Trip(models.Model):
    trip_id = models.CharField(max_length=100, primary_key=True)
    ruta = models.ForeignKey(rutas, on_delete=models.CASCADE)
    service_id = models.CharField(max_length=10)
    red = models.CharField(max_length=4)
    shape_id = models.CharField(max_length=30)
    sentido = models.IntegerField()
    destino = models.CharField(max_length=100)


class Salida(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    salida_seg = models.IntegerField()
    exacta = models.IntegerField()


class StopTime(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    parada = models.ForeignKey(paradas, on_delete=models.CASCADE)
    secuencia = models.IntegerField()
    desfase_seg = models.IntegerField()


class ShapePunto(models.Model):
    shape_id = models.CharField(max_length=30, db_index=True)
    lat = models.FloatField()
    lon = models.FloatField()
    secuencia = models.IntegerField()