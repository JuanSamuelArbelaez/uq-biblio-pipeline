import bibtexparser
import pandas as pd
import matplotlib.pyplot as plt
import os

def generar_barras_bibtex(bib_path: str, output_path: str = "barras_publicaciones.png") -> str:
    """
    Genera un gráfico de barras agrupadas por publisher/journal y año (Top 10 + Sin publisher/journal + Otros)
    a partir de un archivo BibTeX.
    """

    # Leer archivo BibTeX
    with open(bib_path, encoding="utf-8") as bibfile:
        bib_database = bibtexparser.load(bibfile)

    registros = []
    for entry in bib_database.entries:
        year = entry.get("year", "").strip()
        publisher = (
            entry.get("publisher", "").strip()
            or entry.get("journal", "").strip()
            or "Sin publisher/journal"
        )
        if year.isdigit():
            registros.append({"year": int(year), "publisher": publisher})

    df = pd.DataFrame(registros)
    if df.empty:
        raise ValueError("No se encontraron publicaciones con año válido en el archivo .bib")

    # Top 10 publishers + Sin publisher/journal + Otros
    conteo = df["publisher"].value_counts()
    top_publishers = conteo.head(20).index.tolist()
    tiene_sin = "Sin publisher/journal" in df["publisher"].unique()
    categorias = top_publishers + (["Sin publisher/journal"] if tiene_sin else []) + ["Otros"]

    df["publisher_group"] = df["publisher"].apply(lambda x: x if x in categorias else "Otros")

    resumen = df.groupby(["publisher_group", "year"]).size().unstack(fill_value=0)
    resumen = resumen.sort_index()

    resumen.T.plot(kind="bar", figsize=(12, 7))
    plt.title("Publicaciones por año y publisher/journal (Top 10 + Otros)", fontsize=14)
    plt.xlabel("Año", fontsize=12)
    plt.ylabel("Número de publicaciones", fontsize=12)
    plt.legend(title="Publisher / Journal", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()

    return os.path.abspath(output_path)

def generar_areas_bibtex(bib_path: str, output_path: str = "areas_publicaciones.png") -> str:
    """
    Genera un gráfico de áreas apiladas mostrando la evolución de publicaciones
    por año y publisher/journal (Top 10 + Sin publisher/journal + Otros).
    """

    with open(bib_path, encoding="utf-8") as bibfile:
        bib_database = bibtexparser.load(bibfile)

    registros = []
    for entry in bib_database.entries:
        year = entry.get("year", "").strip()
        publisher = (
            entry.get("publisher", "").strip()
            or entry.get("journal", "").strip()
            or "Sin publisher/journal"
        )
        if year.isdigit():
            registros.append({"year": int(year), "publisher": publisher})

    df = pd.DataFrame(registros)
    if df.empty:
        raise ValueError("No se encontraron publicaciones con año válido en el archivo .bib")

    # Top 10 publishers + Sin publisher/journal + Otros
    conteo = df["publisher"].value_counts()
    top_publishers = conteo.head(20).index.tolist()
    tiene_sin = "Sin publisher/journal" in df["publisher"].unique()
    categorias = top_publishers + (["Sin publisher/journal"] if tiene_sin else []) + ["Otros"]

    df["publisher_group"] = df["publisher"].apply(lambda x: x if x in categorias else "Otros")

    resumen = df.groupby(["year", "publisher_group"]).size().unstack(fill_value=0)
    resumen = resumen.sort_index()

    x = resumen.index.values
    y = resumen.values.T
    publishers = resumen.columns.tolist()
    n = len(publishers)

    # Paleta de colores variada (hasta 20 colores únicos)
    if n <= 10:
        cmap = plt.cm.get_cmap("tab10", n)
    elif n <= 20:
        cmap = plt.cm.get_cmap("tab20", n)
    else:
        cmap = plt.cm.get_cmap("nipy_spectral", n)
    colors = [cmap(i) for i in range(n)]

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.stackplot(x, y, labels=publishers, colors=colors, alpha=0.9, linewidth=0.5)

    ax.set_title("Evolución de publicaciones por año y publisher/journal (Top 10 + Otros)", fontsize=14)
    ax.set_xlabel("Año", fontsize=12)
    ax.set_ylabel("Número de publicaciones", fontsize=12)
    ax.legend(title="Publisher / Journal", loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
    ax.grid(alpha=0.3)

    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()

    return os.path.abspath(output_path)
