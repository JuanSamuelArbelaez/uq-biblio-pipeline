import time
import pandas as pd
from src.sorters.sorters import algoritmos
from pybtex.database import parse_file
from src.utils.registro import registro

def analizar_algoritmos(archivo_bib, salida_csv="src/datos/sorters_analisis/algoritmos.csv", salida_png="src/datos/sorters_analisis/algoritmos.png"):
    """
    Analiza el rendimiento de varios algoritmos de ordenamiento sobre los artículos de un archivo .bib.
    Exporta resultados a CSV y genera un diagrama de barras.
    """

    registro.registrar("Iniciando análisis de algoritmos de ordenamiento de artículos...", nivel="INFO")

    # 1️⃣ Cargar artículos del archivo .bib
    registro.registrar(f"Cargando archivo BibTeX: {archivo_bib}", nivel="INFO")
    bib = parse_file(archivo_bib)
    productos = []
    for key, entrada in bib.entries.items():
        year = entrada.fields.get("year", "0")
        title = entrada.fields.get("title", "").strip()
        productos.append({"year": int(year) if year.isdigit() else 0, "title": title})
    registro.registrar(f"Se cargaron {len(productos)} productos académicos para el análisis.", nivel="EXITO")

    # 2️⃣ Definir la clave de ordenamiento general (año → título)
    def key(x):
        return (x["year"], x["title"].lower())

    # 3️⃣ Ejecutar algoritmos y medir tiempos
    resultados = []
    for nombre, funcion in algoritmos.items():
        registro.registrar(f"Iniciando ejecución de {nombre} con {len(productos)} elementos...", nivel="INFO")

        for n in range(10): # reintentos
            datos = productos[:]  # copia de la lista original

            # Usar clave numérica para algoritmos que lo requieren
            if nombre in ["Pigeonhole Sort", "BucketSort", "RadixSort", "Bitonic Sort"]:
                key_func = lambda x: hash((x["year"], x["title"].lower()))
                registro.registrar(f"{nombre} usará clave numérica (hash) para el ordenamiento.", nivel="ADVERTENCIA")
            else:
                key_func = key
            
            try:
                inicio = time.perf_counter()
                _ = funcion(datos, key_func)
                fin = time.perf_counter()
                duracion = fin - inicio
                registro.registrar_exito(f"{nombre} completado en {duracion:.6f} segundos.")
                break
            except Exception as e:
                duracion = float("nan")
                if n < 9:
                    registro.registrar(f"{nombre} falló durante la ejecución: {str(e)}. Reintentando...", nivel="ADVERTENCIA")
                else: 
                    registro.registrar(f"{nombre} falló durante la ejecución: {str(e)}. Fallo definitivo...", nivel="ERROR")

        resultados.append({
            "Método": nombre,
            "Tamaño": len(datos),
            "Tiempo": duracion
        })

    # 4️⃣ Exportar resultados a CSV
    df = pd.DataFrame(resultados).sort_values(by="Tiempo", ascending=True)
    df.to_csv(salida_csv, index=False)
    registro.registrar_exito(f"Resultados exportados a CSV: {salida_csv}")

    # 5️⃣ Graficar resultados
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.barh(df["Método"], df["Tiempo"])
        plt.xlabel("Tiempo (segundos)")
        plt.ylabel("Algoritmo")
        plt.title("Comparación de Algoritmos de Ordenamiento")
        plt.tight_layout()
        plt.savefig(salida_png)
        plt.close()
        registro.registrar_exito(f"Diagrama de barras generado: {salida_png}")
    except Exception as e:
        registro.registrar(f"No se pudo generar el gráfico: {str(e)}", nivel="ERROR")

    registro.registrar_exito("Análisis de algoritmos de ordenamiento finalizado.")
    return df
