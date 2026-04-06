from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os


def generar_pdf(ruta_salida, titular, periodo_desde, periodo_hasta, datos):
    doc = SimpleDocTemplate(ruta_salida, pagesize=A4)
    styles = getSampleStyleSheet()

    elementos = []

    # --- LOGO ---
    ruta_logo = "app/assets/logo.png"
    if os.path.exists(ruta_logo):
        logo = Image(ruta_logo, width=120, height=60)
        elementos.append(logo)

    # --- TITULO ---
    titulo = f"ORDEN DE PAGO (PERIODO {periodo_desde} - {periodo_hasta})"
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph(titulo, styles["Title"]))

    # --- PROVEEDOR ---
    elementos.append(Spacer(1, 20))
    proveedor = f"<b>CONCEPTO Y/O PROVEEDOR:</b> {titular}"
    elementos.append(Paragraph(proveedor, styles["Normal"]))

    elementos.append(Spacer(1, 20))

    # --- TABLA ---
    tabla_data = [
        ["MES", "OPERACIÓN", "FECHA", "IMPORTE"]
    ]

    for fila in datos:
        tabla_data.append([
            fila["mes"],
            fila["operacion"],
            fila["fecha"],
            fila["importe"]
        ])

    tabla = Table(tabla_data)

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)