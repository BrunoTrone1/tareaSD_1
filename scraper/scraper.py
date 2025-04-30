import requests
import json
import time
import os
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

def get_alerts(top, bottom, left, right):
    url = "https://www.waze.com/live-map/api/georss"
    params = {
        "top": top,
        "bottom": bottom,
        "left": left,
        "right": right,
        "env": "row",
        "types": "alerts"
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.waze.com/live-map",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error {response.status_code} al obtener datos para región: {top}, {bottom}, {left}, {right}")
        return None

def clean_alert(alert):
    alert.pop('comments', None)
    return alert

def save_alerts_to_json(alerts, filename="waze_alerts.json"):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(alerts, f, ensure_ascii=False, indent=4)
    logging.info(f"Datos guardados en {filename} (total {len(alerts)} alertas)")

def crawl_area(top, bottom, left, right, step_lat=0.01, step_lon=0.01, delay=1, filename="waze_alerts.json"):
    all_alerts = []

    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as f:
            try:
                all_alerts = json.load(f)
                logging.info(f"Se cargaron {len(all_alerts)} alertas previamente guardadas.")
            except json.JSONDecodeError:
                logging.warning("Archivo JSON existente estaba vacío o corrupto, empezando desde cero.")

    try:
        lat = bottom
        while lat < top:
            lon = left
            while lon < right:
                cell_top = min(lat + step_lat, top)
                cell_bottom = lat
                cell_left = lon
                cell_right = min(lon + step_lon, right)

                logging.info(f"Consultando celda: top={cell_top}, bottom={cell_bottom}, left={cell_left}, right={cell_right}")
                data = get_alerts(cell_top, cell_bottom, cell_left, cell_right)

                if data and 'alerts' in data:
                    cleaned_alerts = [clean_alert(alert) for alert in data['alerts']]
                    all_alerts.extend(cleaned_alerts)

                save_alerts_to_json(all_alerts, filename)
                lon += step_lon
                time.sleep(delay)

            lat += step_lat

    except KeyboardInterrupt:
        logging.warning("Interrupción manual detectada. Guardando progreso...")
        save_alerts_to_json(all_alerts, filename)
    except Exception as e:
        logging.error(f"Error inesperado: {e}. Guardando progreso...")
        save_alerts_to_json(all_alerts, filename)

    return all_alerts

# Configuración
TOP = -33.3
BOTTOM = -33.65
LEFT = -70.85
RIGHT = -70.5
STEP_LAT = 0.005
STEP_LON = 0.006
FILENAME = "waze_alerts.json"

# Ejecución
alerts = crawl_area(TOP, BOTTOM, LEFT, RIGHT, STEP_LAT, STEP_LON, delay=2, filename=FILENAME)
logging.info(f"Total de alertas recolectadas: {len(alerts)}")
logging.info(f"Datos finales guardados en {FILENAME}")
