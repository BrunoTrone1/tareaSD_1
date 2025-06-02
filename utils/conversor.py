# utils/exportar_a_tsv.py
import pymongo
import os
import csv

uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("MONGO_DB")
collection_name = os.environ.get("MONGO_COLLECTION")
output_path = os.environ.get("OUTPUT_PATH", "/data/eventos.tsv")

client = pymongo.MongoClient(uri)
collection = client[db_name][collection_name]

# Campos que quieres exportar
fields = ["uuid", "type", "subtype", "street", "nearBy", "location.x", "location.y", "pubMillis"]

with open(output_path, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(fields)  # encabezado
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
