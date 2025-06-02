-- Cargar el archivo TSV (tab separado)
alerts = LOAD '/input/eventos_limpios.tsv'
  USING PigStorage('\t')
  AS (uuid:chararray, type:chararray, subtype:chararray, street:chararray, nearBy:chararray, x:double, y:double, pubMillis:long);

-- Filtrar solo alertas de tipo HAZARD
hazards = FILTER alerts BY type == 'HAZARD';

-- Guardar resultados
STORE hazards INTO '/output/hazards' USING PigStorage('\t');
