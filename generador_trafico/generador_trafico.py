import random
import time
import numpy as np
import logging
import os
import redis
import json
from pymongo import MongoClient
from datetime import datetime

# Configuracion del logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Lectura de variables de entorno
MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB = os.environ["MONGO_DB"]
MONGO_COLLECTION = os.environ["MONGO_COLLECTION"]
DISTRIBUCION = os.environ.get("DISTRIBUCION", "uniforme")
LAMBDA = float(os.environ.get("LAMBDA", 2))
INTERVALO_UNIFORME = float(os.environ.get("INTERVALO_UNIFORME", 1))
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

# Conexion a MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# Conexion a Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Obtiene un evento aleatorio desde MongoDB
def obtener_evento_random():
    total = collection.count_documents({})
    if total == 0:
        return None
    random_index = random.randint(0, total - 1)
    evento = collection.find().skip(random_index).limit(1)[0]

    # Convierte el ObjectId a string y elimina el campo _id
    evento["id"] = str(evento["_id"])
    del evento["_id"]
    return evento

# Envia un evento a Redis (usa el ID como clave)
def enviar_evento(evento):
    evento_id = evento["id"]
    evento_convertido = convertir_datetime_a_string(evento)

    try:
        data = redis_client.get(evento_id)

        if data:
            logging.info(f"[CACHE HIT] Evento {evento_id} encontrado")
        else:
            redis_client.set(evento_id, json.dumps(evento_convertido))  # Guarda sin TTL
            logging.info(f"[CACHE MISS] Evento {evento_id} no encontrado, guardado en Redis")
    except redis.exceptions.ResponseError as e:
        if "OOM command not allowed when used memory" in str(e):
            logging.error("Redis alcanzo el limite de memoria")
        else:
            logging.error(f"Error al interactuar con Redis: {e}")

# Bucle principal del generador de trafico
def generador_trafico():
    logging.info(f"Generador iniciado con distribucion {DISTRIBUCION}")
    contador = 0
    while True:
        # Calcula el intervalo segun la distribucion seleccionada
        if DISTRIBUCION == "poisson":
            intervalo = np.random.exponential(1 / LAMBDA)
        elif DISTRIBUCION == "uniforme":
            intervalo = INTERVALO_UNIFORME
        else:
            raise ValueError("Distribucion no valida")

        evento = obtener_evento_random()
        if evento:
            enviar_evento(evento)
            contador += 1
            if contador % 10 == 0:
                logging.info(f"[INFO] Eventos enviados: {contador}")
        else:
            logging.warning("No hay eventos en MongoDB")

        time.sleep(intervalo)

# Convierte objetos datetime a string en estructuras anidadas
def convertir_datetime_a_string(data):
    if isinstance(data, dict):
        return {key: convertir_datetime_a_string(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convertir_datetime_a_string(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

# Inicio del generador
if __name__ == "__main__":
    try:
        generador_trafico()
    except KeyboardInterrupt:
        logging.info("Generador detenido")
