from flask import Flask, jsonify, render_template, request, send_from_directory
import os
from pathlib import Path
import sys
import pandas as pd

# --- Ajustar path del proyecto para importar src ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

try:
    from utils.consolidado_bibtex import generar_consolidado_bibtex
except ModuleNotFoundError as e:
    print(f"[ERROR] No se pudo importar 'utils.consolidado_bibtex': {e}")
    sys.exit(1)

try:
    from utils.compare_articles import compare_matrices_from_ids
except ModuleNotFoundError as e:
    print(f"[ERROR] No se pudo importar 'utils.compare_articles': {e}")
    sys.exit(1)

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/articulos")
def api_articulos():
    articulos = generar_consolidado_bibtex()
    return jsonify(articulos)

@app.route("/api/top_autores")
def api_top_autores():
    """
    Devuelve los 15 autores principales desde el CSV.
    """
    try:
        csv_path = os.path.join(SRC_PATH, "datos", "autores", "top15_autores.csv")
        df = pd.read_csv(csv_path)
        if "Apariciones" in df.columns:
            df = df.sort_values(by="Apariciones", ascending=False)
        data = df.to_dict(orient="records")
        return jsonify(data)
    except Exception as e:
        print(f"[ERROR] al leer top15_autores.csv: {e}")
        return jsonify([])
    
@app.route("/api/analisis", methods=["POST"])
def api_analisis():
    data = request.get_json()
    ids = data.get("ids", [])

    if not ids:
        return jsonify({"error": "No se enviaron IDs"}), 400

    matrices = compare_matrices_from_ids(ids)
    return jsonify(matrices)


@app.route("/api/keywords_freq")
def keywords_freq():
    try:
        try:
            from utils.keywords_analizer import main_keywords_analizer, load_bib, count_keyword_frequencies, keywords
        except ModuleNotFoundError as e:
            print(f"[ERROR] No se pudo importar 'utils.keyword_analizer': {e}")
            sys.exit(1)      

        abstracts = load_bib()
        freqs = count_keyword_frequencies(abstracts, keywords)
        data = [{"Keyword": k, "Frecuencia": v} for k, v in freqs.items()]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/src/outputs/<path:filename>")
def servir_outputs(filename):
    """
    Sirve archivos desde src/outputs/keywords_analizer/
    Permitirá acceder a rutas como:
    http://localhost:5000/src/outputs/keywords_analizer/new_terms_tfidf_freq.png
    """
    base_dir = Path(__file__).resolve().parent.parent / "src" / "outputs" / "keywords_analizer"
    return send_from_directory(base_dir, filename)

@app.route("/api/graficas")
def api_graficas():
    """
    Devuelve las URLs de todas las gráficas estáticas disponibles.
    """
    base_dir = Path(__file__).resolve().parent.parent

    rutas = {
        "keywords": base_dir / "src" / "outputs" / "keywords_analizer" / "new_terms_tfidf_freq.png",
        "location": base_dir / "src" / "datos" / "graphs" / "location" / "location_bibtex.png",
        "timeline": [
            base_dir / "src" / "datos" / "graphs" / "timeline" / "timeline_areas_bibtex.png",
            base_dir / "src" / "datos" / "graphs" / "timeline" / "timeline_barras_bibtex.png"
        ],
        "wordcloud": base_dir / "src" / "datos" / "graphs" / "wordcloud" / "wordcloud.png",
        "followup": [
            base_dir / "src" / "follow-ups" / "follow-up2" / "outputs" / "citation_graph_connected.png",
            base_dir / "src" / "follow-ups" / "follow-up2" / "outputs" / "cooccurrence_graph.png"
        ]
    }

    data = {}

    for key, path in rutas.items():
        if isinstance(path, list):
            imgs = []
            for p in path:
                if p.exists():
                    imgs.append(f"/graficas/{key}/{p.name}")
            data[key] = imgs
        else:
            if path.exists():
                data[key] = [f"/graficas/{key}/{path.name}"]
            else:
                data[key] = []

    return jsonify(data)


@app.route("/graficas/<categoria>/<path:filename>")
def servir_grafica(categoria, filename):
    """
    Sirve imágenes de las distintas categorías de gráficas.
    """
    base_dir = Path(__file__).resolve().parent.parent / "src"
    subrutas = {
        "keywords": base_dir / "outputs" / "keywords_analizer",
        "location": base_dir / "datos" / "graphs" / "location",
        "timeline": base_dir / "datos" / "graphs" / "timeline",
        "wordcloud": base_dir / "datos" / "graphs" / "wordcloud",
        "followup": base_dir / "follow-ups" / "follow-up2" / "outputs"
    }
    if categoria not in subrutas:
        abort(404)
    return send_from_directory(subrutas[categoria], filename)


if __name__ == "__main__":
    print(f"[INFO] Ejecutando app Flask con SRC_PATH = {SRC_PATH}")
    app.run(debug=True, port=5000)
