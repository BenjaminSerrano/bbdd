import pandas as pd

# Definir el mapeo de los campos de ORCID a DSpace CRIS
field_mapping = {
    "title": "dc.title",
    "external_id": "dc.identifier.doi",  # Ajustar según tipo
    "url": "dc.identifier.uri",
    "type": "dc.type",
    "publication_year": "dc.date.issued",  
    "publication_month": "dc.date.issued",  
    "publication_day": "dc.date.issued",  
    "journal_title": "dc.relation.ispartof",
    "source_client_id": "dc.source"
}

# Función para combinar la fecha
def combine_date(row):
    year = str(row['publication_year'])
    month = str(row['publication_month']).zfill(2) if not pd.isna(row['publication_month']) else "01"
    day = str(row['publication_day']).zfill(2) if not pd.isna(row['publication_day']) else "01"
    return f"{year}-{month}-{day}"

# Función para transformar los datos de ORCID a DSpace CRIS
def transform_orcid_to_dspace(input_file, output_file):
    # Detectar si el archivo es CSV o Excel
    if input_file.endswith('.csv'):
        # Leer el archivo CSV con coma como delimitador
        data = pd.read_csv(input_file, delimiter=',', skipinitialspace=True)
    elif input_file.endswith('.xlsx') or input_file.endswith('.xls'):
        # Leer el archivo Excel
        data = pd.read_excel(input_file)
    else:
        raise ValueError("El archivo debe ser en formato CSV o Excel.")

    # Crear un DataFrame vacío para los datos de DSpace CRIS
    dspace_data = pd.DataFrame()

    # Realizar el mapeo de los campos
    for orcid_field, dspace_field in field_mapping.items():
        if orcid_field in data.columns:
            # Si una columna tiene múltiples valores separados por coma, crear filas por separado
            dspace_data[dspace_field] = data[orcid_field].str.split(',').apply(lambda x: x[0] if isinstance(x, list) else x)

    # Combinar los campos de fecha (año, mes, día) en un solo campo 'dc.date.issued'
    if 'publication_year' in data.columns:
        dspace_data['dc.date.issued'] = data.apply(combine_date, axis=1)
    
    # Guardar el archivo transformado en el formato adecuado
    if output_file.endswith('.csv'):
        dspace_data.to_csv(output_file, index=False)
    elif output_file.endswith('.xlsx') or output_file.endswith('.xls'):
        dspace_data.to_excel(output_file, index=False)
    else:
        raise ValueError("El archivo de salida debe ser en formato CSV o Excel.")
    
    print(f"El archivo transformado ha sido guardado como {output_file}")

# Ejemplo de uso
input_file = "output.csv"  # Puede ser .csv o .xlsx
output_file = "dspace_cris_data.csv"  # Puede ser .csv o .xlsx

# Llamar a la función
transform_orcid_to_dspace(input_file, output_file)
