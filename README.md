# Generador de Órdenes de Pago - CAMSA SRL

Aplicación de escritorio desarrollada en Python para automatizar la generación de órdenes de pago a partir de datos exportados desde Excel.

## Descripción

Este sistema permite cargar una base de datos de movimientos financieros, seleccionar profesionales y generar comprobantes en formato PDF de manera rápida, ordenada y repetitiva, optimizando el proceso administrativo.

## Funcionalidades

- Importación de base de datos desde archivos Excel (.xlsx / .xls)
- Listado de profesionales disponibles para procesar
- Separación entre:
  - Profesionales pendientes
  - Profesionales procesados
- Visualización detallada de operaciones:
  - Mes correspondiente
  - Número de operación
  - Fecha de transferencia
  - Importe
- Generación automática de PDF por profesional
- Inclusión en el PDF de:
  - Logo institucional
  - Datos del proveedor
  - Tabla de movimientos
  - Total calculado
  - Observaciones
  - Fecha de procesamiento editable
  - Firmas digitales
- Selección de carpeta de guardado persistente durante la sesión

## Tecnologías utilizadas

- Python 3
- PyQt5 (interfaz gráfica)
- Pandas (procesamiento de datos)
- ReportLab (generación de PDFs)
- PyInstaller (empaquetado ejecutable)

## Estructura del proyecto
