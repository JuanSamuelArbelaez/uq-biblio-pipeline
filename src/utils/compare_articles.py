import bibtexparser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import textdistance
from sentence_transformers import SentenceTransformer
import argparse


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
    abstracts = load_bib()
    ids = ids_str.split(",")
    output = []
    n = len(ids)
    for i in range(n):
        for j in range(i + 1, n):
            s1, s2 = abstracts[ids[i]], abstracts[ids[j]]
            output.append(f"\nComparando {ids[i]} vs {ids[j]}:")
            output.append(f" Levenshtein: {levenshtein_sim(s1, s2)}")
            output.append(f" Jaccard: {jaccard_sim(s1, s2)}")
            output.append(f" Dice: {dice_sim(s1, s2)}")
            output.append(f" TF-IDF Cosine: {tfidf_cosine(s1, s2)}")
            output.append(f" SBERT Cosine 1: {sbert_cosine(s1, s2)}")
            output.append(f" SBERT Cosine 2: {compare_articles_sbert(s1, s2)}")
    return "\n".join(output)


# 🔹 NUEVA FUNCIÓN para uso en Flask
def compare_matrices_from_ids(ids_list):
    """Devuelve las matrices de similitud para los artículos dados."""
    abstracts = load_bib()
    subset = {i: abstracts[i] for i in ids_list if i in abstracts}
    keys = list(subset.keys())
    n = len(keys)

    algos = {
        "Levenshtein": levenshtein_sim,
        "Jaccard": jaccard_sim,
        "Dice": dice_sim,
        "TF-IDF": tfidf_cosine,
        "SBERT (MiniLM)": sbert_cosine,
        "SBERT (MPNet)": compare_articles_sbert,
    }

    matrices = {}
    for nombre, func in algos.items():
        M = np.zeros((n, n))
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    M[i, j] = 1
                else:
                    valor = func(subset[keys[i]], subset[keys[j]])
                    M[i, j] = valor
                    M[j, i] = valor
        matrices[nombre] = {"ids": keys, "matrix": M.tolist()}

    return matrices


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Herramienta de comparación de artículos")
    parser.add_argument("--compare_ids", type=str, help="IDs de artículos a comparar, separados por coma. Ej: --compare_ids cons1,cons2")
    args = parser.parse_args()

    ids_str = args.compare_ids or "cons1,cons2"
    print(run_comparison_from_ids(ids_str))
