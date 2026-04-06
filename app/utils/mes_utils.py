import re
import pandas as pd


MESES_MAP = {
    "ENE": "Enero",
    "ENER": "Enero",
    "FEB": "Febrero",
    "MAR": "Marzo",
    "ABR": "Abril",
    "MAY": "Mayo",
    "JUN": "Junio",
    "JUL": "Julio",
    "AGOS": "Agosto",
    "SEP": "Septiembre",
    "SEPT": "Septiembre",
    "OCT": "Octubre",
    "NOV": "Noviembre",
    "DIC": "Diciembre",
}

ORDEN_MESES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


def extraer_meses_desde_observaciones(observacion):
    if pd.isna(observacion):
        return []

    texto = str(observacion).upper().strip()

    meses_detectados = []

    for clave, nombre_mes in MESES_MAP.items():
        if clave in texto and nombre_mes not in meses_detectados:
            meses_detectados.append(nombre_mes)

    meses_ordenados = [mes for mes in ORDEN_MESES if mes in meses_detectados]

    return meses_ordenados


def obtener_mes_desde_fecha(fecha_valor):
    if pd.isna(fecha_valor):
        return ""

    fecha = pd.to_datetime(fecha_valor, errors="coerce")

    if pd.isna(fecha):
        return ""

    return ORDEN_MESES[fecha.month - 1]


def obtener_texto_correspondiente_a_mes(observacion, fecha_valor):
    meses = extraer_meses_desde_observaciones(observacion)

    if meses:
        return " - ".join(meses)

    return obtener_mes_desde_fecha(fecha_valor)