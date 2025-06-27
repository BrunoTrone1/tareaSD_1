import json
import os
import time
import csv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
import logging

# Configuracion del sistema de logs
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

# Lectura de variables de entorno o valores por defecto
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin@localhost:27017/?authSource=admin")
MONGO_DB = os.environ.get("MONGO_DB", "waze_db")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "alerts")
JSON_FILE_PATH = os.environ.get("JSON_FILE_PATH", "almacenamiento/waze_alerts.json")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 10))
OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "/data/eventos_limpios.tsv")

# Conexion a MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# Funcion para eliminar documentos duplicados por uuid
def eliminar_duplicados_por_uuid():
    logging.info("Buscando duplicados por uuid...")
    pipeline = [
        {"$group": {
            "_id": "$uuid",
            "ids": {"$push": "$_id"},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gt": 1}}}
    ]

    total_eliminados = 0

    for grupo in collection.aggregate(pipeline):
        ids_a_eliminar = grupo["ids"][1:]  # conserva uno
        result = collection.delete_many({"_id": {"$in": ids_a_eliminar}})
        total_eliminados += result.deleted_count
        logging.info(f"Eliminados {result.deleted_count} duplicados de uuid: {grupo['_id']}")

    logging.info(f"Total de documentos duplicados eliminados: {total_eliminados}")

# Limpiar duplicados antes de crear índice
eliminar_duplicados_por_uuid()

# Crear un índice único por uuid (solo una vez)
collection.create_index("uuid", unique=True)

# Funcion para cargar el archivo JSON de alertas
def cargar_alertas():
    try:
        with open(JSON_FILE_PATH, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"No se pudo cargar el archivo JSON: {e}")
        return []

# Funcion que inserta alertas, evitando duplicados
def insertar_alertas():
    nuevas = 0
    data = cargar_alertas()
    for alert in data:
        uuid = alert.get("uuid")
        if not uuid:
            logging.warning("Alerta sin UUID, ignorada.")
            continue
        try:
            collection.insert_one(alert)
            nuevas += 1
            logging.info(f"Insertada alerta {uuid}")
        except DuplicateKeyError:
            logging.debug(f"Alerta duplicada {uuid}, no insertada.")
        except Exception as e:
            logging.error(f"Error al insertar alerta {uuid}: {e}")
    return nuevas

# Funcion para exportar los datos de la colección a un archivo TSV
def exportar_a_tsv():
    fields = ["uuid", "type", "subtype", "street", "nearBy", "location.x", "location.y", "pubMillis"]
    try:
        with open(OUTPUT_PATH, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(fields)  # encabezado
            for doc in collection.find():
                row = [
                    doc.get("uuid", ""),
                    doc.get("type", ""),
                    doc.get("subtype", ""),
                    doc.get("street", ""),
                    doc.get("nearBy", ""),
                    doc.get("location", {}).get("x", ""),
                    doc.get("location", {}).get("y", ""),
                    doc.get("pubMillis", ""),
                ]
                writer.writerow(row)
        logging.info(f"Exportacion TSV completada: {OUTPUT_PATH}")
    except Exception as e:
        logging.error(f"Error al exportar TSV: {e}")

# Bucle principal: ejecuta el chequeo periodicamente
if __name__ == "__main__":
    logging.info("Servicio de almacenamiento iniciado.")
    while True:
        logging.info("Insertando alertas desde JSON...")
        nuevas = insertar_alertas()
        logging.info(f"Se insertaron {nuevas} alertas nuevas.")
        exportar_a_tsv()
        time.sleep(CHECK_INTERVAL)
