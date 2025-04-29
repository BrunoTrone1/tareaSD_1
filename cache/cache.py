import redis
import json
import time

class SistemaCacheRedis:
    def __init__(self, policy="LRU", capacity=100, host='localhost', port=6379, db=0):
        self.capacity = capacity
        self.policy = policy.upper()
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.event_access_times = {}  # Solo si queremos manualmente LRU/LFU

    def _evict_if_needed(self):
        keys = self.r.keys()
        if len(keys) >= self.capacity:
            if self.policy == "LRU":
                # Usamos la última vez que se accedió
                oldest_key = min(self.event_access_times, key=lambda k: self.event_access_times[k])
            elif self.policy == "LFU":
                # Usamos la cantidad de accesos
                oldest_key = min(self.event_access_times, key=lambda k: self.event_access_times[k][1])
            else:
                raise ValueError("Política inválida")

            self.r.delete(oldest_key)
            del self.event_access_times[oldest_key]
            print(f"[CACHE] {self.policy} - Evento eliminado: {oldest_key}")

    def recibir_evento(self, evento):
        key = evento["uuid"]
        value = json.dumps(evento)  # Redis almacena strings
        self._evict_if_needed()
        self.r.set(key, value)

        # Actualizamos metadata para LRU/LFU
        now = time.time()
        if self.policy == "LRU":
            self.event_access_times[key] = now
        elif self.policy == "LFU":
            if key in self.event_access_times:
                count = self.event_access_times[key][1] + 1
            else:
                count = 1
            self.event_access_times[key] = (now, count)

        print(f"[CACHE] Evento almacenado: {key}")

    def get_evento(self, key):
        value = self.r.get(key)
        if value:
            now = time.time()
            if self.policy == "LRU":
                self.event_access_times[key] = now
            elif self.policy == "LFU":
                if key in self.event_access_times:
                    count = self.event_access_times[key][1] + 1
                else:
                    count = 1
                self.event_access_times[key] = (now, count)

            return json.loads(value)
        else:
            return None
