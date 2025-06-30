import redis
import json
import time

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
        
    def get_all_keys(self):
        return self.redis.keys("*")

    def get_ttl(self, key):
        return self.redis.ttl(key)
    
    def registrar_hit(self, key):
        self.redis.hincrby(f"stats:{key}", "hits", 1)

    def registrar_miss(self, key):
        self.redis.hincrby(f"stats:{key}", "misses", 1)

    def registrar_tiempo(self, key, tiempo_ms):
        self.redis.hset(f"stats:{key}", "ultimo_tiempo_ms", round(tiempo_ms, 2))

    def obtener_estadisticas(self):
        claves = self.redis.keys("stats:*")
        resultado = []
        for clave in claves:
            stats = self.redis.hgetall(clave)
            resultado.append({
                "clave": clave.replace("stats:", ""),
                **stats
            })
        return resultado