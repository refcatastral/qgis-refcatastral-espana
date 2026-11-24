# QGIS Plugin: RefCatastral - Catastro y SIGPAC España 🇪🇸🗺️

[![QGIS 3](https://img.shields.io/badge/QGIS-3.0%2B-589632.svg?logo=qgis&logoColor=white&style=flat-square)](https://qgis.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Powered by RefCatastral.es](https://img.shields.io/badge/Powered%20by-RefCatastral.es-blue?style=flat-square)](https://refcatastral.es)

Complemento oficial de **[RefCatastral.es](https://refcatastral.es)** para **QGIS 3**, diseñado para topógrafos, ingenieros agrícolas, arquitectos, tasadores y profesionales de los Sistemas de Información Geográfica (SIG) en España.

Permite buscar inmuebles por Referencia Catastral (14 o 20 caracteres), geolocalizar parcelas, consultar recintos y cultivos de **SIGPAC**, y cargar capas WMS oficiales INSPIRE del Catastro y ortofotos del **PNOA (IGN)** con 1 clic.

---

## 🚀 Funcionalidades Principales

### 1. 🔍 Búsqueda de Referencias Catastrales (DGC)
* Introduce una Referencia Catastral urbana o rústica (ej. `9872023VH5797S0001WX` o `47900A00100023`).
* Obtiene en tiempo real la dirección postal oficial, superficie construida ($m^2$), año de construcción, uso principal y coordenadas WGS84.
* **Integración en QGIS:** Crea automáticamente una capa vectorial en memoria con la parcela y sus atributos, y centra el mapa sobre ella.
* **Acceso web:** Botón directo para abrir la ficha completa en [RefCatastral.es](https://refcatastral.es).

### 2. 🌾 Consultor de Parcelas Agrícolas SIGPAC (FEGA / MAPA)
* Consulta cualquier parcela rústica introduciendo Provincia, Municipio, Polígono y Parcela, o pegando directamente la Referencia Catastral rústica de 14 dígitos.
* Muestra una tabla detallada con todos los recintos, superficies (hectáreas y $m^2$), códigos de uso oficial (Olivar `OL`, Viñedo `VI`, Tierras Arables `TA`, Pastos `PR`, etc.), pendiente media (%) y altitud.
* Enlace con 1 clic al [Visor SIGPAC Interactivo de RefCatastral](https://refcatastral.es/visor-sigpac/).

### 3. 🗺️ Carga Rápida de Capas WMS Oficiales INSPIRE
Añade a tu proyecto QGIS las capas cartográficas oficiales de máxima resolución sin tener que configurar URLs manualmente:
* **Catastro:** Parcelas Catastrales INSPIRE (`CP.CadastralParcel`)
* **Catastro:** Edificios y Huellas de Construcción (`BU.Building`)
* **PNOA:** Ortofoto Aérea Actual de Máxima Resolución (IGN)
* **PNOA Histórico:** Vuelo Americano 1956 (IGN)

---

## 📦 Instalación

### Método 1: Desde el Repositorio Oficial de Plugins de QGIS (Recomendado)
1. Abre QGIS.
2. En el menú superior, ve a **Complementos** > **Administrar e instalar complementos...**
3. En la pestaña **Todos**, busca `RefCatastral`.
4. Haz clic en **Instalar complemento**.

### Método 2: Instalación manual desde archivo ZIP
1. Descarga el archivo `qgis-refcatastral-espana.zip`.
2. En QGIS, ve a **Complementos** > **Administrar e instalar complementos...** > pestaña **Instalar a partir de ZIP**.
3. Selecciona el archivo ZIP descargado y pulsa **Instalar complemento**.

---

## 🌐 Enlaces Oficiales

* **Portal Oficial:** [RefCatastral.es](https://refcatastral.es)
* **Visor SIGPAC:** [RefCatastral.es Visor SIGPAC](https://refcatastral.es/visor-sigpac/)
* **Comparador de Ortofotos Históricas PNOA:** [Comparador PNOA](https://refcatastral.es/comparador-ortofotos/)
* **Fuentes de Datos:**
  * Dirección General del Catastro (Ministerio de Hacienda)
  * Fondo Español de Garantía Agraria - FEGA (Ministerio de Agricultura, Pesca y Alimentación)
  * Instituto Geográfico Nacional - IGN (Ministerio de Transportes y Movilidad Sostenible)

---

## 📄 Licencia

Publicado bajo licencia de código abierto **MIT**. Desarrollado por [RefCatastral.es](https://refcatastral.es).
