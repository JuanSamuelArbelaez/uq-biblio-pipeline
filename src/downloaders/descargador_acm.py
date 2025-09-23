import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 📁 Rutas personalizadas
from src.config.ajustes import RUTA_DESCARGAS_ARTICULOS, URL_ACM
from src.utils.registro import registro
from src.utils.navegador import configurar_navegador, esperar_archivo_descargado


# 🆔 Selector CSS para el botón final de descarga
SELECTOR_BOTON_FINAL = "#exportDownloadReady > div.searchCiteExport-popup__body.clearfix > a"

def esperar_boton_download_habilitado(driver):
    """
    Espera hasta que aparezca el contenedor #exportDownloadReady y hace clic en el botón "Download now!".
    No se validan atributos ya que el botón es clickeable apenas aparece el contenedor.
    """
    while True:
        try:
            boton = driver.find_element(By.CSS_SELECTOR, SELECTOR_BOTON_FINAL)
            clase = boton.get_attribute("class")
            href = boton.get_attribute("href")
            texto = boton.text.strip().lower()


            # Evalúa el estado del botón para hacer clic y descargar la base de datos
            if href and "disabled" not in clase.lower() and "download now" in texto:
                driver.execute_script("arguments[0].scrollIntoView(true);", boton)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", boton)
                registro.registrar("Botón 'Download now!' presionado. Iniciando descarga...", nivel="EXITO")
                break  # Salimos del bucle tras el clic exitoso

        except Exception as e:
            registro.registrar(f"Aún no disponible o no interactuable ({e.__class__.__name__})", nivel="ERROR")
        time.sleep(1)

def descargar_articulos_acm():
    """
    Automatiza el proceso de descarga de artículos desde ACM Digital Library.
    Realiza selección de todos los artículos, exportación en formato BibTeX y validación de descarga.
    """
    registro.registrar("Iniciando descarga de artículos desde ACM...", nivel="INFO")
    os.makedirs(RUTA_DESCARGAS_ARTICULOS, exist_ok=True)

    navegador = configurar_navegador("O")
    navegador.get(URL_ACM)
    time.sleep(2)  # Espera inicial para cargar la página completamente

    try:# Espera a que el botón de cookies esté disponible para hacer clic
       
        wait = WebDriverWait(navegador, 5)

        
        cookie_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")))

        # Haz clic en el botón
        cookie_button.click()

        wait = WebDriverWait(navegador, 5)
        
        # Seleccionar todos los artículos usando el checkbox general
        checkbox_todos = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[type='checkbox'][name='markall']")))
        navegador.execute_script("arguments[0].click();", checkbox_todos)
        registro.registrar("Todos los artículos seleccionados.", nivel="EXITO")

        # Clic en botón "Export Citations"
        boton_exportar = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[title='Export Citations']")))
        navegador.execute_script("arguments[0].click();", boton_exportar)
        registro.registrar("Menú de exportación abierto.", nivel="INFO")
        time.sleep(1)

        # Clic en pestaña "All Results"
        pestaña_all_results = wait.until(EC.element_to_be_clickable((By.ID, "allResults")))
        navegador.execute_script("arguments[0].click();", pestaña_all_results)
        registro.registrar("Pestaña 'All Results' activada.", nivel="INFO")
        time.sleep(1)

        # Clic en botón "Download"
        boton_descarga = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a.downloadBtn[title='Download']")))
        navegador.execute_script("arguments[0].click();", boton_descarga)
        registro.registrar("Botón 'Download' presionado.", nivel="INFO")

        # Validación de presencia de #exportDownloadNotReady 3 segundos después del clic
        time.sleep(2)
        try:
            navegador.find_element(By.CSS_SELECTOR, "#exportDownloadNotReady")
            registro.registrar("'exportDownloadNotReady' detectado. Todo va bien.", nivel="INFO")
        except:
            registro.registrar("No apareció 'exportDownloadNotReady'. Página posiblemente bugueada.", nivel="ERROR")
            raise Exception("Reiniciar proceso por bug en la exportación de artículos.")


        
      
        # Esperar a que el botón final esté habilitado y hacer clic
        registro.registrar("Esperando a que ACM genere el archivo BibTeX...", nivel="INFO")
        esperar_boton_download_habilitado(navegador)

        # Validar que el archivo .bib se haya descargado correctamente
        ruta_archivo = esperar_archivo_descargado(RUTA_DESCARGAS_ARTICULOS)
        registro.registrar(f"Archivo BibTeX guardado en: {ruta_archivo}", nivel="EXITO")

    except Exception as e:
        registro.registrar(f"Ocurrió un error durante el proceso: {e}", nivel="ERROR")
        raise

    registro.registrar("Proceso finalizado.", nivel="INFO")


# Ejecutar con reintentos en caso de fallo
if __name__ == "__main__":
    MAX_INTENTOS = 3
    intentos = 0

    while intentos < MAX_INTENTOS:
        try:
            descargar_articulos_acm()
            break  # Salir si todo fue exitoso
        except Exception as e:
            intentos += 1
            registro.registrar(f"Reintentando descarga ({intentos}/{MAX_INTENTOS})...", nivel="ADVERTENCIA")
            time.sleep(5)
    else:
        registro.registrar("Todos los intentos fallaron. No se pudo completar la descarga.", nivel="CRITICO")
