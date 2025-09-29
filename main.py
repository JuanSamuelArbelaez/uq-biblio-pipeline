from pathlib import Path

from src.sorters.analisis_sorters import analizar_algoritmos
from src.downloaders.descarga_controlador import DescargadorArticulos
from src.utils.deduplicador import deduplicar_bibtex 
from src.utils.registro import registro
from src.config.ajustes import RUTA_DESCARGAS_ARTICULOS, ARCHIVO_UNIFICADO
from src.sorters.sorters import pigeonhole_sort
from src.sorters.autores_top import analizar_autores

def main():
    registro.registrar("Iniciando proceso de descarga de artículos...", nivel="INFO")

    # 1️⃣ Ejecutar descargas
    descargador = DescargadorArticulos()
    descargador.ejecutar()

    # 2️⃣ Ejecutar deduplicador después de las descargas
    archivos = list(Path(RUTA_DESCARGAS_ARTICULOS).glob("*.bib"))

    salida_consolidado = ARCHIVO_UNIFICADO.parent / "consolidado.bib"
    salida_corruptos = ARCHIVO_UNIFICADO.parent / "corruptos.bib"
    salida_duplicados = ARCHIVO_UNIFICADO.parent / "duplicados.bib"

    deduplicar_bibtex(archivos, salida_consolidado, salida_corruptos, salida_duplicados)

    registro.registrar("Pipeline completado con éxito 🚀", nivel="EXITO")

    # 3️⃣ Ejecutar analisis de algoritmos después del deduplicado
    salida_consolidado = ARCHIVO_UNIFICADO.parent / "consolidado.bib"
    df = analizar_algoritmos(salida_consolidado)
    print(df)
    registro.registrar("Analisis de algorítmos de ordenamiento de artículos completado con éxito 🚀", nivel="EXITO")


    # 4️⃣ Ejecutar análisis de autores después del deduplicado
    salida_consolidado = ARCHIVO_UNIFICADO.parent / "consolidado.bib"
    salida_autores_csv = "src/datos/autores/top15_autores.csv"
    salida_autores_png = "src/datos/autores/top15_autores.png"

    analizar_autores(salida_consolidado, salida_autores_csv, salida_autores_png)


if __name__ == "__main__":
    main()
