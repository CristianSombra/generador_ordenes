from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os
from app.utils.path_utils import obtener_ruta_recurso


def generar_pdf(ruta_salida, titular, desde, hasta, datos, categoria, descripcion, tipo_transaccion, fecha_procesado):
    c = canvas.Canvas(ruta_salida, pagesize=A4)
    width, height = A4

    margen = 0.8 * cm
    fila_alto = 0.6 * cm
    tabla_ancho = width - 4 * cm

    col1 = 2 * cm
    col2 = 7 * cm
    col3 = 12 * cm
    col4 = 17 * cm

    ancho_col1 = col2 - col1
    ancho_col2 = col3 - col2
    ancho_col3 = col4 - col3
    ancho_col4 = (2 * cm + tabla_ancho) - col4

    ruta_logo = obtener_ruta_recurso("app/assets/logo.png")
    ruta_firma_yanina = obtener_ruta_recurso("app/assets/firma_yanina.png")
    ruta_firma_cristian = obtener_ruta_recurso("app/assets/firma_cristian.png")

    def dibujar_encabezado():
        c.setLineWidth(0.8)
        c.rect(margen, margen, width - (2 * margen), height - (2 * margen))

        if os.path.exists(ruta_logo):
            c.drawImage(
                ruta_logo,
                2 * cm,
                height - 4.5 * cm,
                width=5 * cm,
                height=3.8 * cm,
                preserveAspectRatio=True,
                mask='auto'
            )

        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width / 2, height - 5.1 * cm, f"ORDEN DE PAGO (PERIODO {desde} - {hasta})")

        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, height - 6.4 * cm, f"CONCEPTO Y/O PROVEEDOR: {titular}")

    def dibujar_encabezado_tabla(start_y):
        c.setLineWidth(0.6)
        c.rect(2 * cm, start_y - fila_alto, tabla_ancho, fila_alto)

        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(col1 + ancho_col1 / 2, start_y - 0.4 * cm, "CORRESPONDIENTE A MES")
        c.drawCentredString(col2 + ancho_col2 / 2, start_y - 0.4 * cm, "OPERACIÓN")
        c.drawCentredString(col3 + ancho_col3 / 2, start_y - 0.4 * cm, "FECHA DE TRANSFERENCIA")
        c.drawCentredString(col4 + ancho_col4 / 2, start_y - 0.4 * cm, "IMPORTE")

        c.line(col2, start_y, col2, start_y - fila_alto)
        c.line(col3, start_y, col3, start_y - fila_alto)
        c.line(col4, start_y, col4, start_y - fila_alto)

    def dibujar_firmas():
        y_firma = 3 * cm

        if os.path.exists(ruta_firma_yanina):
            c.drawImage(
                ruta_firma_yanina,
                2.3 * cm,
                y_firma - 0.10 * cm,
                width=6.2 * cm,
                height=3.0 * cm,
                preserveAspectRatio=True,
                mask='auto'
            )

        if os.path.exists(ruta_firma_cristian):
            c.drawImage(
                ruta_firma_cristian,
                10.5 * cm,
                y_firma - 0.25 * cm,
                width=8.4 * cm,
                height=3.8 * cm,
                preserveAspectRatio=True,
                mask='auto'
            )

        c.line(4.0 * cm, y_firma, 8.0 * cm, y_firma)
        c.drawCentredString(6.0 * cm, y_firma - 0.7 * cm, "PREPARÓ")

        c.line(13 * cm, y_firma, 17 * cm, y_firma)
        c.drawCentredString(15 * cm, y_firma - 0.7 * cm, "CONTROLÓ")

    dibujar_encabezado()

    start_y = height - 8 * cm
    dibujar_encabezado_tabla(start_y)

    y = start_y - fila_alto
    total = 0

    c.setFont("Helvetica", 8)

    espacio_reservado_final = 10 * cm

    for fila in datos:
        y_siguiente = y - fila_alto

        if y_siguiente < espacio_reservado_final:
            c.showPage()
            dibujar_encabezado()
            dibujar_encabezado_tabla(start_y)
            c.setFont("Helvetica", 8)
            y = start_y - fila_alto
            y_siguiente = y - fila_alto

        c.rect(2 * cm, y_siguiente, tabla_ancho, fila_alto)
        c.line(col2, y, col2, y_siguiente)
        c.line(col3, y, col3, y_siguiente)
        c.line(col4, y, col4, y_siguiente)

        c.drawString(col1 + 0.2 * cm, y - 0.5 * cm, str(fila["mes"]))
        c.drawCentredString(col2 + 1.8 * cm, y - 0.4 * cm, str(fila["operacion"]))
        c.drawCentredString(col3 + 1.8 * cm, y - 0.4 * cm, str(fila["fecha"]))
        c.drawRightString(width - 2.2 * cm, y - 0.4 * cm, str(fila["importe"]))

        try:
            valor = float(str(fila["importe"]).replace(".", "").replace(",", "."))
            total += valor
        except:
            pass

        y = y_siguiente

    espacio_total_final = 8 * cm
    if y - espacio_total_final < 3 * cm:
        c.showPage()
        dibujar_encabezado()
        c.setFont("Helvetica", 9)
        y = height - 8 * cm

    total_texto = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(width - 2 * cm, y - 0.6 * cm, f"TOTAL: {total_texto}")

    y_obs = y - 1.8 * cm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2 * cm, y_obs, "OBSERVACIONES:")

    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, y_obs - 0.7 * cm, f"Categoría: {categoria}")
    c.drawString(2 * cm, y_obs - 1.3 * cm, f"Descripción: {descripcion}")
    c.drawString(2 * cm, y_obs - 1.9 * cm, f"Tipo de transacción: {tipo_transaccion}")
    c.drawString(2 * cm, y_obs - 3.0 * cm, f"Fecha Procesado: {fecha_procesado}")

    dibujar_firmas()

    c.save()