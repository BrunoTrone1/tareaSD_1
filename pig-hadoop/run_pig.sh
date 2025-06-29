#!/bin/bash
set -e

echo "[INFO] Limpiando salidas anteriores..."
rm -rf /output/*

echo "[INFO] Ejecutando procesamiento de alertas..."
pig -x local /pig-hadoop/procesar_alertas.pig

echo "[INFO] Procesamiento completado. Ejecutando análisis..."
pig -x local /pig-hadoop/analisis_alertas.pig

echo "[INFO] Análisis completado."