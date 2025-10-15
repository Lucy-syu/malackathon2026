import LoadData
import pandas as pd
consulta = "SELECT * FROM ENFERMEDAD WHERE 'COMUNIDAD AUTÓNOMA' not in 'ANDALUCÍA'"
print(LoadData.realizarConsulta(consulta))