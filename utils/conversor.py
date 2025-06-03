import pymongo
import os
import csv

# Obtener variables de entorno
uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("MONGO_DB")
collection_name = os.environ.get("MONGO_COLLECTION")
output_path = os.environ.get("OUTPUT_PATH", "/data/eventos.tsv")

# Conectar a MongoDB
client = pymongo.MongoClient(uri)
collection = client[db_name][collection_name]

# Campos a exportar
fields = ["uuid", "type", "subtype", "street", "nearBy", "location.x", "location.y", "pubMillis"]

# Abrir archivo de salida
with open(output_path, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(fields)  # Escribir encabezado

    for doc in collection.find():
        row = [
            doc.get("uuid", ""),
            doc.get("type", ""),
            doc.get("subtype", ""),
            doc.get("street", ""),
            doc.get("nearBy", ""),
            doc.get("location", {}).get("x", ""),
            doc.get("location", {}).get("y", ""),
            doc.get("pubMillis", ""),
        ]
        writer.writerow(row)
