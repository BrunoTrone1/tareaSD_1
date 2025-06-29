SET default_parallel 1;
SET pig.exec.type local;

-- Cargar los datos limpios procesados
hazards = LOAD '/output/eventos_procesados' USING PigStorage('\t')
  AS (uuid:chararray, subtype:chararray, street:chararray, nearBy:chararray,
      x_norm:double, y_norm:double, timestamp:long);

-- 1. Conteo total de incidentes por comuna
agrupado_por_comuna = GROUP hazards BY nearBy;
conteo_por_comuna = FOREACH agrupado_por_comuna GENERATE
  group AS comuna,
  COUNT(hazards) AS total_incidentes;
STORE conteo_por_comuna INTO '/output/incidentes_por_comuna' USING PigStorage('\t');

-- 2. Conteo total de incidentes por tipo de incidente
agrupado_por_tipo = GROUP hazards BY subtype;
conteo_por_tipo = FOREACH agrupado_por_tipo GENERATE
  group AS tipo_incidente,
  COUNT(hazards) AS total_incidentes;
STORE conteo_por_tipo INTO '/output/incidentes_por_tipo' USING PigStorage('\t');

-- 3. Conteo total de incidentes por combinación de comuna y tipo
agrupado_por_comuna_tipo = GROUP hazards BY (nearBy, subtype);
conteo_por_comuna_tipo = FOREACH agrupado_por_comuna_tipo GENERATE
  group.nearBy AS comuna,
  group.subtype AS tipo_incidente,
  COUNT(hazards) AS total_incidentes;
STORE conteo_por_comuna_tipo INTO '/output/incidentes_por_comuna_y_tipo' USING PigStorage('\t');

-- 4. Conteo total de incidentes por calle
agrupado_por_calle = GROUP hazards BY street;
conteo_por_calle = FOREACH agrupado_por_calle GENERATE
  group AS calle,
  COUNT(hazards) AS total_incidentes;
STORE conteo_por_calle INTO '/output/incidentes_por_calle' USING PigStorage('\t');