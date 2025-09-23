import re
from src.utils.registro import registro

def limpiar_keywords_bibtex(ruta_archivo: str) -> None:
    """
    Reescribe el archivo BibTeX reemplazando llaves '{' y '}' dentro del campo keywords.
    """
    registro.registrar(f"Limpieza de keywords iniciada en: {ruta_archivo}", nivel="INFO")
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    def limpiar_keywords(match):
        texto = match.group(1)
        texto_limpio = texto.replace("{", "").replace("}", "")
        return f"keywords = {{{texto_limpio}}}"

    contenido_limpio = re.sub(r"keywords\s*=\s*\{(.*?)\}", limpiar_keywords, contenido, flags=re.DOTALL)

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(contenido_limpio)
    registro.registrar(f"Limpieza de keywords completada: {ruta_archivo}", nivel="EXITO")
