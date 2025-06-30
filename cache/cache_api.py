import os
import time
import requests
from flask import Flask, request, jsonify
from cache import SistemaCacheNativo

app = Flask(__name__)

# Configuración de Redis desde variables de entorno
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Inicializa la cache
cache = SistemaCacheNativo(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# POST / : Guarda un evento directamente en cache
@app.route("/", methods=["POST"])
def guardar_en_cache():
    evento = request.get_json()
    if not evento:
        return jsonify({"error": "No se proporcionó evento"}), 400
    cache.set_evento(evento)
    return jsonify({"mensaje": "Evento guardado en cache"}), 200

# GET /consultar : Consulta por tipo (match_all o específico) e índice
@app.route("/consultar", methods=["GET"])
def consultar_y_cachear():
    tipo = request.args.get("tipo", "match_all")
    indice = request.args.get("indice", "hazards")

    consulta = { "query": { "match_all": {} } } if tipo == "match_all" else { "query": { "match": { "type": tipo } } }
    clave_cache = f"{indice}:{tipo}"

    inicio = time.time()
    resultado = cache.get_evento(clave_cache)

    if resultado:
        cache.registrar_hit(clave_cache)
        duracion = (time.time() - inicio) * 1000
        cache.registrar_tiempo(clave_cache, duracion)
        return jsonify({"fuente": "cache", "tiempo_ms": duracion, "datos": resultado})

    try:
        r = requests.get(
            f"http://elasticsearch:9200/{indice}/_search",
            headers={"Content-Type": "application/json"},
            json=consulta
        )
        datos = r.json().get("hits", {}).get("hits", [])
        cache.set_evento({"_id": clave_cache, "resultados": datos})
        cache.registrar_miss(clave_cache)
        duracion = (time.time() - inicio) * 1000
        cache.registrar_tiempo(clave_cache, duracion)
        return jsonify({"fuente": "elasticsearch", "tiempo_ms": duracion, "datos": datos})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET /estadisticas : TTL de todas las claves en Redis
@app.route("/estadisticas", methods=["GET"])
def estadisticas():
    claves = cache.get_all_keys()
    return jsonify([
        {"clave": clave, "ttl": cache.get_ttl(clave)}
        for clave in claves
    ])

# GET /estadisticas-avanzadas : Hits, misses y tiempos por clave
@app.route("/estadisticas-avanzadas", methods=["GET"])
def estadisticas_avanzadas():
    return jsonify(cache.obtener_estadisticas())

# Ejecutar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
