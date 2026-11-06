from django.contrib import admin
from django.urls import path
from inicio.views import inicio
#from django.contrib.auth import views as auth_views
from .views import *
urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name="register"),
]
