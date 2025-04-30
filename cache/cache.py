import redis
import json

class SistemaCacheNativo:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def set_evento(self, evento):
        key = str(evento.get("id") or evento.get("_id"))
        self.redis.set(key, json.dumps(evento))  # Redis decide si elimina o no

    def get_evento(self, key):
        data = self.redis.get(key)
        return json.loads(data) if data else None
