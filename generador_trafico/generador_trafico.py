import random
import time
import numpy as np
import logging
from pymongo import MongoClient
from cache.cache import SistemaCache
from config import config

# Configuración del logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Conexión a MongoDB
client = MongoClient(config.MONGO_URI)
db = client[config.MONGO_DB]
collection = db[config.MONGO_COLLECTION]

def obtener_evento_random():
    total = collection.count_documents({})
    if total == 0:
        return None
    random_index = random.randint(0, total - 1)
    evento = collection.find().skip(random_index).limit(1)[0]
    return evento

def enviar_evento(evento, cache):
    cache.recibir_evento(evento)
    logging.info(f"[EVENTO] Enviado: {evento['uuid']} -  {evento.get('city', 'Sin ubicación')} - {evento.get('nearBy', 'Sin ubicación')}")

def generador_trafico():
    logging.info(f"Iniciando generador de tráfico con distribución: {config.DISTRIBUCION}")
    
    cache = SistemaCache(policy=config.CACHE_POLICY, capacity=config.CACHE_CAPACITY)

    while True:
        if config.DISTRIBUCION == "poisson":
            intervalo = np.random.exponential(1 / config.LAMBDA)
        elif config.DISTRIBUCION == "uniforme":
            intervalo = config.INTERVALO_UNIFORME
        else:
            raise ValueError("Distribución no válida. Usa 'poisson' o 'uniforme'.")

        evento = obtener_evento_random()
        if evento:
            enviar_evento(evento, cache)
        else:
            logging.warning("No se encontró evento en la base de datos.")

        time.sleep(intervalo)

if __name__ == "__main__":
    try:
        generador_trafico()
    except KeyboardInterrupt:
        logging.info("Generador de tráfico detenido por el usuario.")
