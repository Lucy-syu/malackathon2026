from flask import Flask, render_template, request
import LoadData

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    resultados = None
    if request.method == "POST":
        comunidad = request.form.get("comunidad")
        df = LoadData.devolverPorComunidadAutonoma(comunidad)
        resultados = df.to_dict(orient='records')  # Convertimos DataFrame a lista de diccionarios
    return render_template("index.html", resultados=resultados)

@app.route('/usuario', methods=["GET", "POST"])
def usuario():
    resultados = None
    if request.method == "POST":
        id_enfermedad = request.form.get("id")
        consulta = f"SELECT * FROM ENFERMEDAD WHERE INDICE={id_enfermedad}"
        df = LoadData.realizarConsulta(consulta)
        resultados = df.to_dict(orient='records')  # Convertimos DataFrame a lista de diccionarios
    return render_template("usuario.html", resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)
