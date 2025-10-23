import bibtexparser
import pandas as pd
import plotly.express as px
import pycountry
import os

def generar_mapa_calor_bibtex(bib_path: str, output_path: str = "mapa_publicaciones.png") -> str:
    """
    Genera un mapa de calor geográfico (por país) basado en publicaciones de un archivo BibTeX.
    Usa los campos 'country', 'address' o 'location' para inferir el país.

    Muestra una etiqueta indicando cuántos artículos no tienen país identificado.
    """

    # Leer archivo BibTeX
    with open(bib_path, encoding="utf-8") as bibfile:
        bib_database = bibtexparser.load(bibfile)

    records = []
    sin_pais = 0

    for entry in bib_database.entries:
        raw_field = entry.get("location", "") or entry.get("address", "") or entry.get("country", "")
        raw_field = raw_field.strip()

        if not raw_field:
            sin_pais += 1
            continue

        country_name = None
        field_lower = raw_field.lower()

        # 1️⃣ Buscar coincidencia con países conocidos
        for country in pycountry.countries:
            possible_names = {country.name.lower()}
            if hasattr(country, "official_name"):
                possible_names.add(country.official_name.lower())
            if hasattr(country, "common_name"):
                possible_names.add(country.common_name.lower())

            if any(name in field_lower for name in possible_names):
                country_name = country.name
                break

        # 2️⃣ Buscar coincidencias manuales con siglas o abreviaciones
        if not country_name:
            manual_map = {
                "usa": "United States",
                "us": "United States",
                "uk": "United Kingdom",
                "uae": "United Arab Emirates",
                "prc": "China",
                "russia": "Russian Federation",
                "iran": "Iran, Islamic Republic of",
                "korea": "Korea, Republic of",
                "germany": "Germany",
                "china": "China"
            }
            for code, name in manual_map.items():
                if code in field_lower:
                    country_name = pycountry.countries.lookup(name).name
                    break

        # 3️⃣ Intentar lookup directo como último recurso
        if not country_name:
            try:
                country_obj = pycountry.countries.lookup(raw_field)
                country_name = country_obj.name
            except LookupError:
                sin_pais += 1
                continue

        records.append(country_name)

    # Crear DataFrame con los países y contar ocurrencias
    df = pd.DataFrame(records, columns=["country"])
    df = df.groupby("country").size().reset_index(name="count")

    if df.empty:
        raise ValueError("No se detectaron países válidos en el archivo BibTeX.")

    # Crear el mapa de calor
    fig = px.choropleth(
        df,
        locations="country",
        locationmode="country names",
        color="count",
        color_continuous_scale="YlOrRd",
        title="Mapa de calor de publicaciones por país",
    )

    # Añadir anotación con los artículos sin país
    fig.add_annotation(
        text=f"Artículos sin país identificado: {sin_pais}",
        x=0.5,
        y=-0.15,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=12, color="black"),
        align="center"
    )

    fig.update_layout(
        title_x=0.5,
        geo=dict(showframe=False, showcoastlines=True, projection_type="equirectangular"),
        margin=dict(l=40, r=40, t=80, b=80),
        template="plotly_white"
    )

    # Crear carpeta destino si no existe
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Guardar imagen
    fig.write_image(output_path)

    return os.path.abspath(output_path)
