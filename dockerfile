# Usa la imagen base (Python 3.13.3 en slim) con digest
FROM python:3.13.3-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala compiladores para numpy y librerías nativas
RUN apt-get update && \
    apt-get install -y gcc g++ && \
    apt-get clean

# Copia requirements.txt e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente
COPY . .

# El CMD se define en docker-compose por cada servicio
