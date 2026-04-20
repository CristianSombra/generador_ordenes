import pandas as pd
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QListWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QGridLayout, QHeaderView, QMessageBox, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QDate
from app.services.excel_service import obtener_titulares_desde_excel
from app.services.data_service import obtener_datos_profesional_desde_excel, obtener_categoria_del_profesional, obtener_categorias_del_profesional, filtrar_datos_por_categoria
from app.utils.mes_utils import obtener_texto_correspondiente_a_mes
from app.utils.formato_utils import formatear_fecha, formatear_importe
from app.services.pdf_service import generar_pdf as generar_pdf_archivo
from app.utils.path_utils import obtener_ruta_recurso

class FechaTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        fecha_self = self.data(Qt.UserRole)
        fecha_other = other.data(Qt.UserRole)

        if isinstance(fecha_self, QDate) and isinstance(fecha_other, QDate):
            return fecha_self < fecha_other

        return super().__lt__(other)
    
def sanitizar_nombre_archivo(texto):
    for caracter in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        texto = texto.replace(caracter, '-')
    return texto.strip()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Generador de Órdenes de Pago")
        self.resize(1000, 700)

        layout = QVBoxLayout()

        logo_layout = QHBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap(obtener_ruta_recurso("app/assets/logo.png"))
        logo_label.setPixmap(
            pixmap.scaledToHeight(65, Qt.SmoothTransformation)
        )
        logo_label.setStyleSheet("background: transparent;")
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()

        layout.addLayout(logo_layout)

        titulo = QLabel("Generador de Órdenes de Pago")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 8px; margin-bottom: 8px;")
        layout.addWidget(titulo)

        periodo_layout = QHBoxLayout()

        label_desde = QLabel("Desde:")
        periodo_layout.addWidget(label_desde)

        self.input_desde = QLineEdit()
        self.input_desde.setPlaceholderText("09/2022")
        periodo_layout.addWidget(self.input_desde)

        label_hasta = QLabel("Hasta:")
        periodo_layout.addWidget(label_hasta)

        self.input_hasta = QLineEdit()
        self.input_hasta.setPlaceholderText("08/2023")
        periodo_layout.addWidget(self.input_hasta)

        layout.addLayout(periodo_layout)

        self.btn_importar = QPushButton("Importar base de datos")
        layout.addWidget(self.btn_importar)
        self.btn_importar.clicked.connect(self.importar_archivo)

        listas_layout = QGridLayout()

        self.label_a_procesar = QLabel("Profesionales a procesar")
        listas_layout.addWidget(self.label_a_procesar, 0, 0)

        self.label_procesados = QLabel("Profesionales procesados")
        listas_layout.addWidget(self.label_procesados, 0, 1)

        self.lista_titulares = QListWidget()
        self.lista_titulares.itemClicked.connect(self.cargar_datos_profesional)
        listas_layout.addWidget(self.lista_titulares, 1, 0)

        self.lista_procesados = QListWidget()
        listas_layout.addWidget(self.lista_procesados, 1, 1)

        layout.addLayout(listas_layout)

        self.btn_quitar = QPushButton("Quitar seleccionado")
        layout.addWidget(self.btn_quitar)
        self.btn_quitar.clicked.connect(self.quitar_profesional_seleccionado)

        self.tabla_datos = QTableWidget()
        self.tabla_datos.setColumnCount(4)
        self.tabla_datos.setHorizontalHeaderLabels([
            "Correspondiente a mes",
            "Operación de control",
            "Fecha de transferencia",
            "Importe"
        ])
        self.tabla_datos.setSortingEnabled(True)

        self.tabla_datos.setColumnWidth(0, 220)
        self.tabla_datos.setColumnWidth(1, 180)
        self.tabla_datos.setColumnWidth(2, 180)
        self.tabla_datos.setColumnWidth(3, 120)

        layout.addWidget(self.tabla_datos)

        self.label_categoria = QLabel("Categoría: ")
        layout.addWidget(self.label_categoria)

        self.combo_categoria = QComboBox()
        layout.addWidget(self.combo_categoria)

        self.combo_categoria.setEnabled(False)

        self.combo_categoria.currentTextChanged.connect(self.cambiar_categoria)

        self.input_descripcion = QLineEdit()
        self.input_descripcion.setPlaceholderText("Descripción")
        self.input_descripcion.setText("Prestaciones profesionales")
        layout.addWidget(self.input_descripcion)

        self.input_tipo_transaccion = QLineEdit()
        self.input_tipo_transaccion.setPlaceholderText("Tipo de transacción")
        self.input_tipo_transaccion.setText("TRANSFERENCIA")
        layout.addWidget(self.input_tipo_transaccion)

        self.input_fecha_procesado = QLineEdit()
        self.input_fecha_procesado.setPlaceholderText("Fecha Procesado")
        self.input_fecha_procesado.setText("16/04/2026")
        layout.addWidget(self.input_fecha_procesado)

        self.btn_ruta_guardado = QPushButton("Elegir ruta de guardado")
        layout.addWidget(self.btn_ruta_guardado)
        self.btn_ruta_guardado.clicked.connect(self.seleccionar_ruta_guardado)

        self.label_ruta_guardado = QLabel("Ruta de guardado: No seleccionada")
        layout.addWidget(self.label_ruta_guardado)

        self.btn_pdf = QPushButton("Generar PDF")
        self.btn_pdf.setEnabled(False)
        layout.addWidget(self.btn_pdf)

        self.btn_pdf.clicked.connect(self.generar_pdf)

        self.ruta_guardado = ""

        self.categorias_procesadas = {}

        self.setLayout(layout)

    def importar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar base de datos",
            "",
            "Archivos soportados (*.xlsx *.xls *.pdf *.txt)"
        )

        if archivo:
            print("Archivo seleccionado:", archivo)
            self.ruta_archivo = archivo

            if archivo.lower().endswith((".xlsx", ".xls")):
                titulares = obtener_titulares_desde_excel(archivo)
                self.lista_titulares.clear()
                self.lista_procesados.clear()
                self.tabla_datos.setRowCount(0)
                self.label_categoria.setText("Categoría: ")
                self.btn_pdf.setEnabled(False)

                for titular in titulares:
                    self.lista_titulares.addItem(titular)

    def cargar_datos_profesional(self, item):
        titular = item.text()

        self.df_profesional_actual = obtener_datos_profesional_desde_excel(self.ruta_archivo, titular)
        df_filtrado = self.df_profesional_actual
        
        categorias = obtener_categorias_del_profesional(df_filtrado)
        
        categorias_ya_procesadas = self.categorias_procesadas.get(titular, set())
        categorias_disponibles = [c for c in categorias if c not in categorias_ya_procesadas]
        
        self.combo_categoria.clear()
        self.combo_categoria.addItems(categorias_disponibles)
        self.combo_categoria.setEnabled(len(categorias_disponibles) > 0)
        
        self.categoria_actual = obtener_categoria_del_profesional(df_filtrado)
        self.label_categoria.setText(f"Categoría: {self.categoria_actual}")
        self.btn_pdf.setEnabled(True)
        self.tabla_datos.setSortingEnabled(False)
        self.tabla_datos.setRowCount(0)
        self.tabla_datos.setRowCount(len(df_filtrado))
    
        for fila, (_, registro) in enumerate(df_filtrado.iterrows()):
            observaciones = registro["Observaciones"] if not pd.isna(registro["Observaciones"]) else ""
            operacion = str(registro["Operación Nro."]) if not pd.isna(registro["Operación Nro."]) else ""
            fecha_hora = registro["Fecha y Hora"] if not pd.isna(registro["Fecha y Hora"]) else ""
            importe = registro["Importe"] if not pd.isna(registro["Importe"]) else ""
    
            correspondiente_mes = obtener_texto_correspondiente_a_mes(observaciones, fecha_hora)
            fecha_hora_texto = formatear_fecha(fecha_hora)
            importe_texto = formatear_importe(importe)
    
            item_mes = QTableWidgetItem(correspondiente_mes)
            item_operacion = QTableWidgetItem(operacion)
    
            item_fecha = FechaTableWidgetItem(fecha_hora_texto)
            if fecha_hora_texto:
                fecha_qt = QDate.fromString(fecha_hora_texto, "dd/MM/yyyy")
                item_fecha.setData(Qt.UserRole, fecha_qt)
    
            item_importe = QTableWidgetItem(importe_texto)
    
            self.tabla_datos.setItem(fila, 0, item_mes)
            self.tabla_datos.setItem(fila, 1, item_operacion)
            self.tabla_datos.setItem(fila, 2, item_fecha)
            self.tabla_datos.setItem(fila, 3, item_importe)
    
        self.tabla_datos.setSortingEnabled(True)
        self.cambiar_categoria(self.combo_categoria.currentText())

    def cambiar_categoria(self, categoria):
        if not categoria or not hasattr(self, "df_profesional_actual"):
            return

        df_filtrado = filtrar_datos_por_categoria(self.df_profesional_actual, categoria)

        self.categoria_actual = categoria
        self.label_categoria.setText(f"Categoría: {categoria}")
        self.btn_pdf.setEnabled(True)

        self.tabla_datos.setSortingEnabled(False)
        self.tabla_datos.setRowCount(0)
        self.tabla_datos.setRowCount(len(df_filtrado))

        for fila, (_, registro) in enumerate(df_filtrado.iterrows()):
            observaciones = registro["Observaciones"] if not pd.isna(registro["Observaciones"]) else ""
            operacion = str(registro["Operación Nro."]) if not pd.isna(registro["Operación Nro."]) else ""
            fecha_hora = registro["Fecha y Hora"] if not pd.isna(registro["Fecha y Hora"]) else ""
            importe = registro["Importe"] if not pd.isna(registro["Importe"]) else ""

            correspondiente_mes = obtener_texto_correspondiente_a_mes(observaciones, fecha_hora)
            fecha_hora_texto = formatear_fecha(fecha_hora)
            importe_texto = formatear_importe(importe)

            item_mes = QTableWidgetItem(correspondiente_mes)
            item_operacion = QTableWidgetItem(operacion)

            item_fecha = FechaTableWidgetItem(fecha_hora_texto)
            if fecha_hora_texto:
                fecha_qt = QDate.fromString(fecha_hora_texto, "dd/MM/yyyy")
                item_fecha.setData(Qt.UserRole, fecha_qt)

            item_importe = QTableWidgetItem(importe_texto)

            self.tabla_datos.setItem(fila, 0, item_mes)
            self.tabla_datos.setItem(fila, 1, item_operacion)
            self.tabla_datos.setItem(fila, 2, item_fecha)
            self.tabla_datos.setItem(fila, 3, item_importe)

        self.tabla_datos.setSortingEnabled(True)


    def quitar_profesional_seleccionado(self):
        item = self.lista_titulares.currentItem()
        if not item:
            QMessageBox.warning(self, "Sin selección", "Seleccioná un profesional de la lista 'A procesar'.")
            return
    
        fila_actual = self.lista_titulares.currentRow()
        nombre = item.text()
    
        self.lista_titulares.takeItem(fila_actual)
    
        self.tabla_datos.setRowCount(0)
        self.label_categoria.setText("Categoría: ")
        self.combo_categoria.clear()
        self.combo_categoria.setEnabled(False)
        self.btn_pdf.setEnabled(False)
    
        QMessageBox.information(self, "Profesional quitado", f"Se quitó a '{nombre}' de la lista 'A procesar'.")


    def seleccionar_ruta_guardado(self):
        carpeta = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de guardado"
        )

        if carpeta:
            self.ruta_guardado = carpeta
            self.label_ruta_guardado.setText(f"Ruta de guardado: {carpeta}")

    def generar_pdf(self):
        if not hasattr(self, "ruta_archivo"):
            print("Primero cargá un archivo")
            return

        item = self.lista_titulares.currentItem()
        if not item:
            print("Seleccioná un titular")
            return

        titular = item.text()
        desde = self.input_desde.text()
        hasta = self.input_hasta.text()
        categoria = getattr(self, "categoria_actual", "")
        descripcion = self.input_descripcion.text()
        tipo_transaccion = self.input_tipo_transaccion.text()
        fecha_procesado = self.input_fecha_procesado.text()

        datos = []

        for fila in range(self.tabla_datos.rowCount()):
            item_mes = self.tabla_datos.item(fila, 0)
            item_operacion = self.tabla_datos.item(fila, 1)
            item_fecha = self.tabla_datos.item(fila, 2)
            item_importe = self.tabla_datos.item(fila, 3)

            datos.append({
                "mes": item_mes.text() if item_mes else "",
                "operacion": item_operacion.text() if item_operacion else "",
                "fecha": item_fecha.text() if item_fecha else "",
                "importe": item_importe.text() if item_importe else "",
            })

        if not self.ruta_guardado:
            QMessageBox.warning(self, "Ruta no seleccionada", "Primero seleccioná una ruta de guardado.")
            return

        titular_archivo = titular.replace("/", "-").replace("\\", "-").strip()
        categoria_archivo = categoria.replace("/", "-").replace("\\", "-").strip()
        nombre_archivo = f"{titular_archivo} ({categoria_archivo}).pdf"
        ruta = os.path.join(self.ruta_guardado, nombre_archivo)

        generar_pdf_archivo(
            ruta,
            titular,
            desde,
            hasta,
            datos,
            categoria,
            descripcion,
            tipo_transaccion,
            fecha_procesado
        )

        print("PDF generado:", ruta)

        titular_categoria = f"{titular} ({categoria})"
        self.lista_procesados.addItem(titular_categoria)

        if titular not in self.categorias_procesadas:
            self.categorias_procesadas[titular] = set()

        self.categorias_procesadas[titular].add(categoria)

        todas_las_categorias = set(obtener_categorias_del_profesional(self.df_profesional_actual))
        categorias_ya_procesadas = self.categorias_procesadas[titular]

        if todas_las_categorias == categorias_ya_procesadas:
             fila_actual = self.lista_titulares.currentRow()
             if fila_actual >= 0:
                 self.lista_titulares.takeItem(fila_actual)      
             self.tabla_datos.setRowCount(0)
             self.combo_categoria.clear()
             self.combo_categoria.setEnabled(False)
             self.label_categoria.setText("Categoría: ")
             self.btn_pdf.setEnabled(False)
        else:
             categorias_disponibles = [c for c in todas_las_categorias if c not in categorias_ya_procesadas]

             self.combo_categoria.blockSignals(True)
             self.combo_categoria.clear()
             self.combo_categoria.addItems(categorias_disponibles)
             self.combo_categoria.blockSignals(False)

             if categorias_disponibles:
                 self.combo_categoria.setCurrentIndex(0)
                 self.cambiar_categoria(self.combo_categoria.currentText())

        QMessageBox.information(self, "PDF generado", "El PDF se generó correctamente.")