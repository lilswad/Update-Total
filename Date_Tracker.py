import requests
import pandas as pd
from datetime import datetime
import os

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
CARTERA_DB_ID = os.getenv("CARTERA_DB_ID")
HISTORIAL_DB_ID = os.getenv("HISTORIAL_DB_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
def get_portfolio_value():
    url = f"https://api.notion.com/v1/databases/{CARTERA_DB_ID}/query"
    response = requests.post(url, headers=headers)
    data = response.json()
    
    # Esto te dirá si el error es de autenticación o ID
    if "results" not in data:
        print(f"❌ Error de Notion: {data.get('message', 'Desconocido')}")
        print(f"Código de error: {data.get('code')}")
        return 0
    
    total_value = 0
    for row in data["results"]:
        try:
            # Extraemos el valor de la fórmula 'Valor Actual'
            properties = row["properties"]
            # Usamos .get() para evitar que el script se rompa si una fila está vacía
            formula_data = properties.get("Valor Actual", {}).get("formula", {})
            value = formula_data.get("number", 0)
            total_value += value
        except Exception as e:
            continue
            
    return total_value
def save_daily_snapshot(value):
    """Crea una nueva fila en la tabla de Historial."""
    url = "https://api.notion.com/v1/pages"
    date_now = datetime.now().strftime("%Y-%m-%d")
    
    new_page_data = {
        "parent": {"database_id": HISTORIAL_DB_ID},
        "properties": {
            "Fecha": {
                "date": {"start": date_now}
            },
            "Valor Total": {
                "number": value
            },
            "Nombre": { # Opcional: Nombre de la entrada
                "title": [{"text": {"content": f"Snapshot {date_now}"}}]
            }
        }
    }
    res = requests.post(url, headers=headers, json=new_page_data)
    if res.status_code == 200:
        print(f"✅ Snapshot guardado: ${value} el {date_now}")
    else:
        print(f"❌ Error: {res.text}")
# Ejecución
if __name__ == "__main__":
    current_value = get_portfolio_value()
    save_daily_snapshot(current_value)
