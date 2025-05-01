import redis
import json

# Clase que implementa un sistema de cache usando Redis nativo
class SistemaCacheNativo:
    def __init__(self, host='localhost', port=6379, db=0):
        # Conexion a Redis
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    # Metodo para guardar un evento en Redis
    def set_evento(self, evento):
        key = str(evento.get("id") or evento.get("_id"))  # Usa 'id' o '_id' como clave
        self.redis.set(key, json.dumps(evento))  # Guarda el evento como JSON

    # Metodo para recuperar un evento desde Redis usando su clave
    def get_evento(self, key):
        data = self.redis.get(key)
        return json.loads(data) if data else None  # Devuelve el evento como dict si existe
