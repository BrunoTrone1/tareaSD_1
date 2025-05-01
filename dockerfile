# Usa la imagen base
FROM python:3.13.3-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Instalar compiladores necesarios para construir numpy
RUN apt-get update && \
    apt-get install -y gcc g++ && \
    apt-get clean

# Copia requirements.txt y instala las dependencias de Python.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto al contenedor
COPY . .

# Define el comando por defecto para ejecutar el script almacenamiento.py
CMD ["python", "almacenamiento/almacenamiento.py"]
