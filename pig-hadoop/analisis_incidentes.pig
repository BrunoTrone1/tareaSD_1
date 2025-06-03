-- Cargar datos procesados previamente
hazards = LOAD '/output/hazards' USING PigStorage('\t')
  AS (uuid:chararray, subtype:chararray, street:chararray, nearBy:chararray,
      x_norm:double, y_norm:double, timestamp:long);

-- 1. Agrupar por comuna
group_by_commune = GROUP hazards BY nearBy;
incident_count_by_commune = FOREACH group_by_commune GENERATE
  group AS comuna,
  COUNT(hazards) AS total_incidentes;
STORE incident_count_by_commune INTO '/output/incidentes_por_comuna' USING PigStorage('\t');

-- 2. Frecuencia por tipo de incidente
group_by_tipo = GROUP hazards BY subtype;
incident_count_by_type = FOREACH group_by_tipo GENERATE
  group AS tipo_incidente,
  COUNT(hazards) AS total;
STORE incident_count_by_type INTO '/output/incidentes_por_tipo' USING PigStorage('\t');

-- 3. Evolución temporal por día
hazards_by_day = FOREACH hazards GENERATE
  uuid, subtype, nearBy, timestamp / 86400 AS dia;
group_by_day = GROUP hazards_by_day BY dia;
daily_count = FOREACH group_by_day GENERATE
  group AS dia,
  COUNT(hazards_by_day) AS total_incidentes;
STORE daily_count INTO '/output/incidentes_por_dia' USING PigStorage('\t');

-- 4. Tipo más frecuente por comuna y día
by_day_commune_type = FOREACH hazards GENERATE
  nearBy, subtype, (long)(timestamp / 86400) AS dia;
group_day_commune_type = GROUP by_day_commune_type BY (dia, nearBy, subtype);
count_day_commune_type = FOREACH group_day_commune_type GENERATE
  FLATTEN(group) AS (dia, comuna, tipo),
  COUNT(by_day_commune_type) AS total;
STORE count_day_commune_type INTO '/output/incidentes_por_dia_comuna_tipo' USING PigStorage('\t');
