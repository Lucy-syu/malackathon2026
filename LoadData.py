import oracledb
import os
from dotenv import load_dotenv
import pandas as pd

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
    """
    Devuelve un DataFrame con las filas de la tabla ENFERMEDADES 
    filtradas por la Comunidad Autónoma especificada.

    Args:
        comunidad_autonoma (str): Nombre de la Comunidad Autónoma por la que filtrar. 
                                  La comparación se realiza sin distinguir mayúsculas/minúsculas.

    Returns:
        pd.DataFrame: DataFrame con todas las columnas de la tabla ENFERMEDADES 
                      correspondientes a la Comunidad Autónoma indicada. 
                      Devuelve un DataFrame vacío si no se encuentran registros.

    Raises:
        oracledb.Error: Si hay un error al conectar o ejecutar la consulta en la base de datos.
    """
    
    connection = conexionBD()
    query = 'SELECT * FROM ENFERMEDADES WHERE UPPER("Comunidad Autónoma") = UPPER(:1)'

    # pandas.read_sql maneja la conexión y los parámetros
    df = pd.read_sql(query, connection, params=[comunidad_autonoma])

    connection.close()
    return df


def realizarConsulta(consulta:str)->str:
    connection = conexionBD()
    if not connection:
        return

    try:
        df = pd.read_sql(consulta, connection)
        return df
    except oracledb.Error as e:
        print("Error en la consulta:", e)
        return []
    finally:
        connection.close()
