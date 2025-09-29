import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from pybtex.database import parse_file
from src.utils.registro import registro

def analizar_autores(bib_path, salida_csv, salida_png):
    """
    Ordena de manera ascendente los quince primeros autores con más apariciones
    en los productos académicos.
    Genera un CSV y un diagrama de barras.
    """
    registro.registrar("Iniciando análisis de autores...", nivel="INFO")

    if not os.path.exists(bib_path):
        registro.registrar(f"Archivo no encontrado: {bib_path}", nivel="ERROR")
        return None

    # Cargar archivo BibTeX
    bib_data = parse_file(bib_path)
    registro.registrar(f"Archivo BibTeX cargado: {bib_path}", nivel="EXITO")

    # Contar autores
    autores = []
    for entry in bib_data.entries.values():
        if "author" in entry.persons:
            for p in entry.persons["author"]:
                nombre = " ".join(p.first_names + p.last_names)
                autores.append(nombre.strip())

    contador = Counter(autores)

    # Tomar los 15 autores con más apariciones (ascendente por frecuencia)
    top15 = contador.most_common(15)
    top15.sort(key=lambda x: x[1])  # ordenar ascendente

    df = pd.DataFrame(top15, columns=["Autor", "Apariciones"])

    # Exportar CSV
    os.makedirs(os.path.dirname(salida_csv), exist_ok=True)
    df.to_csv(salida_csv, index=False, encoding="utf-8")
    registro.registrar_exito(f"Resultados exportados a CSV: {salida_csv}")

    # Generar diagrama de barras
    plt.figure(figsize=(10, 6))
    plt.barh(df["Autor"], df["Apariciones"])
    plt.xlabel("Número de apariciones")
    plt.ylabel("Autor")
    plt.title("Top 15 autores con más apariciones (ascendente)")
    plt.tight_layout()
    plt.savefig(salida_png, dpi=300)
    plt.close()
    registro.registrar_exito(f"Diagrama de barras generado: {salida_png}")

    return df

