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

Consulta empleada para la creación de la vista:
```SQL
CREATE OR REPLACE VIEW VISTA_MUY_INTERESANTE AS
SELECT 
    COUNT(*) AS total_casos,
    e."Comunidad Autónoma",
    e.SEXO,
    e."Diagnóstico Principal",
    e."Categoría",
    e.NIVEL_SEVERIDAD_APR,
    TRUNC(e.FECHA_DE_INICIO_CONTACTO) AS fecha_inicio_dia,
    AVG(e."Estancia Días") AS estancia_promedio_dias,
    AVG(e.COSTE_APR) AS coste_promedio,
    MIN(e.FECHA_DE_INICIO_CONTACTO) AS primera_fecha_contacto,
    MAX(e.FECHA_DE_INICIO_CONTACTO) AS ultima_fecha_contacto
FROM ENFERMEDAD e
WHERE e."Diagnóstico Principal" IS NOT NULL
GROUP BY 
    e."Comunidad Autónoma",
    e.SEXO,
    e."Diagnóstico Principal",
    e."Categoría",
    e.NIVEL_SEVERIDAD_APR,
    TRUNC(e.FECHA_DE_INICIO_CONTACTO)
ORDER BY e."Comunidad Autónoma", e.SEXO, total_casos DESC;
```