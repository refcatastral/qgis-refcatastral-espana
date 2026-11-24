# -*- coding: utf-8 -*-
"""
Clase principal del Plugin RefCatastral para QGIS 3
"""

import os
try:
    from qgis.PyQt.QtCore import QUrl
    from qgis.PyQt.QtGui import QIcon, QDesktopServices
    from qgis.PyQt.QtWidgets import QAction, QMenu
    from .dialogs import BuscarCatastroDialog, ConsultarSigpacDialog, CapasWmsDialog
except ImportError:
    pass


class RefCatastralPlugin:
    """Complemento oficial de RefCatastral.es para QGIS."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = None
        self.toolbar = None

    def initGui(self):
        """Inicializa la interfaz gráfica: crea menú y barra de herramientas."""
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        # Barra de herramientas RefCatastral
        self.toolbar = self.iface.addToolBar("RefCatastral")
        self.toolbar.setObjectName("RefCatastralToolBar")

        # Menú superior
        self.menu = QMenu("&RefCatastral España", self.iface.mainWindow())
        self.iface.mainWindow().menuBar().addMenu(self.menu)

        # Acción 1: Buscar en Catastro
        action_catastro = QAction(icon, "🔍 Buscar Referencia Catastral", self.iface.mainWindow())
        action_catastro.setStatusTip("Consulta datos físicos y localización de parcelas catastrales")
        action_catastro.triggered.connect(self.abrir_buscar_catastro)
        self.toolbar.addAction(action_catastro)
        self.menu.addAction(action_catastro)
        self.actions.append(action_catastro)

        # Acción 2: Consultar SIGPAC
        action_sigpac = QAction(icon, "🌾 Consultar Parcela Agrícola SIGPAC", self.iface.mainWindow())
        action_sigpac.setStatusTip("Consulta recintos, cultivos agrícolas y pendientes en SIGPAC")
        action_sigpac.triggered.connect(self.abrir_consultar_sigpac)
        self.toolbar.addAction(action_sigpac)
        self.menu.addAction(action_sigpac)
        self.actions.append(action_sigpac)

        # Acción 3: Cargar Capas WMS
        action_wms = QAction(icon, "🗺️ Cargar Capas WMS (Catastro y PNOA)", self.iface.mainWindow())
        action_wms.setStatusTip("Añade capas WMS INSPIRE oficiales de Catastro y ortofotos del PNOA")
        action_wms.triggered.connect(self.abrir_cargar_wms)
        self.toolbar.addAction(action_wms)
        self.menu.addAction(action_wms)
        self.actions.append(action_wms)

        self.menu.addSeparator()

        # Acción 4: Abrir RefCatastral.es
        action_web = QAction(icon, "🌐 Abrir RefCatastral.es en Navegador", self.iface.mainWindow())
        action_web.setStatusTip("Abre el portal oficial de RefCatastral.es")
        action_web.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://refcatastral.es")))
        self.menu.addAction(action_web)
        self.actions.append(action_web)

    def unload(self):
        """Limpia los elementos creados al desactivar o desinstalar el plugin."""
        for action in self.actions:
            self.iface.removePluginMenu("&RefCatastral España", action)
            self.iface.removeToolBarIcon(action)

        if self.toolbar:
            del self.toolbar

    def abrir_buscar_catastro(self):
        dlg = BuscarCatastroDialog(self.iface)
        dlg.exec_()

    def abrir_consultar_sigpac(self):
        dlg = ConsultarSigpacDialog(self.iface)
        dlg.exec_()

    def abrir_cargar_wms(self):
        dlg = CapasWmsDialog(self.iface)
        dlg.exec_()
