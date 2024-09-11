import pandas as pd

# Cargar el archivo CSV
input_file = 'output.csv'


# Leer el archivo CSV
data = pd.read_csv(input_file)

# Eliminar columnas duplicadas
data = data.loc[:, ~data.columns.duplicated()]

# Eliminar filas duplicadas en el índice
data = data.drop_duplicates()

# Restablecer el índice para evitar problemas de duplicados
data = data.reset_index(drop=True)

# Función para separar valores en las celdas que contengan comas
def separate_values(df):
    # Crear una nueva copia del DataFrame para trabajar con él
    new_df = df.copy()
    
    # Para cada columna del DataFrame, aplicar la separación de valores por coma
    for column in new_df.columns:
        new_df[column] = new_df[column].apply(lambda x: x.split(',') if isinstance(x, str) else [x])
    
    # Expandir las celdas que contienen listas en varias filas
    expanded_df = new_df.apply(pd.Series.explode)
    
    return expanded_df

# Aplicar la función para separar los valores
separated_data = separate_values(data)

# Guardar los resultados en un nuevo archivo Excel
output_file = '/mnt/data/output_separated_clean.xlsx'
separated_data.to_excel(output_file, index=False)

output_file
