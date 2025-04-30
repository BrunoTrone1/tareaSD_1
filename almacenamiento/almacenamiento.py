import json
from pymongo import MongoClient
from datetime import datetime

# Conexión a MongoDB dockerizado
client = MongoClient("mongodb://admin:admin@localhost:27017/?authSource=admin")
db = client["waze_db"]             # Crea (o conecta) a la base waze_db
collection = db["alerts"]           # Crea (o conecta) a la colección alerts

# Cargar el JSON que generaste en el scraper
with open("waze_alerts.json", "r") as f:
    data = json.load(f)             # data es una lista de alertas [{...}, {...}]

# Insertar los datos
for alert in data:
    # Opcional: agregar timestamp de ingreso
    alert["ingreso_mongo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        collection.insert_one(alert)
    except Exception as e:
        print(f"Error al insertar: {e}")

print(f"Se insertaron {len(data)} alertas (permitiendo duplicados)")

