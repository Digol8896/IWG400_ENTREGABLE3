# Viajar sin Cortisol | Equipo4 P212 - Los SIMPson
En este repositorio se encuentra la funcionalidad corazon de nuestro equipo

# Instrucciones de ejecución

1. Importar el repositorio y crear un `venv` en la carpeta raíz del repositorio.

2. Con el `venv` activo, y desde la carpeta raíz del repositorio, instalar las dependencias:

   ```
   python -m pip install -r requeriments.txt
   ```

3) Ir al siguiente <a href="https://usmcl-my.sharepoint.com/:f:/g/personal/dgaldames_usm_cl/IgCizsb9CzylT6p-1F7kfZ4NAf0pRcse_JCGvNixzsZhIec?e=9fPL2l">enlace de Onedrive</a> (debe tener una cuenta de microsoft de la UTFSM para hacerlo) y descargar la carpeta `datos`.

4) Descomprimir la carpeta y llevar esta carpeta al mismo directorio donde esta manage.py (este paso es importante porque se requiere para poder generar la base de datos)

5) Una vez esta la carpeta `datos` a la altura de manage.py en el terminal (con el venv activo y con django y los otros requisitos instalados) debe ejecuar 3 comandos, primero `python manage.py migrate` luego `python manage.py importar_gtfs` y `python manage.py importar_precios`. Estos comandos permiten tener la base de datos funcional con los recorridos y precios para la ejecución de la funcionalidad corazon.
