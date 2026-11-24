# -*- coding: utf-8 -*-
"""
Diálogos de interfaz gráfica para RefCatastral QGIS Plugin
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import gzip
import io

try:
    from qgis.PyQt.QtCore import Qt, QUrl
    from qgis.PyQt.QtGui import QDesktopServices
    from qgis.PyQt.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
        QMessageBox, QSpinBox, QGroupBox, QFormLayout, QTextEdit
    )
    from qgis.core import (
        QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
        QgsPointXY, QgsField, QgsRasterLayer, QgsCoordinateReferenceSystem
    )
    from qgis.PyQt.QtCore import QVariant
except ImportError:
    # Permite ejecutar scripts de prueba fuera del entorno QGIS
    pass

USOS_SIGPAC = {
    "TA": "Tierras Arables / Cultivos Herbáceos",
    "TH": "Huerta / Cultivos Hortícolas",
    "VF": "Viñedo en Regadío",
    "VI": "Viñedo en Secano",
    "OF": "Olivar en Regadío",
    "OL": "Olivar en Secano",
    "FY": "Frutales",
    "FF": "Frutales en Regadío",
    "CI": "Cítricos",
    "CF": "Cítricos en Regadío",
    "FS": "Frutos Secos",
    "PR": "Pastizal / Pastos Permanentes",
    "PS": "Pastizal con Arbolado / Dehesa",
    "PA": "Pastos Arbustivos",
    "MT": "Matorral",
    "FO": "Forestal / Masa Arbolada",
    "AG": "Aguas Corrientes y Embalses",
    "ED": "Edificación / Construcción",
    "ZU": "Zona Urbana",
    "IM": "Improductivo"
}


class BuscarCatastroDialog(QDialog):
    """Diálogo para buscar inmuebles o parcelas por Referencia Catastral."""

    def __init__(self, iface, parent=None):
        super(BuscarCatastroDialog, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("RefCatastral - Buscar Referencia Catastral")
        self.resize(550, 420)
        self.resultado_actual = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Caja de búsqueda
        group_search = QGroupBox("Consulta de Referencia Catastral (14 o 20 caracteres)")
        h_layout = QHBoxLayout()
        self.txt_rc = QLineEdit()
        self.txt_rc.setPlaceholderText("Ej: 9872023VH5797S0001WX o 47900A00100023")
        btn_buscar = QPushButton("🔍 Consultar")
        btn_buscar.clicked.connect(self.buscar_rc)
        self.txt_rc.returnPressed.connect(self.buscar_rc)
        h_layout.addWidget(self.txt_rc)
        h_layout.addWidget(btn_buscar)
        group_search.setLayout(h_layout)
        layout.addWidget(group_search)

        # Ficha de resultados
        self.group_result = QGroupBox("Datos Oficiales de la Parcela / Inmueble")
        form_layout = QFormLayout()
        self.lbl_direccion = QLabel("-")
        self.lbl_municipio = QLabel("-")
        self.lbl_superficie = QLabel("-")
        self.lbl_anyo = QLabel("-")
        self.lbl_uso = QLabel("-")
        self.lbl_coords = QLabel("-")

        form_layout.addRow("📍 Domicilio Oficial:", self.lbl_direccion)
        form_layout.addRow("🏛️ Municipio / Prov.:", self.lbl_municipio)
        form_layout.addRow("📐 Superficie Construida:", self.lbl_superficie)
        form_layout.addRow("📅 Año Construcción:", self.lbl_anyo)
        form_layout.addRow("🏷️ Uso Principal:", self.lbl_uso)
        form_layout.addRow("🌐 Coordenadas GPS:", self.lbl_coords)

        self.group_result.setLayout(form_layout)
        layout.addWidget(self.group_result)

        # Botones de acción
        h_actions = QHBoxLayout()
        self.btn_mapa = QPushButton("📍 Centrar Mapa en QGIS")
        self.btn_mapa.setEnabled(False)
        self.btn_mapa.clicked.connect(self.centrar_en_qgis)

        self.btn_web = QPushButton("🌐 Abrir Ficha en RefCatastral.es")
        self.btn_web.clicked.connect(self.abrir_web)

        h_actions.addWidget(self.btn_mapa)
        h_actions.addWidget(self.btn_web)
        layout.addLayout(h_actions)

    def buscar_rc(self):
        rc = self.txt_rc.text().strip().upper()
        if len(rc) < 14:
            QMessageBox.warning(self, "Aviso", "La referencia catastral debe tener al menos 14 caracteres.")
            return

        try:
            # 1. Consultar datos físicos en OVC
            url_datos = f"https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC?Provincia=&Municipio=&RC={urllib.parse.quote(rc)}"
            req = urllib.request.Request(url_datos, headers={"User-Agent": "RefCatastral-QGIS/1.0 (+https://refcatastral.es)"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_str = resp.read().decode("utf-8")

            # 2. Consultar coordenadas WGS84
            prov_code = rc[:2]
            url_coor = f"https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_CPMRC?Provincia={prov_code}&Municipio=&RC={urllib.parse.quote(rc)}&SRS=EPSG:4326"
            req_c = urllib.request.Request(url_coor, headers={"User-Agent": "RefCatastral-QGIS/1.0 (+https://refcatastral.es)"})
            lat, lon = None, None
            try:
                with urllib.request.urlopen(req_c, timeout=10) as resp_c:
                    xml_c = resp_c.read().decode("utf-8")
                    root_c = ET.fromstring(xml_c)
                    lat_el = root_c.find(".//{http://www.catastro.meh.es/}coord/{http://www.catastro.meh.es/}geo/{http://www.catastro.meh.es/}ycen")
                    lon_el = root_c.find(".//{http://www.catastro.meh.es/}coord/{http://www.catastro.meh.es/}geo/{http://www.catastro.meh.es/}xcen")
                    if lat_el is not None and lon_el is not None:
                        lat = float(lat_el.text)
                        lon = float(lon_el.text)
            except Exception:
                pass

            root = ET.fromstring(xml_str)
            ldt_el = root.find(".//{http://www.catastro.meh.es/}ldt")
            np_el = root.find(".//{http://www.catastro.meh.es/}np")
            nm_el = root.find(".//{http://www.catastro.meh.es/}nm")
            uso_el = root.find(".//{http://www.catastro.meh.es/}luso")
            sup_el = root.find(".//{http://www.catastro.meh.es/}sfc")
            ant_el = root.find(".//{http://www.catastro.meh.es/}ant")

            direccion = ldt_el.text if ldt_el is not None else "Dirección no disponible"
            municipio = f"{nm_el.text if nm_el is not None else ''} ({np_el.text if np_el is not None else ''})"
            superficie = f"{sup_el.text} m²" if sup_el is not None else "No consta"
            anyo = ant_el.text if ant_el is not None else "No consta"
            uso = uso_el.text if uso_el is not None else "No especificado"
            coords_str = f"{lat:.6f}, {lon:.6f}" if lat and lon else "Coordenadas no disponibles"

            self.lbl_direccion.setText(direccion)
            self.lbl_municipio.setText(municipio)
            self.lbl_superficie.setText(superficie)
            self.lbl_anyo.setText(anyo)
            self.lbl_uso.setText(uso)
            self.lbl_coords.setText(coords_str)

            self.resultado_actual = {
                "rc": rc,
                "direccion": direccion,
                "municipio": municipio,
                "superficie": superficie,
                "anyo": anyo,
                "uso": uso,
                "lat": lat,
                "lon": lon
            }

            self.btn_mapa.setEnabled(lat is not None and lon is not None)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo consultar el Catastro:\n{str(e)}")

    def centrar_en_qgis(self):
        if not self.resultado_actual or not self.resultado_actual["lat"]:
            return

        lat = self.resultado_actual["lat"]
        lon = self.resultado_actual["lon"]
        rc = self.resultado_actual["rc"]
        dir_text = self.resultado_actual["direccion"]

        # Crear capa de memoria en QGIS
        layer = QgsVectorLayer("Point?crs=epsg:4326", f"Parcela {rc}", "memory")
        pr = layer.dataProvider()
        pr.addAttributes([
            QgsField("referencia", QVariant.String),
            QgsField("direccion", QVariant.String),
            QgsField("superficie", QVariant.String),
            QgsField("uso", QVariant.String),
        ])
        layer.updateFields()

        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        feat.setAttributes([rc, dir_text, self.resultado_actual["superficie"], self.resultado_actual["uso"]])
        pr.addFeature(feat)
        layer.updateExtents()

        QgsProject.instance().addMapLayer(layer)
        self.iface.mapCanvas().setCenter(QgsPointXY(lon, lat))
        self.iface.mapCanvas().refresh()
        QMessageBox.information(self, "QGIS", f"Parcela {rc} añadida como capa en QGIS.")

    def abrir_web(self):
        rc = self.txt_rc.text().strip().upper()
        if rc:
            url = f"https://refcatastral.es/visor-catastro/?ref={rc}"
        else:
            url = "https://refcatastral.es"
        QDesktopServices.openUrl(QUrl(url))


class ConsultarSigpacDialog(QDialog):
    """Diálogo para consultar parcelas y recintos agrícolas de SIGPAC."""

    def __init__(self, iface, parent=None):
        super(ConsultarSigpacDialog, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("RefCatastral - Consultar Parcela Agrícola SIGPAC (FEGA)")
        self.resize(700, 480)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Entrada rápida por referencia rústica
        group_ref = QGroupBox("Opción A: Pegar Referencia Catastral Rústica (14 caracteres)")
        h_ref = QHBoxLayout()
        self.txt_rustica = QLineEdit()
        self.txt_rustica.setPlaceholderText("Ej: 47900A00100023")
        btn_desglosar = QPushButton("⚡ Desglosar")
        btn_desglosar.clicked.connect(self.desglosar_rustica)
        h_ref.addWidget(self.txt_rustica)
        h_ref.addWidget(btn_desglosar)
        group_ref.setLayout(h_ref)
        layout.addWidget(group_ref)

        # Formulario de parámetros SIGPAC
        group_form = QGroupBox("Opción B: Coordenadas Agrarias SIGPAC")
        form = QFormLayout()

        self.sp_prov = QSpinBox()
        self.sp_prov.setRange(1, 52)
        self.sp_prov.setValue(47)

        self.sp_mun = QSpinBox()
        self.sp_mun.setRange(1, 999)
        self.sp_mun.setValue(900)

        self.sp_pol = QSpinBox()
        self.sp_pol.setRange(1, 999)
        self.sp_pol.setValue(1)

        self.sp_parc = QSpinBox()
        self.sp_parc.setRange(1, 99999)
        self.sp_parc.setValue(23)

        form.addRow("Provincia (Código INE):", self.sp_prov)
        form.addRow("Municipio (Código INE):", self.sp_mun)
        form.addRow("Polígono:", self.sp_pol)
        form.addRow("Parcela:", self.sp_parc)

        btn_consultar = QPushButton("🌾 Consultar Recintos y Usos SIGPAC")
        btn_consultar.clicked.connect(self.consultar_sigpac)
        form.addRow(btn_consultar)

        group_form.setLayout(form)
        layout.addWidget(group_form)

        # Tabla de recintos
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Recinto", "Superficie (ha)", "Superficie (m²)", "Uso", "Pendiente (%)", "Altitud (m)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Botón visor
        h_bottom = QHBoxLayout()
        btn_visor = QPushButton("🗺️ Abrir en Visor SIGPAC de RefCatastral.es")
        btn_visor.clicked.connect(self.abrir_visor_sigpac)
        h_bottom.addWidget(btn_visor)
        layout.addLayout(h_bottom)

    def desglosar_rustica(self):
        rc = self.txt_rustica.text().strip().upper().replace(" ", "")
        if len(rc) >= 14:
            try:
                pr = int(rc[0:2])
                mu = int(rc[2:5])
                po = int(rc[6:9])
                pa = int(rc[9:14])
                self.sp_prov.setValue(pr)
                self.sp_mun.setValue(mu)
                self.sp_pol.setValue(po)
                self.sp_parc.setValue(pa)
                self.consultar_sigpac()
            except ValueError:
                QMessageBox.warning(self, "Aviso", "Formato de referencia rústica no válido.")

    def consultar_sigpac(self):
        pr = self.sp_prov.value()
        mu = self.sp_mun.value()
        po = self.sp_pol.value()
        pa = self.sp_parc.value()

        url = f"https://sigpac-hubcloud.es/servicioconsultassigpac/query/recinfoparc/{pr}/{mu}/0/0/{po}/{pa}.json"
        req = urllib.request.Request(url, headers={"User-Agent": "RefCatastral-QGIS/1.0 (+https://refcatastral.es)"})

        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw_bytes = resp.read()
                # Descompresión GZIP si viene comprimido
                if len(raw_bytes) >= 2 and raw_bytes[0] == 0x1f and raw_bytes[1] == 0x8b:
                    raw_bytes = gzip.decompress(raw_bytes)
                data = json.loads(raw_bytes.decode("utf-8"))

            if not isinstance(data, list) or len(data) == 0:
                QMessageBox.information(self, "SIGPAC", "No se encontraron recintos para esta parcela.")
                self.table.setRowCount(0)
                return

            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                recinto_num = str(r.get("recinto", ""))
                sup_ha = float(r.get("superficie", 0))
                sup_m2 = int(sup_ha * 10000)
                uso_cod = (r.get("uso_sigpac") or "").upper()
                uso_desc = USOS_SIGPAC.get(uso_cod, uso_cod)
                pendiente = str(r.get("pendiente_media", "-"))
                altitud = str(r.get("altitud", "-"))

                self.table.setItem(i, 0, QTableWidgetItem(recinto_num))
                self.table.setItem(i, 1, QTableWidgetItem(f"{sup_ha:.4f}"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{sup_m2:,}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{uso_cod} - {uso_desc}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"{pendiente}%"))
                self.table.setItem(i, 5, QTableWidgetItem(f"{altitud} m"))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error conectando con SIGPAC:\n{str(e)}")

    def abrir_visor_sigpac(self):
        QDesktopServices.openUrl(QUrl("https://refcatastral.es/visor-sigpac/"))


class CapasWmsDialog(QDialog):
    """Diálogo para cargar capas WMS oficiales de Catastro y PNOA con 1 clic."""

    CAPAS_DISPONIBLES = [
        {
            "nombre": "Catastro: Parcelas Catastrales (INSPIRE)",
            "url": "https://ovc.catastro.meh.es/Cartografia/WMS/BuscarFirmas.aspx",
            "layer": "CP.CadastralParcel",
            "formato": "image/png"
        },
        {
            "nombre": "Catastro: Edificios y Huellas de Construcción",
            "url": "https://ovc.catastro.meh.es/Cartografia/WMS/BuscarFirmas.aspx",
            "layer": "BU.Building",
            "formato": "image/png"
        },
        {
            "nombre": "PNOA: Ortofoto Aérea Actual (IGN)",
            "url": "https://www.ign.es/wms-inspire/pnoa-ma",
            "layer": "OI.OrthoimageCoverage",
            "formato": "image/png"
        },
        {
            "nombre": "PNOA Histórico: Vuelo Americano 1956",
            "url": "https://www.ign.es/wms/pnoa-historico",
            "layer": "AMS_1956-1957",
            "formato": "image/png"
        }
    ]

    def __init__(self, iface, parent=None):
        super(CapasWmsDialog, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("RefCatastral - Cargar Capas WMS Oficiales de España")
        self.resize(520, 360)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        lbl_desc = QLabel(
            "Selecciona las capas oficiales de cartografía que deseas añadir a tu proyecto QGIS:\n"
            "(Conexión directa OGC WMS de la Dirección General del Catastro y del IGN)"
        )
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        from qgis.PyQt.QtWidgets import QCheckBox
        self.checkboxes = []

        for capa in self.CAPAS_DISPONIBLES:
            cb = QCheckBox(capa["nombre"])
            cb.setChecked(True)
            self.checkboxes.append((cb, capa))
            layout.addWidget(cb)

        btn_cargar = QPushButton("📥 Cargar Capas Seleccionadas en QGIS")
        btn_cargar.clicked.connect(self.cargar_capas)
        layout.addWidget(btn_cargar)

        btn_visor = QPushButton("🌐 Explorar en Comparador de Ortofotos de RefCatastral")
        btn_visor.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://refcatastral.es/comparador-ortofotos/")))
        layout.addWidget(btn_visor)

    def cargar_capas(self):
        cargadas = 0
        for cb, info in self.checkboxes:
            if cb.isChecked():
                uri = f"url={info['url']}&layers={info['layer']}&format={info['formato']}&crs=EPSG:4326"
                layer = QgsRasterLayer(uri, info["nombre"], "wms")
                if layer.isValid():
                    QgsProject.instance().addMapLayer(layer)
                    cargadas += 1
                else:
                    QMessageBox.warning(self, "Aviso", f"No se pudo cargar la capa: {info['nombre']}")

        if cargadas > 0:
            QMessageBox.information(self, "QGIS", f"Se han cargado {cargadas} capa(s) en el proyecto.")
            self.accept()
