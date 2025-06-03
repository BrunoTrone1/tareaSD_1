import os
from flask import Flask, request, jsonify
from cache import SistemaCacheNativo

app = Flask(__name__)

# Usa variables de entorno para la conexión a Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Inicializa el sistema de cache nativo con Redis
cache = SistemaCacheNativo(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Ruta para guardar eventos en cache
@app.route("/", methods=["POST"])
def guardar_en_cache():
    # Obtiene el evento del cuerpo de la solicitud
    evento = request.get_json()
    if not evento:
        return jsonify({"error": "No se proporcionó evento"}), 400
    # Verifica que el evento tenga los campos necesarios
    cache.set_evento(evento)
    return jsonify({"mensaje": "Evento guardado en cache"}), 200

# Ruta para obtener eventos del cache
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
