# src/utils/parser.py  (reemplaza la función existente por esto)
import re
from pybtex.database.input import bibtex
from pybtex.database import BibliographyData
from src.utils.registro import registro
from src.utils.limpiador import limpiar_keywords_bibtex


def cargar_bibtex_seguro(ruta):
    """
    Carga un archivo .bib asegurando claves únicas.
    - Limpia keywords problemáticos (llaves internas).
    - Renombra claves duplicadas dentro del archivo (KEY -> KEY_2, etc.).
    - Si el parse completo falla, intenta un fallback: extraer entradas por balance de llaves
      y parsearlas una a una, construyendo un BibliographyData combinado.
    Devuelve un objeto BibliographyData.
    """
    registro.registrar(f"Iniciando carga segura de BibTeX: {ruta}", nivel="INFO")

    # 1) limpiar keywords problemáticos en el archivo (sobrescribe)
    try:
        limpiar_keywords_bibtex(ruta)
    except Exception as e:
        registro.registrar(f"No se pudo ejecutar limpiar_keywords_bibtex: {e}", nivel="ADVERTENCIA")

    # 2) leer contenido
    try:
        with open(ruta, encoding="utf-8") as f:
            contenido = f.read()
    except Exception as e:
        registro.registrar(f"Error leyendo {ruta}: {e}", nivel="ERROR")
        raise

    # 3) renombrar claves duplicadas detectando cabeceras @type{KEY,
    #    patrón robusto: captura prefijo, clave y la coma
    pattern = re.compile(r'(@\w+\s*\{\s*)([^,\s\}]+)(\s*,)', flags=re.IGNORECASE)

    claves_vistas = {}

    def repl_renombrar(m):
        prefijo, clave, coma = m.group(1), m.group(2), m.group(3)
        if clave in claves_vistas:
            claves_vistas[clave] += 1
            nueva = f"{clave}_{claves_vistas[clave]}"
            registro.registrar(f"Clave duplicada detectada en {ruta}: {clave} → renombrada como {nueva}", nivel="ADVERTENCIA")
        else:
            claves_vistas[clave] = 1
            nueva = clave
        return f"{prefijo}{nueva}{coma}"

    contenido_renombrado = pattern.sub(repl_renombrar, contenido)

    parser = bibtex.Parser()

    # 4) intento parse completo (rápido). Si falla, iremos a fallback por entradas individuales.
    try:
        bib = parser.parse_string(contenido_renombrado)
        registro.registrar(f"Parse exitoso (completo) de {ruta} con {len(bib.entries)} entradas.", nivel="EXITO")
        return bib
    except Exception as e:
        registro.registrar(f"Parse completo FALLÓ para {ruta}: {e}. Intentando fallback por entradas individuales...", nivel="ADVERTENCIA")

    # ---------- Fallback: extraer entradas por balance de llaves y parsear individualmente ----------
    def extraer_entradas_por_balance(text):
        entradas = []
        entry_start_re = re.compile(r'@\w+\s*\{', flags=re.IGNORECASE)
        pos = 0
        length = len(text)
        while True:
            m = entry_start_re.search(text, pos)
            if not m:
                break
            start = m.start()
            # Encontrar la primer '{' a partir de start
            brace_idx = text.find('{', start)
            if brace_idx == -1:
                break
            i = brace_idx
            depth = 0
            while i < length:
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        entradas.append(text[start:i+1])
                        pos = i + 1
                        break
                i += 1
            else:
                # no encontró cierre: tomar desde start hasta el final
                entradas.append(text[start:])
                break
        return entradas

    entradas = extraer_entradas_por_balance(contenido_renombrado)
    registro.registrar(f"Fallback: se detectaron {len(entradas)} entradas para parsear individualmente.", nivel="INFO")

    combinado = BibliographyData()
    claves_globales = {}

    for idx, ent_text in enumerate(entradas, start=1):
        try:
            parsed = parser.parse_string(ent_text)
        except Exception as e:
            registro.registrar(f"  [ADVERTENCIA] No se pudo parsear entrada #{idx} individualmente: {e}. Se omite.", nivel="ADVERTENCIA")
            continue

        for k, e_entry in parsed.entries.items():
            if k in combinado.entries:
                # renombrar con contador global para evitar exception en add_entry
                claves_globales[k] = claves_globales.get(k, 1) + 1
                new_k = f"{k}_{claves_globales[k]}"
                registro.registrar(f"  [INFO] Clave {k} ya existe en combinado -> renombrada a {new_k}", nivel="ADVERTENCIA")
            else:
                claves_globales.setdefault(k, 1)
                new_k = k
            combinado.add_entry(new_k, e_entry)

    registro.registrar(f"Fallback completado: combinado contiene {len(combinado.entries)} entradas.", nivel="INFO")
    return combinado
