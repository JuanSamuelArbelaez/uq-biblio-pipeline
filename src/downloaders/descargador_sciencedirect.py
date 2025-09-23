import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.config.ajustes import RUTA_DESCARGAS_ARTICULOS, URL_SCIENCEDIRECT, EMAIL_GMAIL_SD, CONTRASENA_GMAIL_SD
from src.utils.registro import registro  # Se importa la clase Registro
from src.utils.navegador import configurar_navegador, esperar_archivo_descargado


def descargar_articulos_sciencedirect():
    registro.registrar("Iniciando descarga de artículos desde Science Direct...", nivel="INFO")
    os.makedirs(RUTA_DESCARGAS_ARTICULOS, exist_ok=True)

    navegador = configurar_navegador("O")
    navegador.get(URL_SCIENCEDIRECT)
    time.sleep(5)

    try:
        wait = WebDriverWait(navegador, 15)

        # 🔐 Iniciar sesión con Google
        registro.registrar("Buscando botón de inicio con Google...", nivel="INFO")
        boton_google = wait.until(EC.element_to_be_clickable((By.ID, "btn-google")))
        navegador.execute_script("arguments[0].click();", boton_google)
        registro.registrar("Botón 'Iniciar sesión con Google' presionado.", nivel="INFO")

        # ✉️ Ingresar correo institucional
        registro.registrar("Ingresando correo institucional...", nivel="INFO")
        campo_email = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
        campo_email.send_keys(EMAIL_GMAIL_SD)

        boton_siguiente_email = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#identifierNext > div > button > div.VfPpkd-RLmnJb")
        ))
        navegador.execute_script("arguments[0].click();", boton_siguiente_email)
        registro.registrar("Correo enviado. Avanzando a ingreso de contraseña...", nivel="INFO")

       # 🔑 Ingresar contraseña - VERSIÓN CORREGIDA
        registro.registrar("Esperando campo de contraseña...", nivel="INFO")

        # 1. Esperar que el campo esté realmente interactuable
        campo_contrasena = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[type='password'][name='Passwd']")
        ))

        # 2. Scroll para asegurar visibilidad
        navegador.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", campo_contrasena)

        # 3. Usar ActionChains para interacción más realista
        from selenium.webdriver.common.action_chains import ActionChains

        actions = ActionChains(navegador)
        actions.move_to_element(campo_contrasena).click().pause(1).send_keys(CONTRASENA_GMAIL_SD).perform()

        # 4. Esperar antes de hacer clic en siguiente
        time.sleep(2)

        boton_siguiente_pass = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.VfPpkd-LgbsSe-OWXEXe-k8QpJ")
        ))
        navegador.execute_script("arguments[0].click();", boton_siguiente_pass)

        # Esperar redirección
        registro.registrar("Esperando redirección y carga de resultados...", nivel="INFO")
        time.sleep(5)

        total_descargados = 0
        LIMITE_TOTAL = 4000

        while total_descargados < LIMITE_TOTAL:
            registro.registrar(f"Procesando bloque {total_descargados + 1} a {total_descargados + 100}...", nivel="INFO")

            if total_descargados > 0:
                # Seleccionar todos los artículos (desbugueo del selector)
                registro.registrar("Debugueando el selector de artículo", nivel="INFO")
                time.sleep(3) 
                label_checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='select-all-results']")))
                navegador.execute_script("arguments[0].click();", label_checkbox)

            # Seleccionar todos los artículos
            registro.registrar("Seleccionando todos los artículos de la página...", nivel="EXITO")
            time.sleep(2) 
            label_checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='select-all-results']")))
            navegador.execute_script("arguments[0].click();", label_checkbox)

            # Abrir menú de exportación
            registro.registrar("Abriendo menú de exportación...", nivel="INFO")
            time.sleep(2) 
            boton_exportar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.export-all-link-button")))
            navegador.execute_script("arguments[0].click();", boton_exportar)

            # Elegir BibTeX
            registro.registrar("Seleccionando formato BibTeX para exportación...", nivel="INFO")
            time.sleep(2)
            boton_bibtex = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-aa-button='srp-export-multi-bibtex']")))
            navegador.execute_script("arguments[0].click();", boton_bibtex)

            # Esperar descarga del archivo
            registro.registrar("Esperando descarga del archivo...", nivel="INFO")
            ruta_archivo = esperar_archivo_descargado(RUTA_DESCARGAS_ARTICULOS)
            registro.registrar(f"Archivo BibTeX descargado: {ruta_archivo}", nivel="EXITO")

            total_descargados += 100

            if total_descargados >= LIMITE_TOTAL:
                registro.registrar(f"Límite de {LIMITE_TOTAL} artículos alcanzado. Finalizando...", nivel="EXITO")
                break

            # Avanzar a la siguiente página
            registro.registrar("Avanzando a la siguiente página...", nivel="EXITO")
            boton_siguiente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                "#srp-pagination > li.pagination-link.next-link > a")
            ))
            navegador.execute_script("arguments[0].click();", boton_siguiente)
            time.sleep(5)

    except Exception as e:
        registro.registrar(f"Ocurrió un error durante el proceso: {e}", nivel="ERROR")

    registro.registrar("Proceso finalizado.", nivel="INFO")

if __name__ == "__main__":
    descargar_articulos_sciencedirect()
