from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import plotly.express as px
import LoadData
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ------------------------------
# Clase de usuario
# ------------------------------
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = LoadData.conexionBD()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM USUARIOS WHERE id = :1", [user_id])
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

# ------------------------------
# Función auxiliar para sanitizar inputs
# ------------------------------
def sanitize_input(value):
    if not value:
        return None
    value = re.sub(r'[^\w\s-]', '', value.strip())[:100]
    return value if value else None

# ------------------------------
# Funciones para generar gráficos
# ------------------------------
def generate_bar_chart(df, x_col, y_col, title):
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    return fig.to_html(full_html=False)

def generate_pie_chart(df, values_col, names_col, title):
    fig = px.pie(df, values=values_col, names=names_col, title=title)
    return fig.to_html(full_html=False)

def generate_histogram(df, x_col, title):
    fig = px.histogram(df, x=x_col, title=title)
    return fig.to_html(full_html=False)

# ------------------------------
# Función para generar gráficos
# ------------------------------
def generate_charts(df):
    """
    Generate various charts from a DataFrame.
    Returns a dictionary with HTML strings for each chart.
    """
    charts = {
        'plot_bar': None,
        'plot_pie': None,
        'plot_hist': None,
        'plot_diag': None,
        'plot_cat': None
    }
    
    if not df.empty:
        # Gráfico de barras: Casos por Comunidad Autónoma
        df_grouped_comunidad = df.groupby('Comunidad Autónoma').size().reset_index(name='Count')
        charts['plot_bar'] = generate_bar_chart(df_grouped_comunidad, 'Comunidad Autónoma', 'Count', 'Casos por Comunidad Autónoma')
        
        # Gráfico de pie: Distribución por Sexo
        df_grouped_sexo = df.groupby('SEXO').size().reset_index(name='Count')
        df_grouped_sexo['SEXO'] = df_grouped_sexo['SEXO'].map({1: 'Hombre', 2: 'Mujer', 0: 'Otro'})
        charts['plot_pie'] = generate_pie_chart(df_grouped_sexo, 'Count', 'SEXO', 'Distribución por Sexo')
        
        # Histograma: Distribución de Edades
        charts['plot_hist'] = generate_histogram(df, 'EDAD', 'Distribución de Edades')
        
        # Gráfico de pie: Top 10 Diagnósticos Principales
        if 'Diagnóstico Principal' in df.columns:
            df_diag = df['Diagnóstico Principal'].value_counts().reset_index()
            df_diag.columns = ['Diagnóstico Principal', 'Count']
            charts['plot_diag'] = generate_pie_chart(df_diag.head(10), 'Count', 'Diagnóstico Principal', 'Top 10 Diagnósticos Principales')
        
        # Gráfico de pie: Distribución por Categoría
        if 'Categoría' in df.columns:
            df_cat = df['Categoría'].value_counts().reset_index()
            df_cat.columns = ['Categoría', 'Count']
            charts['plot_cat'] = generate_pie_chart(df_cat, 'Count', 'Categoría', 'Distribución por Categoría')

    return charts
# ------------------------------
# Rutas de usuario
# ------------------------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = LoadData.conexionBD()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO USUARIOS (username, password) VALUES (:1, :2)", [username, hashed_password])
            conn.commit()
            flash('Usuario registrado con éxito!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print("Error al registrar usuario:", e)
            flash('El usuario ya existe o hubo un error.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = LoadData.conexionBD()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM USUARIOS WHERE username = :1", [username])
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1], user[2]))
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrecta', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ------------------------------
# Página principal (panel de navegación)
# ------------------------------
@app.route('/')
@login_required
def index():
    return render_template('index.html')  # panel de navegación

