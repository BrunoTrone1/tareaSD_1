SET default_parallel 1;
SET pig.exec.type local;

alerts = LOAD '/data/eventos_limpios.tsv'
  USING PigStorage('\t')
  AS (uuid:chararray, type:chararray, subtype:chararray, street:chararray, nearBy:chararray, x:double, y:double, pubMillis:long);

-- Solo filtramos los que tienen coordenadas, tiempo y uuid válidos
valid_alerts = FILTER alerts BY
  uuid IS NOT NULL AND uuid != '' AND
  x IS NOT NULL AND
  y IS NOT NULL AND
  pubMillis IS NOT NULL;

incidents = valid_alerts;

distinct_incidents = DISTINCT incidents;

hazards_with_time = FOREACH distinct_incidents GENERATE
  uuid,
  type,
  subtype,
  street,
  nearBy,
  x,
  y,
  (long)(pubMillis / 1000) AS timestamp;

coords_casted = FOREACH hazards_with_time GENERATE
  uuid,
  subtype,
  street,
  nearBy,
  x AS x_d,
  y AS y_d,
  timestamp;

normalized = FOREACH coords_casted GENERATE
  uuid,
  subtype,
  street,
  nearBy,
  x_d AS x_norm,
  y_d AS y_norm,
  (long)timestamp AS timestamp;

grouped = GROUP normalized BY (x_norm, y_norm, timestamp);

standardized = FOREACH grouped {
  first = LIMIT normalized 1;
  GENERATE FLATTEN(first);
};

STORE standardized INTO '/output/hazards' USING PigStorage('\t');
