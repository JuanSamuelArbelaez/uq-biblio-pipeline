import bibtexparser
from config.ajustes import ARCHIVO_UNIFICADO
from pathlib import Path

def generar_consolidado_bibtex():
    """
    Lee el archivo BibTeX consolidado (definido en ARCHIVO_UNIFICADO)
    y devuelve una lista de artículos en formato JSON para el frontend.
    """
    bib_path = Path(ARCHIVO_UNIFICADO)

    if not bib_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo consolidado: {bib_path}")

    articulos = []

    with open(bib_path, encoding="utf-8") as f:
        db = bibtexparser.load(f)

    for i, e in enumerate(db.entries):
        articulos.append({
            "id": e.get("ID", f"art_{i+1}"),
            "titulo": e.get("title", "Sin título"),
            "autores": e.get("author", "Desconocido"),
            "año": e.get("year", "N/A"),
            "abstract": e.get("abstract", "Sin resumen disponible")
        })

    print(f"[INFO] Se cargaron {len(articulos)} artículos desde {bib_path}")
    return articulos
