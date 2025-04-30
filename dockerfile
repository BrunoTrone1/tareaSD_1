FROM python:3.13.3-slim

WORKDIR /app

# Instalar compiladores necesarios para construir numpy
RUN apt-get update && \
    apt-get install -y gcc g++ && \
    apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "almacenamiento/almacenamiento.py"]
