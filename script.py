import requests
import csv
import os

# Paso 1: Obtener el Bearer Token
def get_bearer_token(client_id, client_secret):
    url = "https://orcid.org/oauth/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "/read-public"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(url, data=data, headers=headers)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        raise Exception(f"Error obteniendo el token: {response.status_code} - {response.text}")

# Paso 2: Obtener los registros ORCID
def get_orcid_records():
    url = 'https://pub.orcid.org/v3.0/expanded-search/?q=ror-org-id:"https://ror.org/00h9jrb69"'
    headers = {
        "Accept": "application/json"    
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["expanded-result"]
    else:
        raise Exception(f"Error obteniendo los registros ORCID: {response.status_code} - {response.text}")

# Paso 3: Guardar los ORCID_ID en un archivo
def save_orcid_ids(orcid_records, filename="data/orcid_id.txt"):
    with open(filename, 'w') as file:
        for record in orcid_records:
            file.write(f"{record['orcid-id']}\n")

# Paso 4: Leer ORCID_ID y obtener trabajos
def get_works(orcid_id, bearer_token):
    url = f"https://api.orcid.org/v3.0/{orcid_id}/works"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["group"]
    else:
        print(f"Error obteniendo los trabajos para ORCID ID {orcid_id}: {response.status_code} - {response.text}")
        return []


# Paso 5: Guardar los trabajos en un archivo CSV
def save_works_to_csv(orcid_id, works, filename="data/output.csv"):
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            "title", "external_id", "url", "type", 
            "publication_year", "publication_month", "publication_day", 
            "journal_title", "source_client_id"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for work in works:
            for summary in work.get("work-summary", []):
                external_id = ""
                if summary.get("external-ids") and summary["external-ids"].get("external-id"):
                    first_external_id = summary["external-ids"]["external-id"][0]
                    if first_external_id.get("external-id-normalized"):
                        external_id = first_external_id["external-id-normalized"].get("value", "")

                publication_date = summary.get("publication-date")
                publication_year = publication_date.get("year", {}).get("value", "") if publication_date and publication_date.get("year") else ""
                publication_month = publication_date.get("month", {}).get("value", "") if publication_date and publication_date.get("month") else ""
                publication_day = publication_date.get("day", {}).get("value", "") if publication_date and publication_date.get("day") else ""

                source_client_id = ""
                source = summary.get("source")
                if source and source.get("source-client-id"):
                    source_client_id = source["source-client-id"].get("path", "")

                url_value = summary.get("url", {}).get("value", "") if summary.get("url") else ""

                journal_title = summary.get("journal-title", {}).get("value", "") if summary.get("journal-title") else ""

                writer.writerow({
                    "title": summary.get("title", {}).get("title", {}).get("value", ""),
                    "external_id": external_id,
                    "url": url_value,
                    "type": summary.get("type", ""),
                    "publication_year": publication_year,
                    "publication_month": publication_month,
                    "publication_day": publication_day,
                    "journal_title": journal_title,
                    "source_client_id": orcid_id
                })

if __name__ == "__main__":
    # Reemplaza con tus credenciales
    client_id = "APP-OO3GAP5KY1T65G70"
    client_secret = "93a8255e-c84e-40bf-8f7d-ab3a72963add"
    
    action = input("¿Deseas crear un nuevo archivo orcid_id.txt o leer el existente? (crear/leer): ").strip().lower()
    # Obtener el token
    token = get_bearer_token(client_id, client_secret)
    if action == "crear":
        # Obtener los registros ORCID
        orcid_records = get_orcid_records()
        # Guardar los ORCID_ID en un archivo
        save_orcid_ids(orcid_records)
        print("ORCID_IDs guardados exitosamente en 'data/orcid_id.txt'.")

    input_file = "data/orcid_id.txt"
    output_file = "data/output.csv"
      
    if not os.path.exists(input_file):
        print(f"El archivo {input_file} no existe.")
    else:
        with open(input_file, 'r') as file:
            orcid_ids = file.readlines()
            
        for orcid_id in orcid_ids:
            orcid_id = orcid_id.strip()
            works = get_works(orcid_id,token)
            save_works_to_csv(orcid_id, works, output_file)
            
        print(f"Los datos de trabajos han sido guardados en '{output_file}'.")
