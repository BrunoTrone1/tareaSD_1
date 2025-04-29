import requests
import json
import time
import os

def get_alerts(top, bottom, left, right):
    url = "https://www.waze.com/live-map/api/georss"
    params = {
        "top": top,
        "bottom": bottom,
        "left": left,
        "right": right,
        "env": "row",
        "types": "alerts"  # Solo alerts
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
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
        print(f"Error {response.status_code} al obtener datos para región: {top}, {bottom}, {left}, {right}")
        return None

def clean_alert(alert):
    """Elimina el campo 'comments' de una alerta si existe."""
    alert.pop('comments', None)
    return alert

def save_alerts_to_json(alerts, filename="waze_alerts.json"):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(alerts, f, ensure_ascii=False, indent=4)
    print(f"Datos guardados en {filename} (total {len(alerts)} alertas)")

def crawl_area(top, bottom, left, right, step_lat=0.01, step_lon=0.01, delay=1, filename="waze_alerts.json"):
    all_alerts = []

    # Si existe archivo previo, cargarlo para continuar acumulando
    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as f:
            try:
                all_alerts = json.load(f)
                print(f"Se cargaron {len(all_alerts)} alertas previamente guardadas.")
            except json.JSONDecodeError:
                print("Archivo JSON existente estaba vacío o corrupto, empezando desde cero.")

    try:
        lat = bottom
        while lat < top:
            lon = left
            while lon < right:
                cell_top = min(lat + step_lat, top)
                cell_bottom = lat
                cell_left = lon
                cell_right = min(lon + step_lon, right)

                print(f"Consultando celda: top={cell_top}, bottom={cell_bottom}, left={cell_left}, right={cell_right}")
                data = get_alerts(cell_top, cell_bottom, cell_left, cell_right)

                if data and 'alerts' in data:
                    # Limpiar cada alerta antes de agregarla
                    cleaned_alerts = [clean_alert(alert) for alert in data['alerts']]
                    all_alerts.extend(cleaned_alerts)

                # Guardar tras cada celda
                save_alerts_to_json(all_alerts, filename)

                lon += step_lon
                time.sleep(delay)

            lat += step_lat

    except KeyboardInterrupt:
        print("\nInterrupción manual detectada. Guardando progreso...")
        save_alerts_to_json(all_alerts, filename)
    except Exception as e:
        print(f"\nError inesperado: {e}. Guardando progreso...")
        save_alerts_to_json(all_alerts, filename)

    return all_alerts

# -------------------- Configuración --------------------

# Coordenadas de la Región Metropolitana, por ejemplo
TOP = -33.3
BOTTOM = -33.7
LEFT = -70.9
RIGHT = -70.5

STEP_LAT = 0.009  # Tamaño de celda en latitud (~2 km aprox)
STEP_LON = 0.01075  # Tamaño de celda en longitud (~2 km aprox)

FILENAME = "waze_alerts.json"

# -------------------- Ejecución --------------------

alerts = crawl_area(TOP, BOTTOM, LEFT, RIGHT, STEP_LAT, STEP_LON, delay=60, filename=FILENAME)
print(f"Total de alertas recolectadas: {len(alerts)}")
print(f"Datos finales guardados en {FILENAME}")
