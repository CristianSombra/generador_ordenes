import pandas as pd


def obtener_datos_profesional_desde_excel(ruta_archivo, titular):
    df = pd.read_excel(ruta_archivo)

    columnas_requeridas = ["Titular", "Observaciones", "Operación Nro.", "Fecha y Hora", "Importe", "Categoría"]

    for columna in columnas_requeridas:
        if columna not in df.columns:
            raise ValueError(f"El archivo no contiene la columna '{columna}'.")

    df["Titular"] = df["Titular"].astype(str).str.strip()

    df_filtrado = df[df["Titular"] == titular].copy()

    return df_filtrado


def obtener_categoria_del_profesional(df_filtrado):
    if df_filtrado.empty:
        return ""

    categorias = (
        df_filtrado["Categoría"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    if not categorias:
        return ""

    return categorias[0]


def obtener_categorias_del_profesional(df_filtrado):
    if df_filtrado.empty:
        return []

    categorias = (
        df_filtrado["Categoría"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return categorias


def filtrar_datos_por_categoria(df_filtrado, categoria):
    if df_filtrado.empty:
        return df_filtrado.copy()

    return df_filtrado[
        df_filtrado["Categoría"]
        .fillna("")
        .astype(str)
        .str.strip() == categoria.strip()
    ].copy()