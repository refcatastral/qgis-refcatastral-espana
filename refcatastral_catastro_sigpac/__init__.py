# -*- coding: utf-8 -*-
"""
RefCatastral - Catastro y SIGPAC España
Plugin oficial de RefCatastral.es para QGIS 3
"""


def classFactory(iface):
    """Carga y devuelve la instancia principal del plugin en QGIS."""
    from .refcatastral_plugin import RefCatastralPlugin
    return RefCatastralPlugin(iface)
