#!/bin/bash
set -e

# Verifica si el contenedor de Pig está en ejecución
echo "[INFO] Limpiando salidas anteriores..."
rm -rf /output/*

# Verifica si el contenedor de Pig está en ejecución
echo "[INFO] Ejecutando procesamiento de alertas..."
pig -x local /pig-hadoop/procesar_alertas.pig

# Verifica si el procesamiento se completó correctamente
echo "[INFO] Procesamiento completado. Ejecutando análisis..."
pig -x local /pig-hadoop/analisis_alertas.pig

# El análisis se completó correctamente
echo "[INFO] Análisis completado."