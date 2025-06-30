SET default_parallel 1;
SET pig.exec.type local;

-- Cargar archivo TSV de alertas limpias
alerts = LOAD '/output/eventos_limpios.tsv'
  USING PigStorage('\t')
  AS (uuid:chararray, type:chararray, subtype:chararray, street:chararray, nearBy:chararray, x:double, y:double, pubMillis:long);

-- Filtrar solo alertas válidas con UUID, coordenadas y timestamp definidos
valid_alerts = FILTER alerts BY
  uuid IS NOT NULL AND uuid != '' AND
  x IS NOT NULL AND
  y IS NOT NULL AND
  pubMillis IS NOT NULL;

-- Guardar referencia de alertas válidas como incidentes
incidents = valid_alerts;

-- Eliminar duplicados exactos
distinct_incidents = DISTINCT incidents;

-- Convertir pubMillis a timestamp en segundos (Unix time)
hazards_with_time = FOREACH distinct_incidents GENERATE
  uuid,
  type,
  subtype,
  street,
  nearBy,
  x,
  y,
  (long)(pubMillis / 1000) AS timestamp;

-- Renombrar campos x/y para clarificar que son tipo double
coords_casted = FOREACH hazards_with_time GENERATE
  uuid,
  subtype,
  street,
  nearBy,
  x AS x_d,
  y AS y_d,
  timestamp;

-- Normalizar nombres y tipos de campos finales para salida estandarizada
normalized = FOREACH coords_casted GENERATE
  uuid,
  subtype,
  street,
  nearBy,
  x_d AS x_norm,
  y_d AS y_norm,
  (long)timestamp AS timestamp;

-- Agrupar por coordenadas y timestamp para eliminar posibles duplicados espaciales/temporales
grouped = GROUP normalized BY (x_norm, y_norm, timestamp);

-- Seleccionar solo una alerta por grupo (el primero) para evitar redundancias
standardized = FOREACH grouped {
  first = LIMIT normalized 1;
  GENERATE FLATTEN(first);
};

-- Guardar resultados finales como TSV
STORE standardized INTO '/output/eventos_procesados' USING PigStorage('\t');
