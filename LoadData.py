import oracledb
import os
from dotenv import load_dotenv


load_dotenv()

def conexionBD():

    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    dsn = os.getenv("DB_DSN")
    wallet_dir = os.getenv("DB_WALLET_DIR")
    wallet_password = os.getenv("DB_WALLET_PASSWORD")
    https_proxy_port = int(os.getenv("DB_HTTPS_PROXY_PORT", 80))

    connection = oracledb.connect(
        user=username,
        password=password,
        dsn=dsn,
        config_dir=wallet_dir,
        wallet_location=wallet_dir,
        wallet_password=wallet_password,
        https_proxy_port=https_proxy_port
    )

    print("Conectado a:", connection.version)
    return connection

def devolverPorComunidadAutonoma(comunidad_autonoma: str):
    connection = conexionBD()
    cursor = connection.cursor()
    
    # Configuramos rowfactory
    cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
    
    query = 'SELECT * FROM ENFERMEDADES WHERE UPPER("Comunidad Autónoma") = UPPER(:1)'
    cursor.execute(query, [comunidad_autonoma])
    
    resultados = cursor.fetchall()
    print("Resultados:", resultados)  # Depuración: imprime los resultados
    print("Tipo de la primera fila:", type(resultados[0]) if resultados else "Lista vacía")  # Depuración: verifica el tipo
    
    cursor.close()
    
    return resultados
def realizarConsulta(consulta:str)->str:
    connection = conexionBD()
    if not connection:
        return
    cursor = connection.cursor()

    try:
        cursor.execute(consulta)
        columnas = [col[0] for col in cursor.description]
        resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return resultados
    except oracledb.Error as e:
        print("Error en la consulta:", e)
        return []
    finally:
        cursor.close()
        connection.close()
