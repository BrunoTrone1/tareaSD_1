# Plataforma de Análisis de Tráfico Urbano - Sistemas Distribuidos

Este proyecto simula una plataforma distribuida para el análisis de tráfico urbano usando datos de Waze. Incluye componentes para scraping, almacenamiento, generación sintética de tráfico, caching y exportación de datos, todo orquestado con Docker Compose.

---

## Tabla de Contenidos

- [Arquitectura del sistema](#arquitectura-del-sistema)
- [Servicios y tecnologías](#servicios-y-tecnologías)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instrucciones de ejecución](#instrucciones-de-ejecución)
- [Configuración y variables de entorno](#configuración-y-variables-de-entorno)
- [Monitoreo de servicios](#monitoreo-de-servicios)
- [Exportación de datos](#exportación-de-datos)
- [Notas y recomendaciones](#notas-y-recomendaciones)
- [Contribuciones](#contribuciones)

---

## Arquitectura del sistema

El sistema está compuesto por los siguientes servicios (contenedores):

1. **MongoDB**: Base de datos NoSQL para almacenar eventos de tráfico.
2. **Mongo Express**: Interfaz web para visualizar y administrar MongoDB.
3. **Redis**: Sistema de caché en memoria para acelerar el acceso a eventos.
4. **Redis Commander**: Interfaz web para administrar Redis.
5. **Scraper**: Descarga eventos de tráfico desde la API de Waze (o datos simulados) y los almacena en MongoDB.
6. **Almacenamiento**: Inserta nuevos eventos en MongoDB desde archivos JSON.
7. **Generador de tráfico**: Lee eventos de MongoDB y los envía masivamente a la caché Redis, simulando tráfico real.
8. **API de caché**: Servicio Flask que expone una API para almacenar y recuperar eventos en Redis.
9. **Conversor**: Exporta eventos de MongoDB a un archivo TSV para análisis externo.
10. **Pig**: Contenedor Hadoop Pig para procesamiento de datos (opcional/avanzado).

---

## Servicios y tecnologías

- **MongoDB** y **Mongo Express**
- **Redis** y **Redis Commander**
- **Python 3.13.3-slim** (Flask, requests, pymongo, redis, numpy, etc.)
- **Docker** y **Docker Compose**
- **Hadoop Pig** (opcional, para procesamiento avanzado)
- **CSV/TSV Export** (conversor)

---

## Estructura del proyecto

```
tareaSD_1/
├── almacenamiento/
│   ├── almacenamiento.py
│   ├── waze_alerts_test.json
│   └── waze_alerts_test copy.json
├── cache/
│   ├── cache.py
│   ├── cache_api.py
│   └── __init__.py
├── generador_trafico/
│   └── generador_trafico.py
├── scraper/
│   └── scraper.py
├── utils/
│   └── conversor.py
├── waze_alerts.json
├── requirements.txt
├── docker-compose.yml
├── dockerfile
└── README.md
```

---

## Requisitos

- Docker y Docker Compose
- Acceso a los puertos: 27017 (MongoDB), 8081 (Mongo Express), 6379 (Redis), 8082 (Redis Commander), 9090 (API de caché)
- Python 3.13.3-slim (usado en los contenedores)
- Recursos suficientes para varios contenedores simultáneos

---

## Instrucciones de ejecución

1. **Clona el repositorio:**

   ```sh
   git clone https://github.com/BrunoTrone1/tareaSD_1.git
   cd tareaSD_1
   ```

2. **Levanta la plataforma:**

   ```sh
   docker-compose up --build
   ```

   Esto iniciará todos los servicios definidos en `docker-compose.yml`.

3. **Carga datos iniciales:**

   - Puedes usar el servicio `almacenamiento` para cargar eventos desde un archivo JSON (`waze_alerts.json` o `almacenamiento/waze_alerts_test.json`).
   - O ejecuta el `scraper` para poblar la base de datos con datos simulados.

4. **Monitorea los servicios:**

   - Mongo Express: [http://localhost:8081](http://localhost:8081)
   - Redis Commander: [http://localhost:8082](http://localhost:8082)

---

## Configuración y variables de entorno

Las variables de entorno principales se configuran en `docker-compose.yml` para cada servicio. Ejemplo para el generador de tráfico:

```yaml
  generador_trafico:
    environment:
      - MONGO_URI=mongodb://admin:admin@mongo:27017/?authSource=admin
      - MONGO_DB=waze_db
      - MONGO_COLLECTION=alerts
      - DISTRIBUCION=poisson
      - LAMBDA=2
      - INTERVALO_UNIFORME=1
      - CACHE_POLICY=LFU
      - CACHE_CAPACITY=100
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
```

Puedes modificar la política de caché, la distribución de generación de tráfico, los nombres de base de datos y colección, y otros parámetros desde aquí.

---

## Monitoreo de servicios

- **Mongo Express:** [http://localhost:8081](http://localhost:8081)
- **Redis Commander:** [http://localhost:8082](http://localhost:8082)
- **Logs de servicios:**  
  Usa `docker logs <nombre_contenedor>` para ver los logs de cada servicio, por ejemplo:
  ```sh
  docker logs generador_trafico
  docker logs cache_api
  ```

---

## Exportación de datos

El servicio `conversor` permite exportar los eventos de MongoDB a un archivo TSV para análisis externo:

- El archivo se genera en `/data/eventos_limpios.tsv` (dentro del volumen compartido).
- Puedes modificar el nombre y ruta de salida con la variable `OUTPUT_PATH`.

---

## Notas y recomendaciones

- Si experimentas problemas de conexión, asegúrate de que todos los contenedores estén levantados y que los puertos no estén ocupados.
- Si la caché de Redis se llena, revisa la política de reemplazo (`allkeys-lfu` por defecto) y el tamaño máximo configurado.
- Puedes modificar los archivos JSON de alertas para probar distintos escenarios.
- El generador de tráfico puede configurarse para usar distintas distribuciones y volúmenes de eventos.

---

## Contribuciones

¿Quieres mejorar el proyecto?  
Abre un Pull Request o crea una Issue con tu propuesta.  
Para desarrollos mayores, crea una rama con un nombre descriptivo.

---

**Autor:**  
Bruno Trone  
Proyecto para la cátedra de Sistemas Distribuidos