# Viajar sin Cortisol | Equipo4 P212 - Los SIMPson
En este repositorio se encuentra la funcionalidad corazon de nuestro equipo

# Instrucciones de instalación

1. Importar el repositorio y crear un `venv` en la carpeta raíz del repositorio.

2. Con el `venv` activo, y desde la carpeta raíz del repositorio, instalar las dependencias utilizando el siguiente comando:

   ```
   python -m pip install -r requeriments.txt
   ```

3. Descargar la carpeta `datos` desde [OneDrive](https://usmcl-my.sharepoint.com/:f:/g/personal/dgaldames_usm_cl/IgCizsb9CzylT6p-1F7kfZ4NAf0pRcse_JCGvNixzsZhIec?e=9fPL2l). Se necesita una cuenta Microsoft de la UTFSM.

4. Descomprimirla y dejarla **al mismo nivel que `manage.py`**. tal como se dejara en el ejemplo a continuación:

<img width="809" height="388" alt="image" src="https://github.com/user-attachments/assets/9b84b3b7-3890-4e87-94d1-078d01b7f38a" />

Este paso es obligatorio ya los comandos del siguiente paso leen los archivos desde esa ubicación.

5) Una vez haya realizado los pasos debe ir a un terminal, activar el VENV y quedar en la carpeta "proyectoinicial" del repositorio (donde se encuentra manage.py) tal como se muestra en la siguiente imagen:

<img width="771" height="66" alt="image" src="https://github.com/user-attachments/assets/b545c826-cc81-45f3-8c0d-5165e2e902dd" />

Es importante este paso porque el programa y los comandos a ejecutar dependen de estar ubicados correctamente.

6) Ingresar los siguientes comandos en el ortden que aparecen:

   ```
   python manage.py migrate
   python manage.py importar_gtfs
   python manage.py importar_precios
   ```
Si algún comando da error, verificar que la carpeta datos esta ubicada correctamente. Django debe ser capaz de encontrar todos los CSV que necesita de esa carpeta para poder generar la base de datos.

En caso de que de fallas la importación de la base de datos se dejara disponible una base de datos en la misma carpeta de [OneDrive](https://usmcl-my.sharepoint.com/:f:/g/personal/dgaldames_usm_cl/IgCizsb9CzylT6p-1F7kfZ4NAf0pRcse_JCGvNixzsZhIec?e=9fPL2l) del paso 3. Para utilizar esta base debe descargar el archivo db.sqlite3 y dejarlo en el directorio en el que esta manage.py (mismo lugar donde se dejo la carpeta `datos`)

Si este proceso se completa exitosamente podra realizar la ejecución del programa.

# Ejecución del programa

Para ejecutar el programa debe estar ubicado en la carpeta `proyectoinicial` (misma ubicación que para los comandos que se utilizaban para importar la base de datos).

Pasos para ejecutar la función corazon:

1) Ingresar el comando: `python manage.py runserver`

2) Ir en el navegador a `127.0.0.1:8000` o `localhost:8000` (El puerto puede variar en caso de que se elija otro al ejecutar el comando de runserver, el url ingresado corresponde al caso del dominio predeterminado)

3) Apretar el boton `Ir a rutas`, tambien puede usarse directamente el url `127.0.0.1:8000/rutas` o `localhost:8000/rutas`.

Una vez realizados estos pasos la función debería ser capaz de ejecutarse correctamente.
