import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from src.config.ajustes import CANTIDAD_LOGS

class Registro:
    """
    Clase para gestionar el registro de logs con diferentes niveles.
    Los logs se guardan en la carpeta 'registros' (al mismo nivel que las demás carpetas del proyecto)
    y se limita la cantidad de archivos mediante rotación.

    Para utilizarla, basta con importar la instancia global 'registro':
        from utilidades.registro import registro

    Y luego usar:
        registro.registrar("Mensaje de log", nivel="INFO")

    Los emojis se agregan automáticamente según el nivel.
    """

    EMOJIS = {
        'INFO': "ℹ️",
        'ADVERTENCIA': "⚠️",
        'ERROR': "❌",
        'CRITICO': "🚨",
        'EXITO': "✅"
    }

    def __init__(self, carpeta_registros="registros", limite_archivos=CANTIDAD_LOGS, tamaño_maximo=10*1024*1024):
        """
        Inicializa el sistema de registros.

        :param carpeta_registros: Carpeta donde se guardarán los archivos de registro.
        :param limite_archivos: Número máximo de archivos log (rotación).
        :param tamaño_maximo: Tamaño máximo de cada archivo log antes de rotarlo (en bytes).
        """
        self.carpeta_registros = "src/"+carpeta_registros
        if not os.path.exists(self.carpeta_registros):
            os.makedirs(self.carpeta_registros)

        # Crear un nombre único para el archivo log con la fecha y hora
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.ruta_log = os.path.join(self.carpeta_registros, f"registro_{timestamp}.log")

        # Configurar el manejador rotativo con codificación UTF-8
        self.manejador = RotatingFileHandler(
            self.ruta_log,
            maxBytes=tamaño_maximo,
            backupCount=limite_archivos,
            encoding="utf-8"
        )
        self.manejador.setLevel(logging.INFO)
        formato = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        self.manejador.setFormatter(formato)

        # Configuración global del logger
        self.logger = logging.getLogger("LoggerBibliometria")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            self.logger.addHandler(self.manejador)

        # Limitar los archivos a un máximo de CANTIDAD_LOGS
        self.limitar_archivos()

    def _imprimir_consola(self, mensaje, nivel):
        """
        Imprime el mensaje en consola con formato y colores.
        """
        colores = {
            'INFO': '\033[94m',      # Azul
            'ADVERTENCIA': '\033[93m',  # Amarillo
            'ERROR': '\033[91m',     # Rojo
            'CRITICO': '\033[41m',   # Fondo rojo
            'EXITO': '\033[92m',     # Verde
            'RESET': '\033[0m'
        }
        print(f"{colores.get(nivel, '')}[{nivel}]{mensaje}{colores['RESET']}")

    def registrar(self, mensaje, nivel="INFO"):
        """
        Registra un mensaje en el archivo de log y lo imprime en consola.
        Se agrega un emoji automáticamente según el nivel.

        :param mensaje: Mensaje a registrar.
        :param nivel: Nivel del mensaje ('INFO', 'ADVERTENCIA', 'ERROR', 'CRITICO', 'EXITO').
        """
        nivel_mayuscula = nivel.upper()
        emoji = self.EMOJIS.get(nivel_mayuscula, "")
        mensaje_con_emoji = f"{emoji}  {mensaje}"  # Espacio adicional para claridad visual

        if nivel_mayuscula == "EXITO":
            self.logger.info(f"[EXITO] {mensaje_con_emoji}")
        else:
            niveles_log = {
                "INFO": self.logger.info,
                "ADVERTENCIA": self.logger.warning,
                "ERROR": self.logger.error,
                "CRITICO": self.logger.critical
            }
            niveles_log.get(nivel_mayuscula, self.logger.info)(mensaje_con_emoji)

        self._imprimir_consola(mensaje_con_emoji, nivel_mayuscula)

    def registrar_exito(self, mensaje):
        """
        Método específico para registrar un mensaje de éxito.
        :param mensaje: Mensaje a registrar como exitoso.
        """
        self.registrar(mensaje, nivel="EXITO")

    def ver_ultimo_log(self):
        """
        Devuelve el contenido del archivo de log más reciente.

        :return: Texto con el contenido del último archivo de log.
        """
        archivos = sorted(
            [f for f in os.listdir(self.carpeta_registros) if f.endswith(".log")],
            key=lambda x: os.path.getmtime(os.path.join(self.carpeta_registros, x)),
            reverse=True
        )
        if archivos:
            with open(os.path.join(self.carpeta_registros, archivos[0]), 'r', encoding="utf-8") as f:
                return f.read()
        return "No se encontraron archivos de log."

    def ver_todos_los_logs(self):
        """
        Lista todos los archivos de log disponibles en la carpeta.

        :return: Lista con los nombres de los archivos de log.
        """
        return sorted(
            [f for f in os.listdir(self.carpeta_registros) if f.endswith(".log")],
            key=lambda x: os.path.getmtime(os.path.join(self.carpeta_registros, x)),
            reverse=True
        )

    def limitar_archivos(self):
        """
        Limita la cantidad de archivos log a un máximo de CANTIDAD_LOGS definido en configuracion/ajustes.py, eliminando los más antiguos.
        """
        archivos = sorted(
            [f for f in os.listdir(self.carpeta_registros) if f.endswith(".log")],
            key=lambda x: os.path.getmtime(os.path.join(self.carpeta_registros, x)),
            reverse=False  # Ordenar de más antiguo a más reciente
        )
        while len(archivos) > CANTIDAD_LOGS:
            archivo_a_eliminar = archivos.pop(0)  # El archivo más antiguo
            os.remove(os.path.join(self.carpeta_registros, archivo_a_eliminar))


# Instancia global para facilitar su uso en otros módulos
registro = Registro()
