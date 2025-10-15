# Documentación
Para la instalación del proyecto se recomienda usar un entorno virtual de python

**Creación**
```
python -m venv venv
```

**Activación**
windows
```shell
.\venv\Scripts\activate
```
linux
```bash
source venv/bin/activate
```
**Configuración del proyecto**
Para que el proyecto funcione es necesario crear un fichero llamado .env que siguiendo la estructura .env.example tenga las columnas llenas con los datos correspondientes.

También es necesaria la wallet de la base de datos autonoma para que se ejecute poder acceder a ella.
# Retos
## Reto 1

1 - El usuario ha sido creado de manera exitosa

2 - La vista muy interesante ha sido creada también. 

Contenido de VISTA_MUY_INTERESANTE:
VISTA_MUY_INTERESANTE contiene datos claves para el analisis epidemológico y la gestion sanitaria de la tabla ENFERMEDAD.
Los datos que he considerado relevantes han sido:
- cantidad de casos
- comunidad autonoma
- sexo
- diagnostico principal
- categoría del diagnóstico 
- nivel de severidad
- fecha de inicio de contacto

Además de eso incluye metricas tales como la estancia promedio en días, el coste promedio por caso, y las fechas de contacto más temprana y reciente por grupo. Esta vista permite identificar tendencias en diagnósticos, costes hospitalarios, y severidad de casos por región, sexo, y día, facilitando decisiones en salud pública.