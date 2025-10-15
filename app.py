from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import LoadData  # Tu módulo LoadData.py
import re  # Para sanitizar inputs

app = Flask(__name__)

# Función auxiliar para sanitizar inputs y evitar inyecciones SQL
def sanitize_input(value):
    if not value:
        return None
    # Eliminar caracteres peligrosos y limitar longitud
    value = re.sub(r'[^\w\s-]', '', value.strip())[:100]
    return value if value else None

# Funciones auxiliares para generar gráficos (reutilizables)
def generate_bar_chart(df, x_col, y_col, title):
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    return fig.to_html(full_html=False)

def generate_pie_chart(df, values_col, names_col, title):
    fig = px.pie(df, values=values_col, names=names_col, title=title)
    return fig.to_html(full_html=False)

def generate_histogram(df, x_col, title):
    fig = px.histogram(df, x=x_col, title=title)
    return fig.to_html(full_html=False)

@app.route('/', methods=["GET", "POST"])
def index():
    resultados = None
    plot_bar = None
    plot_pie = None
    plot_hist = None
    
    if request.method == "POST":
        # Obtener y sanitizar filtros del formulario
        comunidad = sanitize_input(request.form.get("comunidad"))
        sexo = request.form.get("sexo")
        edad_min = request.form.get("edad_min")
        edad_max = request.form.get("edad_max")
        diagnostico = sanitize_input(request.form.get("diagnostico"))
        
        # Construir consulta SQL con filtros
        consulta = 'SELECT * FROM ENFERMEDAD WHERE 1=1'
        params = []
        
        if comunidad:
            consulta += ' AND UPPER("Comunidad Autónoma") = UPPER(:1)'
            params.append(comunidad)
        if sexo and sexo.isdigit():
            consulta += ' AND SEXO = :{}'.format(len(params) + 1)
            params.append(int(sexo))
        if edad_min and edad_min.isdigit():
            consulta += ' AND EDAD >= :{}'.format(len(params) + 1)
            params.append(int(edad_min))
        if edad_max and edad_max.isdigit():
            consulta += ' AND EDAD <= :{}'.format(len(params) + 1)
            params.append(int(edad_max))
        if diagnostico:
            consulta += ' AND UPPER("Diagnóstico Principal") LIKE UPPER(:{})'.format(len(params) + 1)
            params.append(f'%{diagnostico}%')
        
        # Limitar resultados para rendimiento
        consulta += ' FETCH FIRST 100 ROWS ONLY'
        
        try:
            # Usar realizarConsulta, pero necesitamos ajustar porque no soporta params directamente
            if comunidad and len(params) == 1:
                # Usar la función específica si solo se filtra por comunidad
                df = LoadData.devolverPorComunidadAutonoma(comunidad)
            else:
                # Para consultas personalizadas, usamos realizarConsulta
                # Como no soporta params, usamos una versión modificada internamente
                connection = LoadData.conexionBD()
                df = pd.read_sql(consulta, connection, params=params)
                connection.close()
                
            resultados = df.to_dict(orient='records')
            
            # Generar visualizaciones si hay datos
            if not df.empty:
                # Gráfico de barras: Casos por Comunidad Autónoma
                df_grouped_comunidad = df.groupby('Comunidad Autónoma').size().reset_index(name='Count')
                plot_bar = generate_bar_chart(df_grouped_comunidad, 'Comunidad Autónoma', 'Count', 'Casos por Comunidad Autónoma')
                
                # Gráfico de pie: Distribución por Sexo
                df_grouped_sexo = df.groupby('SEXO').size().reset_index(name='Count')
                df_grouped_sexo['SEXO'] = df_grouped_sexo['SEXO'].map({1: 'Hombre', 2: 'Mujer', 0: 'Otro'})
                plot_pie = generate_pie_chart(df_grouped_sexo, 'Count', 'SEXO', 'Distribución por Sexo')
                
                # Histograma: Distribución de Edades
                plot_hist = generate_histogram(df, 'EDAD', 'Distribución de Edades')
        except Exception as e:
            return render_template("error.html", error=str(e))
    
    return render_template("index.html", resultados=resultados, plot_bar=plot_bar, plot_pie=plot_pie, plot_hist=plot_hist)

@app.route('/usuario', methods=["GET", "POST"])
def usuario():
    resultados = None
    if request.method == "POST":
        id_enfermedad = request.form.get("id")
        if id_enfermedad and id_enfermedad.isdigit():
            try:
                consulta = f"SELECT * FROM ENFERMEDAD WHERE INDICE = :1"
                connection = LoadData.conexionBD()
                df = pd.read_sql(consulta, connection, params=[int(id_enfermedad)])
                connection.close()
                resultados = df.to_dict(orient='records')
            except Exception as e:
                return render_template("error.html", error=str(e))
        else:
            return render_template("error.html", error="ID inválido")
    return render_template("usuario.html", resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)