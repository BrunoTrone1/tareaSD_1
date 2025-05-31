import redis
import json

# Clase que implementa un sistema de cache usando Redis nativo
class SistemaCacheNativo:
    def __init__(self, host='localhost', port=6379, db=0):
        # Conexion a Redis
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    # Metodo para guardar un evento en Redis
    def set_evento(self, evento, ttl=300):  # TTL en segundos (300 = 5 minutos)
        key = str(evento.get("id") or evento.get("_id"))
        self.redis.set(key, json.dumps(evento), ex=ttl)


    # Metodo para recuperar un evento desde Redis usando su clave
    def get_evento(self, key):
        data = self.redis.get(key)
        if data:
            print(f"[CACHE HIT] Evento con clave {key} encontrado en cache.")
            return json.loads(data)
        else:
            print(f"[CACHE MISS] Evento con clave {key} no encontrado en cache.")
            return None