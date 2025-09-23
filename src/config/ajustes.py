"""
Este archivo contiene rutas y configuraciones generales para:
- Descarga de artículos (ACM, ScienceDirect)
- Procesamiento de BibTeX
- Agrupamiento jerárquico de abstracts
"""

import os
from pathlib import Path

# --- Configuración base ---
RUTA_BASE = Path("src").resolve()  # Usamos Path para mayor robustez
os.makedirs(RUTA_BASE / "datos", exist_ok=True)  # Asegura que la carpeta exista

# --- Configuración de descarga ---
RUTA_PERFIL_CHROME = os.path.join(
    os.environ["LOCALAPPDATA"],
    "Google",
    "Chrome",
    "User Data"
)

URL_ACM = 'https://dl.acm.org/action/doSearch?AllField="generative+artificial+intelligence"'
URL_SCIENCEDIRECT = 'https://www-sciencedirect-com.crai.referencistas.com/search?qs="generative+artificial+intelligence"&show=100'

# 🔐 Credenciales de Gmail para SCIENCEDIRECT BIBLIOTECA CRAI
EMAIL_GMAIL_SD = "jhoana.verav@uqvirtual.edu.co"
CONTRASENA_GMAIL_SD = "Gmail!099139"

# --- Rutas para archivos BibTeX ---
RUTA_DESCARGAS_ARTICULOS = RUTA_BASE / "datos" / "bib" / "crudos"
RUTA_ARCHIVO_UNIFICADO = RUTA_BASE / "datos" / "bib"
ARCHIVO_UNIFICADO = RUTA_ARCHIVO_UNIFICADO / "unificado.bib"

# --- Configuración de agrupamiento (nuevo) ---
RUTA_CLUSTERS = RUTA_BASE / "datos" / "clusters"
RUTA_ESTATICOS = RUTA_BASE / "aplicacion_web" / "estaticos"

os.makedirs(RUTA_CLUSTERS, exist_ok=True)  # Crea la carpeta si no existe

# Parámetros de clustering
UMBRAL_SIMILITUD = 0.6          # Para MinHash (ajustable)
METODO_LINKAGE = "complete"      # Para algoritmo matricial ("complete", "average", etc.)
STOPWORDS_PERSONALIZADAS = [     # Palabras a ignorar en abstracts
    "algorithm", "study", "based", "results", "approach"
]

# --- Validación de rutas ---
if not os.path.exists(RUTA_DESCARGAS_ARTICULOS):
    os.makedirs(RUTA_DESCARGAS_ARTICULOS)


RUTA_BD = RUTA_BASE / "datos" / "articulos.db"


CANTIDAD_LOGS = 5