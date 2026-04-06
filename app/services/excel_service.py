import pandas as pd


def obtener_titulares_desde_excel(ruta_archivo):
    df = pd.read_excel(ruta_archivo)

    if "Titular" not in df.columns:
        raise ValueError("El archivo no contiene la columna 'Titular'.")

    titulares = (
        df["Titular"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    titulares_unicos = sorted(titulares.unique().tolist())

    return titulares_unicos