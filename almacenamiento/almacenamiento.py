import json
import os
import time
from pymongo import MongoClient
from datetime import datetime

# Configuraciones desde variables de entorno
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin@localhost:27017/?authSource=admin")
MONGO_DB = os.environ.get("MONGO_DB", "waze_db")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "alerts")
JSON_FILE_PATH = os.environ.get("JSON_FILE_PATH", "waze_alerts.json")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 30))

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def cargar_alertas():
    try:
        with open(JSON_FILE_PATH, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"[ERROR] No se pudo cargar el archivo JSON: {e}")
        return []

def insertar_alertas_nuevas():
    nuevas = 0
    data = cargar_alertas()
    for alert in data:
        alert_uuid = alert.get("uuid")
        if not alert_uuid:
            continue
        if not collection.find_one({"uuid": alert_uuid}):
            alert["ingreso_mongo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                collection.insert_one(alert)
                nuevas += 1
            except Exception as e:
                print(f"[ERROR] Al insertar alerta {alert_uuid}: {e}")
    return nuevas

if __name__ == "__main__":
    print("[INFO] Servicio de almacenamiento iniciado.")
    while True:
        print("[INFO] Chequeando si hay nuevas alertas para insertar...")
        nuevas = insertar_alertas_nuevas()
        print(f"[INFO] Se insertaron {nuevas} alertas nuevas.")
        time.sleep(CHECK_INTERVAL)
