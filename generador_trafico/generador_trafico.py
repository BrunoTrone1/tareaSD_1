import random
import time
import numpy as np
import logging
import os
import redis
import json
from pymongo import MongoClient
from datetime import datetime

# Configuración del logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Variables de entorno
MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB = os.environ["MONGO_DB"]
MONGO_COLLECTION = os.environ["MONGO_COLLECTION"]
DISTRIBUCION = os.environ.get("DISTRIBUCION", "uniforme")
LAMBDA = float(os.environ.get("LAMBDA", 2))
INTERVALO_UNIFORME = float(os.environ.get("INTERVALO_UNIFORME", 1))
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

# MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# Redis nativo
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def obtener_evento_random():
    total = collection.count_documents({})
    if total == 0:
        return None
    random_index = random.randint(0, total - 1)
    evento = collection.find().skip(random_index).limit(1)[0]

    # Convertir ObjectId a string para evitar el error de serialización
    evento["id"] = str(evento["_id"])  # Aquí se convierte el ObjectId a string
    del evento["_id"]  # Opcionalmente puedes eliminar el _id original si no lo necesitas
    return evento

def enviar_evento(evento):
    evento_id = evento["id"]
    evento_convertido = convertir_datetime_a_string(evento)

    try:
        # Buscar en Redis
        data = redis_client.get(evento_id)

        if data:
            logging.info(f"[CACHE HIT] Evento {evento_id} encontrado")
        else:
            # Si no existe, lo guardamos SIN TTL
            evento_json = json.dumps(evento_convertido)
            redis_client.set(evento_id, evento_json)  # ← SIN TTL
            logging.info(f"[CACHE MISS] Evento {evento_id} no encontrado, guardado en Redis")
    except redis.exceptions.ResponseError as e:
        if "OOM command not allowed when used memory" in str(e):
            logging.error("Redis ha alcanzado el límite de memoria y no puede agregar más eventos")
        else:
            logging.error(f"Error al interactuar con Redis: {e}")




def generador_trafico():
    logging.info(f"Generador iniciado con distribución {DISTRIBUCION}")
    contador = 0
    while True:
        # Tiempo entre eventos según la distribución
        if DISTRIBUCION == "poisson":
            intervalo = np.random.exponential(1 / LAMBDA)
        elif DISTRIBUCION == "uniforme":
            intervalo = INTERVALO_UNIFORME
        else:
            raise ValueError("Distribución no válida")

        evento = obtener_evento_random()
        if evento:
            enviar_evento(evento)
            contador += 1
            if contador % 10 == 0:
                logging.info(f"[INFO] Eventos enviados: {contador}")
        else:
            logging.warning("No hay eventos en MongoDB")

        time.sleep(intervalo)
    
def convertir_datetime_a_string(data):
    if isinstance(data, dict):
        # Recursivamente convertir todos los valores del diccionario
        return {key: convertir_datetime_a_string(value) for key, value in data.items()}
    elif isinstance(data, list):
        # Recursivamente convertir todos los elementos de la lista
        return [convertir_datetime_a_string(item) for item in data]
    elif isinstance(data, datetime):
        # Convertir el objeto datetime a formato ISO 8601
        return data.isoformat()
    else:
        return data

if __name__ == "__main__":
    try:
        generador_trafico()
    except KeyboardInterrupt:
        logging.info("Generador detenido")
