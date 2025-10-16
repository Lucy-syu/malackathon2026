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
        

def consultaNaturalGemini(pregunta: str) -> tuple[pd.DataFrame, str]:
    import google.generativeai as genai
    from dotenv import load_dotenv
    import os
    import pandas as pd

    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    connection = None
    sql_generado = ""

    try:
        connection = conexionBD()
        cursor = connection.cursor()

        # Descubrir esquema
        cursor.execute("""
            SELECT table_name, column_name
            FROM all_tab_columns
            WHERE owner = UPPER(:1)
            ORDER BY table_name, column_id
        """, [os.getenv("DB_USERNAME").upper()])
        esquema = {}
        for table, column in cursor:
            esquema.setdefault(table, []).append(column)

        print("Pregunta recibida:", pregunta)

        esquema_texto = "\n".join(f"{tabla}({', '.join(columnas)})" for tabla, columnas in esquema.items())

        prompt_sql = f"""
        Eres un asistente experto en SQL para Oracle. Genera solo la consulta SQL compatible con Oracle.
        Esquema de base de datos:
        {esquema_texto}

        Pregunta del usuario:
        {pregunta}
        """

        raw_sql = model.generate_content(prompt_sql)
        sql_generado = raw_sql.text.strip().strip("```sql").strip("```")
        sql_generado = sql_generado.replace(";", "").replace("\n", " ").replace("\t", " ")

        print("Consulta generada por Gemini:\n", sql_generado)

        df = pd.read_sql(sql_generado, connection)
        print("DataFrame shape:", df.shape)
        return df, sql_generado

    except Exception as e:
        print("Error al generar o ejecutar la consulta:", e)
        return pd.DataFrame(), ""

    finally:
        if connection:
            connection.close()
