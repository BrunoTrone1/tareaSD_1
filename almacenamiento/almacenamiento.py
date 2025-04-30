import json
import os
import time
from pymongo import MongoClient
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

# Configuración desde entorno
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin@localhost:27017/?authSource=admin")
MONGO_DB = os.environ.get("MONGO_DB", "waze_db")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "alerts")
JSON_FILE_PATH = os.environ.get("JSON_FILE_PATH", "waze_alerts.json")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 30))

# Conexión
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def cargar_alertas():
    try:
        with open(JSON_FILE_PATH, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"No se pudo cargar el archivo JSON: {e}")
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
                logging.info(f"Insertada alerta {alert_uuid}")
            except Exception as e:
                logging.error(f"Al insertar alerta {alert_uuid}: {e}")
        else:
            logging.debug(f"Alerta ya existente: {alert_uuid}")
    return nuevas

if __name__ == "__main__":
    logging.info("Servicio de almacenamiento iniciado.")
    while True:
        logging.info("Chequeando si hay nuevas alertas para insertar...")
        nuevas = insertar_alertas_nuevas()
        logging.info(f"Se insertaron {nuevas} alertas nuevas.")
        time.sleep(CHECK_INTERVAL)
