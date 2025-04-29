from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# Generador de tráfico
DISTRIBUCION = os.getenv("DISTRIBUCION", "poisson")
LAMBDA = float(os.getenv("LAMBDA", 2))
INTERVALO_UNIFORME = float(os.getenv("INTERVALO_UNIFORME", 1))

# Cache
CACHE_POLICY = os.getenv("CACHE_POLICY", "LRU")
CACHE_CAPACITY = int(os.getenv("CACHE_CAPACITY", 100))
