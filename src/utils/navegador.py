"""
Módulo de utilidad para configurar navegador Firefox.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from src.config.ajustes import RUTA_DESCARGAS_ARTICULOS
from src.utils.registro import registro

def configurar_navegador(modovisual="M"):
    """
    Configura y retorna el navegador Firefox con opciones personalizadas.
    
    Parámetros:
      - modovisual: "M" para mostrar el navegador, "O" para ocultarlo.
    """
    registro.registrar("Configurando navegador Firefox...", nivel="INFO")

    # 1. Configurar opciones y perfil
    opciones = FirefoxOptions()
    
    # Configuración de descargas
    opciones.set_preference("browser.download.folderList", 2)
    opciones.set_preference("browser.download.dir", str(RUTA_DESCARGAS_ARTICULOS))
    opciones.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-bibtex, text/plain")
    opciones.set_preference("pdfjs.disabled", True)
    opciones.set_preference("browser.download.manager.showWhenStarting", False)
    
    # Modo headless para mejor rendimiento
    if modovisual.upper() == "O":
        opciones.add_argument("--headless")

    try:
        # 2. Inicializar navegador con nueva sintaxis
        navegador = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=opciones
        )
        
        registro.registrar("✓ Navegador Firefox configurado", nivel="EXITO")
        return navegador
        
    except Exception as e:
        registro.registrar(f"ERROR Configuración: {str(e)}", nivel="ERROR")
        raise

def esperar_archivo_descargado(ruta_descargas):
    """Espera hasta detectar un archivo .bib válido"""
    registro.registrar("Buscando archivo .bib...", nivel="INFO")
    timeout = time.time() + 60*5
    
    while time.time() < timeout:
        archivos = [
            f for f in os.listdir(ruta_descargas)
            if f.endswith(".bib") and not f.startswith(".")
        ]
        
        if archivos:
            archivo = max(
                [os.path.join(ruta_descargas, f) for f in archivos],
                key=os.path.getctime
            )
            if os.path.getsize(archivo) > 1024:  # Mínimo 1KB
                registro.registrar(f"✓ Archivo válido: {archivo}", nivel="EXITO")
                return archivo
        time.sleep(2)
    
    raise TimeoutError("No se encontró archivo .bib válido en 1 minuto")