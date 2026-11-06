# Proyecto Inicial
Repositorio para el proyecto y para las cosas en las que necesitemos trabajar con código. 
El repositorio esta divido en 2 carpetas principales, para trabajar en Django deben hacer usar la carpeta de `proyectoinicial` que es la del proyecto de Django

# Base de datos
La base de datos del proyecto requiere de una serie de pasos previos para poder ejecutarse debido a que esta no se sube a GitHub por motivos de seguridad y protección de datos. Es por esto que se
deja el paso a paso de como debe cargarse la base de datos para poder ejecutarse:

1) Descargar la carpeta datos desde el Onedrive. (Ubicada en la carpeta `base de datos recorrido` del onedrive proyecto inicial)
2) En caso de que este descomprimida hay que descomprimirla
3) Llevarla a la carpeta `"proyectoinicial"` del repositorio (en sus pc), como referencia hay que dejarla en la misma carpeta donde esta el script `manage.py`
4) Ir al terminal y hacer cd hasta llegar al directorio de django: Ejemplo `.../proyecto_inicial/proyectoinicial` (`...` representa las ruta que va antes del repo de github en el computador)
5) Escribir el comando `python manage.py migrate`
6) Escribir el comando `python manage.py importar_gtfs`
(Este comando puede demorarse en su ejecución.)
7) Escribir el comando `python manage.py importar_precios`

<b>Recordatorio: </b>Deben estar en el VENV con django para ejecutar los comandos.

Una vez realizados estos pasos van a tener la base de datos funcional con los recorridos. Es importante realizar este proceso debido a que sino no podran ejecutar las funciones del proyecto.

# Indicaciones

1) No modificar el .gitignore (esta hecho para evitar que se suban archivos para con datos personales, bases de datos o info de sus pc)
2) La carpeta bocetos html es donde van los HTML que vamos a usar para el modelo de baja fidelidad del entregable 2.

# Como ejecutar el prototipo de baja fidelidad
Hay 2 metodos para ejecutarlo:

<b>Metodo 1:</b>

Ir al sitio web <a href="https://simpson.digol8896.dev">simpson.digol8896.dev</a> y ahi podran ver el prototipo de baja fidelidad.

<b>Metodo 2:</b>

1) Abrir un terminal e ir a la carpeta donde se encuentra el modelo dentro del repositorio
2) escribir en la consola `python -m http.server 8000` (en caso de estar en macos o linux poner python3 en vez de python)
3) Abrir en el navegador la url `127.0.0.1:8000` y les apareceran los archivos de la carpeta, ahi seleccionen el html
Advertencia: Si el prototipo no se abre asi el mapa no se va a ver.

# Base de datos de recorridos

Los recorridos se basan de un sistema de datos llamado GTFS, es por esto que para poder agregarse a Django tuvieron que ser formateados en 8 tablas de bases de datos, por esto a continuación se muestra un diagrama ER que representa como estan diseñada la base de datos de los recorridos:

<img width="2700" height="2600" alt="diagrama_er_taller_estilo (1)" src="https://github.com/user-attachments/assets/6306e4a8-0781-4411-8eaf-72af0d7482c1" />
