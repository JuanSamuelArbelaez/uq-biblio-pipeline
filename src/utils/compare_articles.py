import bibtexparser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import textdistance
from sentence_transformers import SentenceTransformer
import argparse
import sqlite3
import os

# =========================================================
# 📦 CONFIGURACIÓN DE CACHE SQLITE
# =========================================================
CACHE_PATH = "src/cache/sim_cache.db"
os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

conn = sqlite3.connect(CACHE_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS sim_cache (
    algoritmo TEXT,
    id1 TEXT,
    id2 TEXT,
    valor REAL,
    PRIMARY KEY (algoritmo, id1, id2)
)
""")
conn.commit()


def get_cached_value(algoritmo, id1, id2):
    """Busca un valor en cache (simétrica)."""
    q = """
    SELECT valor FROM sim_cache
    WHERE algoritmo = ? AND (
        (id1 = ? AND id2 = ?) OR (id1 = ? AND id2 = ?)
    )
    """
    row = cur.execute(q, (algoritmo, id1, id2, id2, id1)).fetchone()
    return row[0] if row else None


def set_cached_value(algoritmo, id1, id2, valor):
    """Guarda valor en cache (simétrica)."""
    q = """
    INSERT OR REPLACE INTO sim_cache (algoritmo, id1, id2, valor)
    VALUES (?, ?, ?, ?)
    """
    cur.execute(q, (algoritmo, id1, id2, float(valor)))
    conn.commit()

# =========================================================
# 🧩 FUNCIONES BASE
# =========================================================

def load_bib(path="src/datos/bib/consolidado.bib"):
    with open(path, encoding="utf-8") as f:
        db = bibtexparser.load(f)
        return {entry["ID"]: entry.get("abstract", "") for entry in db.entries}


def levenshtein_sim(s1, s2):
    return 1 - textdistance.levenshtein.normalized_distance(s1, s2)


def jaccard_sim(s1, s2):
    set1, set2 = set(s1.lower().split()), set(s2.lower().split())
    return len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0


def dice_sim(s1, s2):
    set1, set2 = set(s1.lower().split()), set(s2.lower().split())
    return 2 * len(set1 & set2) / (len(set1) + len(set2)) if (set1 and set2) else 0


def tfidf_cosine(s1, s2):
    vec = TfidfVectorizer().fit([s1, s2])
    tfidf = vec.transform([s1, s2])
    return cosine_similarity(tfidf[0], tfidf[1])[0][0]


def sbert_cosine(s1, s2):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = model.encode([s1, s2])
    return cosine_similarity([emb[0]], [emb[1]])[0][0]


def compare_articles_sbert(s1, s2):
    sbert_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    embeddings = sbert_model.encode([s1, s2], convert_to_numpy=True)
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]


def compare_articles(abstracts, ids):
    n = len(ids)
    for i in range(n):
        for j in range(i + 1, n):
            s1, s2 = abstracts[ids[i]], abstracts[ids[j]]
            print(f"\nComparando {ids[i]} vs {ids[j]}:")
            print(" Levenshtein:", levenshtein_sim(s1, s2))
            print(" Jaccard:", jaccard_sim(s1, s2))
            print(" Dice:", dice_sim(s1, s2))
            print(" TF-IDF Cosine:", tfidf_cosine(s1, s2))
            print(" SBERT Cosine 1:", sbert_cosine(s1, s2))
            print(" SBERT Cosine 2:", compare_articles_sbert(s1, s2))


def run_comparison_from_ids(ids_str):
    ids = ids_str.split(",")
    results = compare_matrices_from_ids(ids)
    for nombre, data in results.items():
        print(f"\n🔹 {nombre}")
        print(np.array(data["matrix"]))
    return results


# =========================================================
# 🔹 FUNCIÓN PRINCIPAL CON CACHE Y MODELOS CARGADOS UNA SOLA VEZ
# =========================================================
# Cargar modelos SBERT una vez (persisten entre llamadas Flask)

_SbertMiniLM = SentenceTransformer("all-MiniLM-L6-v2")
_SbertMPNet = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def compare_matrices_from_ids(ids_list):
    """Devuelve matrices de similitud, con cache persistente y ordenadas por ID."""
    abstracts = load_bib()
    subset = {i: abstracts[i] for i in ids_list if i in abstracts}
    keys = sorted(subset.keys())  # Orden ascendente para front
    n = len(keys)

    algos = {
        "Levenshtein": levenshtein_sim,
        "Jaccard": jaccard_sim,
        "Dice": dice_sim,
        "TF-IDF": tfidf_cosine,
        "SBERT (MiniLM)": lambda s1, s2: cosine_similarity(
            [_SbertMiniLM.encode(s1)], [_SbertMiniLM.encode(s2)]
        )[0][0],
        "SBERT (MPNet)": lambda s1, s2: cosine_similarity(
            [_SbertMPNet.encode(s1)], [_SbertMPNet.encode(s2)]
        )[0][0],
    }

    matrices = {}
    cache_updates = []

    for nombre, func in algos.items():
        M = np.zeros((n, n))
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    M[i, j] = 1
                else:
                    id1, id2 = keys[i], keys[j]
                    val = get_cached_value(nombre, id1, id2)
                    if val is None:
                        val = func(subset[id1], subset[id2])
                        cache_updates.append((nombre, id1, id2, float(val)))
                    M[i, j] = val
                    M[j, i] = val
        matrices[nombre] = {"ids": keys, "matrix": M.tolist()}

    # Guardar todos los nuevos valores en una sola operación (más eficiente)
    if cache_updates:
        cur.executemany(
            "INSERT OR REPLACE INTO sim_cache (algoritmo, id1, id2, valor) VALUES (?, ?, ?, ?)",
            cache_updates
        )
        conn.commit()

    return matrices


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Herramienta de comparación de artículos")
    parser.add_argument("--compare_ids", type=str, help="IDs separados por coma. Ej: --compare_ids cons1,cons2")
    args = parser.parse_args()

    ids_str = args.compare_ids or "cons1,cons2"
    run_comparison_from_ids(ids_str)
