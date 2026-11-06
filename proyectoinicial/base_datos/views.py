from django.shortcuts import render, redirect
from .models import *
import json
from mapa.funciones import *
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.core.exceptions import ValidationError
# Create your views here.

#----------------------------------------------

#Funciones Python

def enviar_conts(lista):
    return json.dumps(lista)

#Funciones Views Django

#---------------------------------------------

#Prueba de la base de datos
def base_inicio(request):
    return render(request, 'base.html')
#Base de datos de los recorridos

def base_prueba_recorridos(request):
    lista = rutas.objects.all().order_by('codigo')
    if request.method == 'POST':
        filtro = request.POST.get('codigo')
        lista = rutas.objects.filter(codigo__icontains=filtro).order_by('codigo')
    return render(request, 'base_recorridos.html', {'rutas': lista})
#Base de datos de las paradas

def base_prueba_paradas(request):
    lista = paradas.objects.all().order_by('stop_id')
    if request.method == 'POST':
        filtro = request.POST.get('nombre')
        lista = paradas.objects.filter(nombre__icontains=filtro).order_by('stop_id')
    return render(request, 'base_paradas.html', {'paradas': lista})

def base_prueba_trips(request):
    lista = Trip.objects.all().order_by('trip_id')
    if request.method == 'POST':
        filtro = request.POST.get('trip_id')
        lista = Trip.objects.filter(trip_id__icontains=filtro).order_by('trip_id')
    return render(request, 'base_trips.html', {'trips': lista})

def prueba_de_mapa(request):
    filtro = ""
    puntos = []

    mapa = crear_mapa(-33.49018527152, -70.6195230959199, 11.5)
    lista = rutas.objects.filter(codigo=filtro).order_by('codigo')
    if request.method == 'POST':
        filtro = request.POST.get('codigo')
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
    return render(request, 'simulacion_busquedarecorrido.html', {'rutas': lista, 'mapa': mapa})

def login_view_basedatos(request):

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home_manage') 
            
            else:
                messages.error(request, "Usuario o contraseña inválidos.")
        else:
            messages.error(request, "Usuario o contraseña inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'loginbdatos.html', {'form': form})

@login_required
def admin_home(request):
    return render(request, "manage_home.html")

@login_required
def admin_precios(request):
    if request.method == 'POST':
        tabla = request.POST.get('tabla')
        pk = request.POST.get('pk')

        if tabla == 'dtpm':
            modelo = precios_dtpm
            permiso = 'tuapp.change_precios_dtpm'
        elif tabla == 'dtpr':
            modelo = precios_dtpr
            permiso = 'tuapp.change_precios_dtpr'
        elif tabla == 'mtr':
            modelo = precios_mtr
            permiso = 'tuapp.change_precios_mtr'
        else:
            return HttpResponseForbidden()

        if not request.user.has_perm(permiso):
            return HttpResponseForbidden()

        fila = get_object_or_404(modelo, pk=pk)
        fila.regular = request.POST.get('regular')
        fila.estudiante = request.POST.get('estudiante')
        fila.adulto_mayor = request.POST.get('adulto_mayor')
        if tabla == 'mtr':
            fila.discapacidad = request.POST.get('discapacidad')

        try:
            fila.full_clean()
            fila.save()
        except ValidationError:
            messages.error(request, "Valor inválido en " + str(pk) + ". No se guardó.")
        return redirect(request.get_full_path())  

    tabla = request.GET.get('tabla')
    if tabla is None:
        if request.user.has_perm('tuapp.view_precios_dtpm'):
            tabla = 'dtpm'
        elif request.user.has_perm('tuapp.view_precios_dtpr'):
            tabla = 'dtpr'
        elif request.user.has_perm('tuapp.view_precios_mtr'):
            tabla = 'mtr'
    buscar = request.GET.get('buscar', '')

    lista_dtpm = []
    lista_dtpr = []
    lista_mtr = []
    total = 0

    if tabla == 'dtpm' and request.user.has_perm('tuapp.view_precios_dtpm'):
        lista_dtpm = precios_dtpm.objects.filter(tipo__icontains=buscar).order_by('tipo')
        total = lista_dtpm.count()
    elif tabla == 'dtpr' and request.user.has_perm('tuapp.view_precios_dtpr'):
        lista_dtpr = precios_dtpr.objects.filter(codigo_recorrido__icontains=buscar).order_by('codigo_recorrido')
        total = lista_dtpr.count()
    elif tabla == 'mtr' and request.user.has_perm('tuapp.view_precios_mtr'):
        lista_mtr = precios_mtr.objects.filter(tipo__icontains=buscar).order_by('tipo')
        total = lista_mtr.count()

    return render(request, 'manage_precios.html', {
        'dtpm': lista_dtpm,
        'dtpr': lista_dtpr,
        'mtr': lista_mtr,
        'tabla': tabla,
        'buscar': buscar,
        'total': total,
    })

def logout_bd(request):
    logout(request)
    return redirect('/')