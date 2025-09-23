from src.downloaders.descargador_acm import descargar_articulos_acm
from src.downloaders.descargador_sciencedirect import descargar_articulos_sciencedirect
from src.utils.registro import registro

class DescargadorArticulos:
    def ejecutar(self):
        """Orquesta todo el proceso de descarga"""
        registro.registrar("=== INICIANDO DESCARGA ===", nivel="INFO")
        self._descargar_acm()
        self._descargar_sciencedirect()
    
    def _descargar_acm(self):
        try:
            descargar_articulos_acm()
            registro.registrar("✓ Descarga ACM completada", nivel="EXITO")
        except Exception as e:
            registro.registrar(f"Error descarga ACM: {str(e)}", nivel="ERROR")

    def _descargar_sciencedirect(self):
        try:
            descargar_articulos_sciencedirect()
            registro.registrar("✓ Descarga ScienceDirect completada", nivel="EXITO")
        except Exception as e:
            registro.registrar(f"Error descarga ScienceDirect: {str(e)}", nivel="ERROR")

descargadorArticulosBIBs = DescargadorArticulos()