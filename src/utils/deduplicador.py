from pybtex.database import BibliographyData
from src.utils.registro import registro
from src.utils.parser import cargar_bibtex_seguro
from src.utils.limpiador import limpiar_keywords_bibtex

def normalizar_texto(txt: str) -> str:
    """Normaliza texto quitando espacios, puntuación y pasando a minúsculas."""
    import re
    return re.sub(r'\W+', '', txt.strip().lower())

def deduplicar_bibtex(archivos, salida_consolidado, salida_corruptos, salida_duplicados):
    """
    Deduplica archivos BibTeX priorizando DOI → URL → título+autores.
    Maneja colisiones de claves BibTeX renombrándolas si apuntan a recursos distintos.
    Genera:
      - consolidado.bib → artículos válidos y únicos
      - corruptos.bib   → artículos sin DOI, título o autores
      - duplicados.bib  → una copia de cada artículo duplicado válido
    """

    validos = {}       # recurso_id → (key, entrada)
    duplicados = {}    # recurso_id → entrada duplicada
    corruptos = {}     # clave generada → entradas corruptas
    todas_claves = set()
    contador_corruptos = 0

    registro.registrar("Iniciando proceso de deduplicación de BibTeX...", nivel="INFO")

    for archivo in archivos:
        limpiar_keywords_bibtex(archivo)

        registro.registrar(f"Procesando archivo: {archivo}", nivel="INFO")
        bib = cargar_bibtex_seguro(archivo)

        for key, entrada in bib.entries.items():
            doi = entrada.fields.get("doi", "").strip().lower()
            url = entrada.fields.get("url", "").strip().lower()
            titulo = normalizar_texto(entrada.fields.get("title", ""))
            autores = ";".join(
                [" ".join(p.last_names + p.first_names) for p in entrada.persons.get("author", [])]
            ).lower()

            # Identificador único del recurso (prioridad DOI > URL > título+autores)
            recurso_id = None
            if doi:
                recurso_id = f"doi:{doi}"
            elif url:
                recurso_id = f"url:{url}"
            elif titulo and autores:
                recurso_id = f"title:{titulo}|{autores}"

            # Caso de corrupción: no se pudo generar identificador
            if not recurso_id:
                contador_corruptos += 1
                clave_corr = f"corrupto_{contador_corruptos}"
                corruptos[clave_corr] = entrada
                registro.registrar(f"Entrada corrupta detectada (clave={clave_corr})", nivel="ADVERTENCIA")
                continue

            # Resolver colisiones de claves BibTeX (key repetida para recursos distintos)
            clave_final = key
            while clave_final in todas_claves and (
                recurso_id not in validos or validos[recurso_id][0] != clave_final
            ):
                clave_final = f"{clave_final}_dup"
            todas_claves.add(clave_final)

            # Deduplicar por recurso_id
            if recurso_id in validos:
                # Ya existe: es un duplicado real
                if recurso_id not in duplicados:
                    duplicados[recurso_id] = entrada
                registro.registrar(f"Duplicado detectado para recurso={recurso_id}", nivel="INFO")
            else:
                # Guardar como válido
                validos[recurso_id] = (clave_final, entrada)

    # Guardar resultados
    BibliographyData(entries={k: e for _, (k, e) in validos.items()}).to_file(salida_consolidado)
    registro.registrar_exito(f"Archivo consolidado generado: {salida_consolidado} ({len(validos)} entradas)")

    BibliographyData(entries=corruptos).to_file(salida_corruptos)
    registro.registrar(f"Archivo de corruptos generado: {salida_corruptos} ({len(corruptos)} entradas)", nivel="ADVERTENCIA")

    BibliographyData(entries={f"dup_{i}": e for i, e in enumerate(duplicados.values(), 1)}).to_file(salida_duplicados)
    registro.registrar(f"Archivo de duplicados generado: {salida_duplicados} ({len(duplicados)} entradas)", nivel="INFO")

    registro.registrar_exito("Proceso de deduplicación finalizado correctamente.")
