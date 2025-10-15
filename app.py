from flask import Flask, render_template, request
from . import LoadData

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    resultados = None
    if request.method == "POST":
        comunidad = request.form.get("comunidad")
        LoadData.conexionBD()
        resultados = LoadData.devolverPorComunidadAutonoma(comunidad)
    return render_template("index.html", resultados = resultados)

if __name__ == '__main__':
    app.run(debug=True)

