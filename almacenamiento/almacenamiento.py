import json
from pymongo import MongoClient
from datetime import datetime

# Conexión a MongoDB dockerizado
client = MongoClient("mongodb://admin:admin@localhost:27017/?authSource=admin")
db = client["waze_db"]             # Crea (o conecta) a la base waze_db
collection = db["alerts"]           # Crea (o conecta) a la colección alerts

# Cargar el JSON que generaste en el scraper
with open("../waze_alerts.json", "r") as f:
    data = json.load(f)             # data es una lista de alertas [{...}, {...}]

# Insertar los datos
for alert in data:
    # Opcional: agregar timestamp de ingreso
    alert["ingreso_mongo"] = datetime.utcnow()

    # Insertar (puedes usar insert_one o insert_many si quieres en lote)
    collection.update_one(
        {"uuid": alert["uuid"]},    # Usa 'uuid' para evitar duplicados
        {"$set": alert},
        upsert=True                 # Crea si no existe
    )

print(f"Se insertaron {len(data)} alertas en MongoDB")
