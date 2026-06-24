import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob

# --- 1. Ingesta por Lotes y Concatenación Dinámica ---
# Localiza todos los archivos que coinciden con el patrón especificado en el directorio
states = glob.glob("states*.csv")

status_files = []
for files in states:
    data = pd.read_csv(files)
    status_files.append(data)

# Consolidación en un único DataFrame maestro
us_census = pd.concat(status_files)

# --- 2. Limpieza de Variables Financieras y Demográficas ---
# Remoción de caracteres no numéricos en la columna de ingresos mediante Regex
us_census['Income'] = us_census['Income'].str.replace(r'[^\d.]', '', regex=True)
us_census['Income'] = us_census['Income'].astype(float)

# Eliminación de registros con campos críticos vacíos en la distribución de género
us_census = us_census.dropna(subset=["GenderPop"])

# Segmentación de la población por género mediante división de cadenas
us_census[["Men", "Women"]] = us_census["GenderPop"].str.split("_", expand=True)
us_census["Men"] = pd.to_numeric(us_census["Men"].str.replace("M", "", regex=False))
us_census["Women"] = pd.to_numeric(us_census["Women"].str.replace("F", "", regex=False))

# --- 3. Imputación Lógica de Valores Faltantes (Data Imputation) ---
# Deducción analítica de la población de mujeres basándose en el total y los hombres registrados
us_census['Women'] = us_census['Women'].fillna(us_census['TotalPop'] - us_census['Men'])

# --- 4. Remoción de Registros Duplicados ---
# Audita y remueve filas repetidas omitiendo el índice automático de la primera columna
census = us_census.drop_duplicates(subset=us_census.columns[1:])

# --- 5. Estandarización Porcentual de Distribuciones Étnicas ---
races = ['Hispanic', 'White', 'Black', 'Native', 'Asian', 'Pacific']
for race in races:
    for index in range(0, len(us_census)):    
        string = str(us_census[race].iat[index])
        replace = string.replace('%', '')
        if (replace == "nan"):
            replace = ""
        us_census[race].iat[index] = replace
    us_census[race] = pd.to_numeric(us_census[race])
    
# Imputación de la variable residual 'Pacific' deduciendo las proporciones conocidas
us_census['Pacific'] = us_census['Pacific'].fillna(100 - us_census['Hispanic'] - us_census['White'] - us_census['Black'] - us_census['Native'] - us_census['Asian'])

# Actualización del DataFrame limpio libre de duplicados
census = us_census.drop_duplicates(subset=us_census.columns[1:])

# --- 6. Pipeline de Visualización de Frecuencias ---
for race in races:
    plt.hist(census[race])
    plt.title("Histogram of the Percentage of {} People per State".format(race))
    plt.xlabel("Percentage")
    plt.ylabel("Frequency")
    plt.savefig(f"histograma_{race.lower()}.png")  # Exportación automática del gráfico
    plt.close()
