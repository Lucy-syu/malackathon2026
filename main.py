import LoadData
import pandas as pd
consulta = "SELECT * FROM ENFERMEDAD WHERE INDICE=1 or INDICE=2"
print(LoadData.realizarConsulta(consulta))