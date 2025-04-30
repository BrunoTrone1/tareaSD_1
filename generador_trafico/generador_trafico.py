import random
import time
import numpy as np
import logging
import os
from pymongo import MongoClient
from cache.cache import SistemaCacheRedis

# Configuración del logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Leer variables de entorno
MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB = os.environ["MONGO_DB"]
MONGO_COLLECTION = os.environ["MONGO_COLLECTION"]
DISTRIBUCION = os.environ.get("DISTRIBUCION", "poisson")
LAMBDA = float(os.environ.get("LAMBDA", 2))
INTERVALO_UNIFORME = float(os.environ.get("INTERVALO_UNIFORME", 1))
CACHE_POLICY = os.environ.get("CACHE_POLICY", "LRU")
CACHE_CAPACITY = int(os.environ.get("CACHE_CAPACITY", 100))
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def obtener_evento_random():
    total = collection.count_documents({})
    if total == 0:
        return None
    random_index = random.randint(0, total - 1)
    evento = collection.find().skip(random_index).limit(1)[0]

    evento["id"] = str(evento["_id"])
    return evento

def enviar_evento(evento, cache):
    evento_id = evento["id"]

    # Intentar obtener el evento desde cache
    cache_hit = cache.get_evento(evento_id)

    if cache_hit:
        logging.info(f"[CACHE HIT] Evento ya estaba en cache: {evento_id}")
    else:
        # Si no está en cache, lo insertamos
        evento = cache.convertir_datetime(evento)
        cache.recibir_evento(evento)
        logging.info(f"[CACHE MISS] Evento agregado al cache: {evento_id} - {evento.get('city', 'Sin ubicación')}")


def generador_trafico():
    logging.info(f"Iniciando generador de tráfico con distribución: {DISTRIBUCION}")

    cache = SistemaCacheRedis(
        policy=CACHE_POLICY,
        capacity=CACHE_CAPACITY,
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB
    )

    contador_eventos = 0
    imprimir_cada_n = 10  # cada 10 eventos, mostrar estadísticas

    while True:
        if DISTRIBUCION == "poisson":
            intervalo = np.random.exponential(1 / LAMBDA)
        elif DISTRIBUCION == "uniforme":
            intervalo = INTERVALO_UNIFORME
        else:
            raise ValueError("Distribución no válida. Usa 'poisson' o 'uniforme'.")

        evento = obtener_evento_random()
        if evento:
            enviar_evento(evento, cache)
        else:
            logging.warning("No se encontró evento en la base de datos.")

        contador_eventos += 1
        if contador_eventos % imprimir_cada_n == 0:
            stats = cache.estadisticas()
            logging.info(f"[CACHE STATS] {stats}")

        time.sleep(intervalo)
        time.sleep(intervalo)

if __name__ == "__main__":
    try:
        generador_trafico()
    except KeyboardInterrupt:
        logging.info("Generador de tráfico detenido por el usuario.")