# ------------------------------
# Dashboard con filtros y gráficos
# ------------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    resultados = None
    if request.method == "POST":
        comunidades = [sanitize_input(c) for c in request.form.getlist("comunidad") if c]
        sexo = request.form.get("sexo")
        edad_min = request.form.get("edad_min")
        edad_max = request.form.get("edad_max")
        diagnosticos = request.form.getlist("diagnostico") 
        pacientes = request.form.get("numPacientes")
        
        consulta = 'SELECT * FROM ENFERMEDAD WHERE 1=1'
        params = []
        
        if comunidades:
            placeholders = []
            for c in comunidades:
                placeholders.append(f":{len(params)+1}")
                params.append(c.upper())
            consulta += f' AND UPPER("Comunidad Autónoma") IN ({", ".join(placeholders)})'
        if sexo and sexo.isdigit():
            consulta += ' AND SEXO = :{}'.format(len(params)+1)
            params.append(int(sexo))
        if edad_min and edad_min.isdigit():
            consulta += ' AND EDAD >= :{}'.format(len(params)+1)
            params.append(int(edad_min))
        if edad_max and edad_max.isdigit():
            consulta += ' AND EDAD <= :{}'.format(len(params)+1)
            params.append(int(edad_max))
        if diagnosticos:
            condiciones = []
            for d in diagnosticos:
                condiciones.append(f'UPPER("Diagnóstico Principal") LIKE UPPER(:{len(params)+1})')
                params.append(f"%{d}%")
            consulta += " AND (" + " OR ".join(condiciones) + ")"
        if pacientes:
            consulta += f' FETCH FIRST {pacientes} ROWS ONLY'
        else:
            consulta += ' FETCH FIRST 100 ROWS ONLY'
        
        try:
            if comunidades and len(params) == 1:
                df = LoadData.devolverPorComunidadAutonoma(comunidades)
            else:
                connection = LoadData.conexionBD()
                df = pd.read_sql(consulta, connection, params=params)
                connection.close()
            
            resultados = df.to_dict(orient='records')
            charts = generate_charts(df)  # Generate charts using the new function
            
        except Exception as e:
            return render_template("error.html", error=str(e))
        
        return render_template(
            "dashboard.html",
            resultados=resultados,
            **charts  
        )
    
    return render_template(
        "dashboard.html",
        resultados=None,
        plot_bar=None,
        plot_pie=None,
        plot_hist=None,
        plot_diag=None,
        plot_cat=None
    )


# ------------------------------
# Consulta por ID de enfermedad
# ------------------------------
@app.route('/usuario', methods=["GET", "POST"])
@login_required
def usuario():
    resultados = None
    if request.method == "POST":
        id_enfermedad = request.form.get("id")
        if id_enfermedad and id_enfermedad.isdigit():
            try:
                consulta = "SELECT * FROM ENFERMEDAD WHERE INDICE = :1"
                connection = LoadData.conexionBD()
                df = pd.read_sql(consulta, connection, params=[int(id_enfermedad)])
                connection.close()
                resultados = df.to_dict(orient='records')
            except Exception as e:
                return render_template("error.html", error=str(e))
        else:
            return render_template("error.html", error="ID inválido")
    return render_template("usuario.html", resultados=resultados)

# ------------------------------
# Consulta en lenguaje natural
# ------------------------------
@app.route('/lenguaje_natural', methods=['GET', 'POST'])
@login_required
def lenguaje_natural():
    resultados = None
    sql_generado = None  

    if request.method == 'POST':
        query_text = sanitize_input(request.form.get('query'))
        if query_text:
            try:
                df, sql_generado = LoadData.consultaNaturalGemini(query_text)
                resultados = df.to_dict(orient='records')
            except Exception as e:
                return render_template("error.html", error=str(e))
            try:
                charts = generate_charts(df)
            except Exception as chart_error:
                print("Error generando gráficos:", chart_error)

                charts = {
                    "plot_bar": None,
                    "plot_pie": None,
                    "plot_hist": None,
                    "plot_diag": None,
                    "plot_cat": None
                }
        
            charts = {
                    "plot_bar": None,
                    "plot_pie": None,
                    "plot_hist": None,
                    "plot_diag": None,
                    "plot_cat": None
            }
            #return render_template("error.html", error=str(e))

            return render_template(
                "lenguaje_natural.html",
                resultados=resultados,
                sql_generado=sql_generado,
                **charts
            )

    return render_template(
        "lenguaje_natural.html",
        resultados=None,
        sql_generado=None,
        plot_bar=None,
        plot_pie=None,
        plot_hist=None,
        plot_diag=None,
        plot_cat=None
    )
# ------------------------------
# Visión General (estadísticas generales)
# ------------------------------
@app.route('/vision_general')
@login_required
def vision_general():
    try:
        # Query to fetch all records (limited to avoid performance issues)
        consulta = 'SELECT * FROM ENFERMEDAD FETCH FIRST 1000 ROWS ONLY'
        connection = LoadData.conexionBD()
        df = pd.read_sql(consulta, connection)
        connection.close()

        # Generate charts
        charts = generate_charts(df)

        return render_template(
            "vision_general.html",
            **charts
        )
    except Exception as e:
        return render_template("error.html", error=str(e))

# ------------------------------
# Ejecutar app
# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=False)
