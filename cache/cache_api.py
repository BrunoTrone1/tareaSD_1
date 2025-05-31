import os
from flask import Flask, request, jsonify
from cache import SistemaCacheNativo

app = Flask(__name__)

# Usa variables de entorno para la conexión a Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

cache = SistemaCacheNativo(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

@app.route("/", methods=["POST"])
def guardar_en_cache():
    evento = request.get_json()
    if not evento:
        return jsonify({"error": "No se proporcionó evento"}), 400
    cache.set_evento(evento)
    return jsonify({"mensaje": "Evento guardado en cache"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
