import os
import requests
import time
import logging
from pymongo import MongoClient
from random import gauss, choice

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Conexión a MongoDB usando variables de entorno
mongoClient = MongoClient(
    host="mongo",
    port=27017,
    username="admin",
    password="admin",
    authSource="admin",
    authMechanism='SCRAM-SHA-256'
)
MONGO_DB = os.getenv("MONGO_DB", "waze_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "alerts")

def get_events_db():
    """Obtiene todos los eventos de MongoDB."""
    eventos = list(mongoClient[MONGO_DB][MONGO_COLLECTION].find({}))
    logging.info(f"Recuperados {len(eventos)} eventos de MongoDB.")
    return eventos

def get_events_random(m=10000):
    """Genera m eventos aleatorios a partir de los existentes."""
    events = get_events_db()
    if not events:
        logging.warning("No hay eventos para el generador aleatorio.")
        return []
    result = list(events)
    while len(result) < m:
        result.append(choice(events))
    logging.info(f"Generados {len(result)} eventos aleatorios.")
    return result

def get_events_normal(m=10000):
    """Genera m eventos según una distribución normal."""
    events = get_events_db()
    n = len(events)
    if n == 0:
        logging.warning("No hay eventos para el generador normal.")
        return []
    mean, stddev = n / 2, n / 6
    weighted_events = []
    while len(weighted_events) < m:
        idx = max(0, min(n - 1, int(gauss(mean, stddev))))
        weighted_events.append(events[idx])
    logging.info(f"Generados {len(weighted_events)} eventos con distribución normal.")
    return weighted_events

def make_requests_events(events):
    """Envía los eventos al API de caché."""
    for i, event in enumerate(events, 1):
        event.pop("_id", None)
        try:
            resp = requests.post("http://cache_api:9090", json=event)
            if resp.status_code == 200:
                logging.info(f"[{i}/{len(events)}] Evento enviado correctamente.")
            else:
                logging.warning(f"[{i}/{len(events)}] Error al enviar evento: {resp.status_code}")
        except Exception as e:
            logging.error(f"[{i}/{len(events)}] Error: {e}")
        time.sleep(0.2)

def main():
    modo = os.getenv("MODO_DISTRIBUCION", "aleatorio")
    multiplicador = int(os.getenv("MULTIPLICADOR", "1"))
    logging.info(f"[Generador] MODO: {modo.upper()} x{multiplicador}")

    eventos_db = get_events_db()
    if not eventos_db:
        logging.warning("[Generador] No hay eventos en la base de datos.")
        return

    for ciclo in range(multiplicador):
        logging.info(f"Iniciando ciclo {ciclo+1}/{multiplicador}")
        eventos = get_events_normal() if modo == "normal" else get_events_random()
        make_requests_events(eventos)
        logging.info(f"Ciclo {ciclo+1} finalizado.")

if __name__ == "__main__":
    logging.info("Esperando 1 segundo para que los servicios estén listos...")
    time.sleep(1)
    main()
