from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('', base_inicio, name='base_inicio'),
    path('recorridos/', base_prueba_recorridos, name='base_prueba_recorridos'),
    path('paradas/', base_prueba_paradas, name='base_prueba_paradas'),
    path('trips/', base_prueba_trips, name='base_prueba_trips'),
    path('prueba/', prueba_de_mapa, name='prueba_mapa'),
    path('login/', login_view_basedatos, name='login_bd'),
    path('manage/', admin_home, name='home_manage'),
    path('logout/', logout_bd, name='logout_bd'),
    path('manage_precios/', admin_precios, name="manage_precios")
]