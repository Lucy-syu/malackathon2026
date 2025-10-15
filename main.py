import LoadData
import pandas as pd
prompt = "SELECT * FROM ENFERMEDAD"
df = LoadData.realizarConsulta(prompt)


print(df.head())


