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
    query = 'SELECT * FROM ENFERMEDAD WHERE UPPER("Comunidad Autónoma") = UPPER(:1) FETCH FIRST 10 ROWS ONLY'

    # pandas.read_sql maneja la conexión y los parámetros
    df = pd.read_sql(query, connection, params=[comunidad_autonoma])

    connection.close()
    return df


def realizarConsulta(consulta: str, params: list = None) -> pd.DataFrame:
    connection = conexionBD()
    try:
        df = pd.read_sql(consulta, connection, params=params or [])
        return df
    except oracledb.Error as e:
        print("Error en la consulta:", e)
        return pd.DataFrame()
    finally:
        connection.close()
        
def consultaLenguajeNatural(prompt: str) -> pd.DataFrame:
    """
    Realiza una consulta en lenguaje natural sobre la base de datos Oracle 
    y devuelve los resultados en un DataFrame.

    Args:
        prompt (str): Consulta en lenguaje natural.

    Returns:
        pd.DataFrame: Resultados de la consulta. Devuelve un DataFrame vacío si hay error.
    """
    connection = conexionBD()
    
    try:
        # Generar SQL desde lenguaje natural usando DBMS_CLOUD.AI_GENERATE_SQL
        plsql_block = f"""
        DECLARE
            l_sql CLOB;
        BEGIN
            l_sql := DBMS_CLOUD.AI_GENERATE_SQL(
                prompt => '{prompt}'
            );
            DBMS_OUTPUT.PUT_LINE(l_sql);
        END;
        """

        # Ejecutamos el bloque PL/SQL
        cursor = connection.cursor()
        cursor.execute(plsql_block)

        # Capturamos el SQL generado desde DBMS_OUTPUT
        # oracledb no captura automáticamente DBMS_OUTPUT, necesitamos activarlo:
        cursor.callproc("DBMS_OUTPUT.ENABLE")
        cursor.execute(plsql_block)

        output_lines = []
        while True:
            line = cursor.callfunc("DBMS_OUTPUT.GET_LINE", str, [None])
            if line is None:
                break
            output_lines.append(line)
        sql_generated = " ".join(output_lines)

        if not sql_generated.strip():
            print("No se generó SQL.")
            return pd.DataFrame()

        # Ejecutamos el SQL generado y devolvemos resultados
        df = pd.read_sql(sql_generated, connection)
        return df

    except oracledb.Error as e:
        print("Error en la consulta en lenguaje natural:", e)
        return pd.DataFrame()
    finally:
        connection.close()
