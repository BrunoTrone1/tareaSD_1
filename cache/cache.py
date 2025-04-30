import redis
import json
import time
from datetime import datetime

class SistemaCacheRedis:
    def __init__(self, policy="LRU", capacity=100, host='localhost', port=6379, db=0):
        self.capacity = capacity
        self.policy = policy.upper()
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.uso = {}  # Guarda el tiempo o frecuencia de uso

        # Contadores para estadísticas
        self.hits = 0
        self.misses = 0

    def _evict(self):
        if len(self.uso) < self.capacity:
            return
        
        if self.policy == "LRU":
            key_a_borrar = min(self.uso, key=self.uso.get)
        elif self.policy == "LFU":
            key_a_borrar = min(self.uso, key=lambda k: self.uso[k][1])
        else:
            raise ValueError("Política no válida: usa LRU o LFU")

        self.redis.delete(key_a_borrar)
        del self.uso[key_a_borrar]
        print(f"[CACHE] Eliminado {key_a_borrar} por política {self.policy}")

    def recibir_evento(self, evento):
        if "_id" in evento:
            evento["id"] = str(evento["_id"])
            evento["_id"] = str(evento["_id"])
        key = evento["id"]
        value = json.dumps(evento)

        self._evict()
        self.redis.set(key, value)

        now = time.time()
        if self.policy == "LRU":
            self.uso[key] = now
        elif self.policy == "LFU":
            if key in self.uso:
                count = self.uso[key][1] + 1
            else:
                count = 1
            self.uso[key] = (now, count)

        print(f"[CACHE] Guardado evento {key}")

    def get_evento(self, key):
        data = self.redis.get(key)
        if data:
            self.hits += 1
            if self.policy == "LRU":
                self.uso[key] = time.time()
            elif self.policy == "LFU":
                if key in self.uso:
                    count = self.uso[key][1] + 1
                else:
                    count = 1
                self.uso[key] = (time.time(), count)
            return json.loads(data)
        else:
            self.misses += 1
            return None

    def convertir_datetime(self, data):
        if isinstance(data, dict):
            return {key: self.convertir_datetime(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.convertir_datetime(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data

    def estadisticas(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total) * 100 if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate (%)": round(hit_rate, 2),
            "total_requests": total
        }
