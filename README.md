# Plataforma de Análisis de Tráfico - Sistemas Distribuidos

Este proyecto es una simulación de una plataforma de análisis de tráfico urbano basada en datos de Waze. Implementa una arquitectura distribuida y modular, con componentes que permiten recolección, almacenamiento, generación sintética y caching de eventos de tráfico, todo contenido en servicios Docker.

---
## Contenidos

- [Arquitectura del sistema](#arquitectura-del-sistema)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instrucciones de ejecución](#instrucciones-de-ejecución)
- [Monitoreo de servicios](#monitoreo-de-servicios)
- [Uso](#uso)
- [Notas](#notas)
- [TODO](#todo)
- [Contribuciones](#contribuciones)

---

##  Arquitectura del sistema

1. **Scraper**: Extrae eventos de tráfico desde datos de Waze (reales o simulados).

2. **Almacenamiento**: Guarda los eventos obtenidos en MongoDB.

3. **Generador de tráfico**: Toma eventos aleatorios y los emite periódicamente a una caché Redis usando distribuciones Poisson o uniforme.

4. **Sistema de Caché**: Implementado sobre Redis. Permite políticas de reemplazo LFU o LRU.

---

## Tecnologías utilizadas:
- **MongoDB**: Base de datos NoSQL para almacenar eventos de tráfico.
- **Redis**: Sistema de caché para mejorar la eficiencia en la recuperación de datos.
- **Python**: Lenguaje de programación principal para el scraping, procesamiento de eventos y generación de tráfico.
- **Docker**: Contenedores para ejecutar los componentes de manera aislada.
- **Redis-Commander**: Interfaz web para administrar Redis.

---

## Estructura del proyecto
```
tareaSD_1/ 
├── almacenamiento/ 
│ └── almacenamiento.py 
├── cache/ 
│ └── cache.py 
├── generador_trafico/ 
│ └── generador_trafico.py 
├── scraper/ 
│ └── scraper.py 
├── waze_alerts.json 
├── Dockerfile 
├── docker-compose.yml 
├── requirements.txt 
└── README.md
```

---

## Requisitos

- Docker
- Docker Compose
- Python:3.13.3-slim
- Redis
- Redis Commander
- MongoDB
- MongoDB Express
- Conocimientos basicos de programacion

---

## Instrucciones de ejecución
1. Clonar el repositorio

`git clone https://github.com/BrunoTrone1/tareaSD_1.git`

`cd tareaSD_1`

2. Ejecutar la plataforma

`docker-compose up --build`

Esto levantará automáticamente:

- MongoDB + Mongo Express

- Redis + Redis Commander

- Scraper

- Almacenamiento

- Generador de tráfico

Cabe destacar que al comienzo no se tendran datos, por lo que se recomienda ejecutar el `scraper.py` para generar algunos eventos sobre los cuales trabajar.

---

## Monitoreo de servicios

- Mongo Express	`http://localhost:8081`

- Redis Commander `http://localhost:8082`

---

## Uso

El sistema empezará a funcionar automáticamente una vez que todos los contenedores estén levantados. El generador de tráfico comenzará a obtener eventos de la base de datos y los enviará a Redis, simulando un tráfico continuo de alertas. Los eventos se almacenarán en la caché de Redis y, si se solicitan nuevamente, se podrán obtener de la caché, lo que mejora la eficiencia.

---

## Notas

- Asegúrate de que tu red local permita el acceso a los puertos 8081 (Mongo Express) y 8082 (Redis Commander).

- Si experimentas problemas con el tamaño de la caché, puedes ajustar los parámetros de CACHE_CAPACITY.

---

## TODO

- Manejar inserciones automaticas del scraper a la DB!

## Contribuciones

Si deseas contribuir, por favor abre un pull request con tus cambios. Para nuevos desarrollos o mejoras, asegúrate de crear una nueva rama con un nombre descriptivo.