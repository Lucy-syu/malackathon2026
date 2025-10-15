import LoadData
import pandas as pd
prompt = "Muéstrame los 10 primeros pacientes con enfermedad respiratoria en Andalucía"
df = LoadData.consultaLenguajeNatural(prompt)
print(df.head())
