#!/usr/bin/env python3
"""
utils/visuals_wordcloud_only.py

Script exclusivo para generar la NUBE DE PALABRAS a partir de un archivo BibTeX.

Características:
- Limpieza avanzada de texto (abstracts + keywords)
- Eliminación de stopwords (español/inglés)
- Nube de palabras profesional (WordCloud + Matplotlib)
- Guardado automático en carpeta de salida

Dependencias:
    pandas, bibtexparser, nltk, wordcloud, matplotlib
"""

import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Manejo de stopwords
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    STOPWORDS_AVAILABLE = True
except ImportError:
    STOPWORDS_AVAILABLE = False

# Lectura de archivos BibTeX
import bibtexparser

plt.style.use('seaborn-v0_8-darkgrid')


# -----------------------------------------------------------
# FUNCIONES PRINCIPALES
# -----------------------------------------------------------

def load_bib(bib_path: str | Path) -> list[dict]:
    """Carga el archivo .bib y retorna una lista de entradas (dicts)."""
    bib_path = Path(bib_path)
    with open(bib_path, "r", encoding="utf-8", errors="ignore") as f:
        db = bibtexparser.load(f)
    return db.entries


def clean_text_for_wordcloud(text: str) -> str:
    """Limpia y procesa texto para la nube de palabras."""
    if not text:
        return ""

    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()

    if STOPWORDS_AVAILABLE:
        stop_words = set(stopwords.words('english')) | set(stopwords.words('spanish'))
        stop_words.update([
            'using', 'based', 'approach', 'method', 'algorithm', 'system',
            'paper', 'study', 'analysis', 'research', 'data', 'results',
            'conclusion', 'introduction', 'methodology', 'discussion'
        ])
        words = word_tokenize(text)
        text = ' '.join([word for word in words if word not in stop_words and len(word) > 2])

    return text


def build_wordcloud(entries: list[dict], out_png: Path) -> None:
    """Genera y guarda una nube de palabras a partir de abstracts y keywords."""
    corpus = []

    for e in entries:
        if isinstance(e.get("abstract"), str):
            corpus.append(clean_text_for_wordcloud(e["abstract"]))
        if isinstance(e.get("keywords"), str):
            keywords_clean = e["keywords"].replace(";", " ").replace(",", " ")
            corpus.append(clean_text_for_wordcloud(keywords_clean))

    text = " ".join(corpus)
    if not text.strip():
        text = "No data available"

    wc = WordCloud(
        width=1600,
        height=900,
        background_color="white",
        colormap="viridis",
        max_words=100,
        relative_scaling=0.5,
        min_font_size=10,
        prefer_horizontal=0.7,
        max_font_size=100
    )

    wordcloud_img = wc.generate(text)

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.imshow(wordcloud_img, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Nube de Palabras - Términos Más Frecuentes',
                 fontsize=20, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"✅ Nube de palabras guardada en: {out_png}")


def main_wordcloud_only():
    """Ejecuta el proceso completo solo para la nube de palabras."""
    bib_path = Path("src/datos/bib/consolidado.bib")
    out_dir = Path("src/datos/graphs/wordcloud")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not bib_path.exists():
        print(f"❌ Error: No se encontró el archivo {bib_path}")
        return

    print("Cargando datos bibliográficos...")
    entries = load_bib(bib_path)
    print(f"Entradas cargadas: {len(entries)}")

    out_png = out_dir / "wordcloud.png"
    print("Generando nube de palabras...")
    build_wordcloud(entries, out_png)

    print("\n🎉 Proceso completado exitosamente.")


if __name__ == "__main__":
    main_wordcloud_only()
