# Plataforma de Análisis de Tráfico Urbano - Sistemas Distribuidos

Este proyecto simula una plataforma distribuida para el análisis de tráfico urbano usando datos de Waze. Incluye componentes para scraping, almacenamiento, generación sintética de tráfico, caching y exportación de datos, todo orquestado con Docker Compose.

---

## Tabla de Contenidos

- [Arquitectura del sistema](#arquitectura-del-sistema)
- [Servicios y tecnologías](#servicios-y-tecnologías)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instrucciones de ejecución](#instrucciones-de-ejecución)
- [Funcionamiento de la carga de archivos a Kibana](#funcionamiento-de-la-carga-de-archivos-a-Kibana)

---

## Arquitectura del sistema

El sistema está compuesto por los siguientes servicios (contenedores):

1. **MongoDB**: Base de datos NoSQL para almacenar eventos de tráfico.

2. **Mongo Express**: Interfaz web para visualizar y administrar MongoDB.

3. **Redis**: Sistema de caché en memoria para acelerar el acceso a eventos.

4. **Redis Commander**: Interfaz web para administrar Redis.

5. **Scraper**: Descarga eventos de tráfico desde la API de Waze, seleccionando solo los campos relevantes de las alertas, y los almacena en MongoDB.

6. **Almacenamiento**: Servicio encargado de limpiar la base de datos y los datos de alertas antes de la inserción, carga archivos JSON de alertas (como `waze_alerts.json`), y además descarga las alertas desde MongoDB para exportarlas a archivos TSV para análisis externo.

7. **Generador de tráfico**: Lee eventos de MongoDB y los envía masivamente a la caché Redis, simulando tráfico real.

8. **API de caché**: Servicio Flask que expone una API para almacenar y recuperar eventos en Redis con estadísticas de cacheo.

9. **Pig (Hadoop Pig)**: Contenedor para procesamiento avanzado de datos usando scripts Pig sobre HDFS (Hadoop Distributed File System), que permite procesamiento distribuido y análisis a gran escala.

10. **ElasticSearch**: Motor de búsqueda y análisis distribuido que indexa los datos para permitir consultas rápidas y agregaciones avanzadas.

11. **Kibana**: Interfaz gráfica para visualizar y analizar los datos indexados en ElasticSearch mediante dashboards dinámicos y personalizables.

Todos los servicios anteriores se ejecutan en contenedores Docker y se coordinan mediante Docker Compose, facilitando la instalación, configuración y escalabilidad del sistema completo.

---

## Servicios y tecnologías

- **MongoDB** y **Mongo Express**
- **Redis** y **Redis Commander**
- **Python 3.13.3-slim** (Flask, requests, pymongo, redis, numpy, etc.)
- **Docker** y **Docker Compose**
- **Hadoop Pig** con **HDFS** (opcional, para procesamiento avanzado distribuido)
- **ElasticSearch** y **Kibana** para indexación, búsqueda y visualización de datos
- **Almacenamiento** que realiza limpieza de la base de datos, carga de alertas JSON y exportación de datos a TSV

---

## Estructura del proyecto

```
tareaSD_1/
├── almacenamiento/
│   ├── almacenamiento.py
├── cache/
│   ├── cache.py
│   ├── cache_api.py
├── generador_trafico/
│   └── generador_trafico.py
├── pig-hadoop/
│   └── analisis_alertas.pig
│   └── procesar_alertas.pig  
│   └── run_pig.sh  
├── scraper/
│   └── scraper.py
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── dockerfile
├── README.md
└── requirements.txt
```

---

## Requisitos

- Docker y Docker Compose instalados y configurados en el sistema.
- Acceso a los siguientes puertos en la máquina anfitriona:
  - 27017 para MongoDB
  - 8081 para Mongo Express
  - 6379 para Redis
  - 8082 para Redis Commander
  - 9090 para la API de caché Flask
  - 9200 para ElasticSearch (si se utiliza)
  - 5601 para Kibana (si se utiliza)
- Python 3.13.3-slim como base en los contenedores Python.
- Suficientes recursos (CPU, memoria y disco) para ejecutar múltiples contenedores simultáneamente.
- Espacio en disco adecuado para almacenar los datos exportados y procesados, especialmente para HDFS y ElasticSearch.

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

   - El servicio almacenamiento realiza limpieza de la base de datos y prepara las alertas para su inserción.

   - Además, descarga las alertas almacenadas en MongoDB y las exporta a archivos TSV para análisis externo.

   - Puedes cargar eventos desde un archivo JSON usando este servicio.

   - Alternativamente, ejecuta el servicio scraper para descargar y seleccionar solo los campos relevantes de las alertas directamente desde la network de Waze y cargar la base de datos.

4. **Monitorea los servicios:**

   - Mongo Express (Interfaz web para gestionar MongoDB, user y password admin:admin): [http://localhost:8081](http://localhost:8081)
   - Redis Commander (Interfaz web para administrar Redis): [http://localhost:8082](http://localhost:8082)
   - Kibana (Dashboard para visualizar y analizar datos en ElasticSearch): [http://localhost:5601](http://localhost:5601)
   - Cache API (API Flask para gestión de caché en Redis):
      - Endpoint principal para guardar eventos: `POST http://localhost:9090/`
      - Consultar eventos cacheados y resultados de búsquedas: `GET http://localhost:9090/consultar?indice=hazards&tipo=match_all`
      - Ver estadísticas básicas de caché: `GET http://localhost:9090/estadisticas`
      - Ver estadísticas avanzadas (hits, misses, tiempos): `GET http://localhost:9090/estadisticas-avanzadas`
   ---

## Funcionamiento de la carga de archivos a Kibana

Después de ejecutar docker-compose up --build y procesar los datos con Hadoop Pig, seguir estos pasos:

    1. Procesamiento con Pig
    - Los scripts Pig generan resultados agregados como archivos en carpetas locales dentro del contenedor (o en volúmenes compartidos), por ejemplo:

      -  /output/incidentes_por_comuna/

      -  /output/incidentes_por_tipo/

      -  /output/incidentes_por_comuna_y_tipo/

      -  /output/incidentes_por_calle/

    2. Ubicación de archivos de salida
    - En cada carpeta de salida hay uno o más archivos con nombre tipo part-r-00000 que contienen los datos resultantes en formato tabulado.

    3. Cargar archivos a Elasticsearch usando Kibana

       - Abre la interfaz de Kibana en http://localhost:5601

       - Ve a la sección "Stack Management" > "Index Patterns" para crear un índice nuevo o selecciona uno existente.

       - Usa la función "File Data Visualizer" o la opción de importación para subir el archivo part-r-00000 de la carpeta correspondiente (descargado o accedido desde el volumen compartido).

       - Durante la importación, define el nombre del índice en Elasticsearch donde quieres que se almacenen estos datos (ejemplo: incidentes_por_comuna).

       - Kibana indexará los datos y podrás comenzar a crear visualizaciones y dashboards usando esos índices.

   4. Visualización

       - Una vez indexados los datos, usa las herramientas de Kibana para crear gráficos, tablas y análisis interactivos basados en los datos de incidentes.

       - Esto permite explorar los conteos por comuna, tipo de incidente, combinaciones, etc., facilitando el análisis urbano.


