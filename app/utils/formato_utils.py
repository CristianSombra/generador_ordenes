import pandas as pd


def formatear_fecha(fecha_valor):
    if pd.isna(fecha_valor):
        return ""

    fecha = pd.to_datetime(fecha_valor, errors="coerce")

    if pd.isna(fecha):
        return ""

    return fecha.strftime("%d/%m/%Y")


def formatear_importe(valor):
    if pd.isna(valor):
        return ""

    try:
        numero = float(valor)
        texto = f"{numero:,.2f}"
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return texto
    except (ValueError, TypeError):
        return str(valor)