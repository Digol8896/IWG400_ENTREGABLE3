# Viajar sin Cortisol | Equipo4 P212 - Los SimpSON
En este repositorio se encuentra la funcionalidad corazon de nuestro equipo

# Instrucciones de ejecución

1) Importar el repositorio

2) Crear un `venv` de python en la carpeta raiz del repositorio y luego de activarlo escribir el comando `python -m pip install -r requeriments.txt` en caso de estar en MacOS o Linux se usa python3 en vez de python.

3) Ir al siguiente enlace de Onedrive (debe tener una cuenta de microsoft de la UTFSM para hacerlo) y descargar la carpeta `datos`.

4) Descomprimir la carpeta y llevar esta carpeta al mismo directorio donde esta manage.py (este paso es importante porque se requiere para poder generar la base de datos)

5) Una vez esta la carpeta `datos` a la altura de manage.py en el terminal (con el venv activo y con django y los otros requisitos instalados) debe ejecuar 3 comandos, primero `python manage.py migrate` luego `python manage.py importar_gtfs` y `python manage.py importar_precios`. Estos comandos permiten tener la base de datos funcional con los recorridos y precios para la ejecución de la funcionalidad corazon.
