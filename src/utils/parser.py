from pybtex.database.input import bibtex
import re
from src.utils.registro import registro

def cargar_bibtex_seguro(ruta):
    """
    Carga un archivo .bib asegurando claves únicas.
    Si una clave se repite, se renombra automáticamente (ej: WANG2025 -> WANG2025_2).
    """
    with open(ruta, encoding="utf-8") as f:
        contenido = f.read()

    nuevo_contenido = []
    claves_vistas = {}

    for linea in contenido.splitlines():
        if linea.strip().startswith("@"):
            # Detectar cabecera: @article{WANG2025,
            m = re.match(r"(@\w+\{)([^,]+)(,)", linea)
            if m:
                prefijo, clave, sufijo = m.groups()
                if clave in claves_vistas:
                    claves_vistas[clave] += 1
                    clave_nueva = f"{clave}_{claves_vistas[clave]}"
                    registro.registrar(
                        f"Clave duplicada detectada: {clave} → renombrada como {clave_nueva}",
                        nivel="ADVERTENCIA"
                    )
                    clave = clave_nueva
                else:
                    claves_vistas[clave] = 1
                linea = f"{prefijo}{clave}{sufijo}"
        nuevo_contenido.append(linea)

    parser = bibtex.Parser()
    return parser.parse_string("\n".join(nuevo_contenido))
