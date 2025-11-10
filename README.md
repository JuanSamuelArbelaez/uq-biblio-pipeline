# UQ-Biblio Pipeline  
Análisis, Similitud y Agrupamiento de Artículos Científicos

## Descripción General

**UQ-Biblio Pipeline** es una aplicación web de análisis bibliométrico que permite automatizar la descarga, comparación y agrupamiento de artículos científicos.  
Fue desarrollada con **Flask** (backend) y un **dashboard web dinámico** en **HTML, CSS y JavaScript** (frontend).

El sistema integra varios módulos de procesamiento de datos científicos, desde la recolección automática hasta el análisis de similitud y agrupamiento temático mediante algoritmos de inteligencia artificial.

## Información del Proyecto

**Programa:** Ingeniería de Sistemas y Computación  
**Asignatura:** Análisis de Algoritmos  
**Profesor:** Sergio Augusto Cardona Torres  
**Autores:** Julián A. Ladino Moreno y Juan S. Arbelaez  
**Repositorio GitHub:** [https://github.com/JuanSamuelArbelaez/uq-biblio-pipeline](https://github.com/JuanSamuelArbelaez/uq-biblio-pipeline)  
**Despliegue:** [https://opulent-happiness-jv466px6rg4c9v9-5000.app.github.dev/](https://opulent-happiness-jv466px6rg4c9v9-5000.app.github.dev/) *(desactivado temporalmente, activo durante sustentación y revisión)*

## Requerimientos Funcionales

| Requerimiento | Descripción |
|----------------|-------------|
| **1. Scraping de datos** | Descarga automática de artículos desde ACM y ScienceDirect. |
| **2. Similitud textual** | Implementa seis algoritmos de similitud entre abstracts. |
| **3. Análisis de keywords** | Vectorización TF-IDF y generación de nube de palabras. |
| **4. Agrupamiento jerárquico** | Clustering jerárquico con tres algoritmos y visualización con dendrogramas. |
| **5. Dashboard y despliegue web** | Interfaz interactiva para consulta, comparación y análisis visual. |
| **6. Documentación técnica y despliegue** | Este documento. Explica la arquitectura, dependencias y uso del sistema. |

## Arquitectura del Sistema

El sistema está organizado bajo una arquitectura **cliente-servidor**, con el siguiente esquema:

```
uq-biblio-pipeline/
│
├── app/                     # Aplicación web principal
│   ├── app.py               # Servidor Flask (backend principal)
│   ├── templates/
│   │   └── index.html       # Interfaz principal (dashboard)
│   └── static/
│       ├── css/
│       │   └── styles.css   # Estilos visuales del dashboard
│       └── js/
│           └── script.js    # Lógica e interacción del frontend
│
├── src/                     # Módulos funcionales
│   ├── datos/               # Archivos CSV, gráficos y resultados
│   ├── downloaders/         # Descargadores de artículos (ACM, ScienceDirect)
│   ├── utils/               # Funciones y analizadores principales
│   └── follow-ups/          # Experimentos y visualizaciones adicionales
│
└── requirements.txt         # Dependencias del proyecto
```

## Módulos Principales

| Requerimiento | Archivo | Descripción |
|----------------|----------|-------------|
| **1. Scraping de datos** | `src/downloaders/descargador_acm.py`, `descargador_sciencedirect.py` | Obtención y normalización de metadatos de artículos. |
| **2. Similitud textual** | `src/utils/compare_articles.py` | Implementa seis algoritmos de similitud (Levenshtein, Jaccard, Dice, TF-IDF, SBERT). |
| **3. Análisis de keywords** | `src/utils/keywords_analizer.py` | Procesamiento de keywords mediante TF-IDF y generación de nube de palabras. |
| **4. Agrupamiento jerárquico** | `src/utils/agrupamiento/ejecutar_todo.py` | Aplica algoritmos jerárquicos: single, complete y average linkage; genera dendrogramas. |
| **5. Despliegue web** | `app/app.py`, `app/static/js/script.js`, `app/templates/index.html` | Flask gestiona las rutas, API REST y el renderizado del dashboard web. |
| **6. Documentación técnica** | `README.md` | Descripción de arquitectura, instalación y uso. |

## Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/JuanSamuelArbelaez/uq-biblio-pipeline.git
cd uq-biblio-pipeline
```

### 2. Crear y activar entorno virtual
En Windows PowerShell:
```bash
python -m venv .venv
.venv\Scripts\activate
```

En Linux/Mac:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
Desde el directorio raíz del proyecto:
```bash
python3 app/app.py
```

Luego abrir en el navegador:
```
http://localhost:5000
```

## Interfaz Web

La aplicación web cuenta con secciones interactivas en `index.html`:

| Sección | Descripción |
|----------|--------------|
| **Descargar BibTeX** | Informa sobre los archivos descargados disponibles. |
| **Autores y Keywords** | Muestra el gráfico de los top 15 autores y las nubes de palabras clave. |
| **Artículos disponibles** | Lista paginada de artículos descargados, con opción de selección múltiple. |
| **Artículos seleccionados** | Muestra los abstracts de los artículos elegidos. |
| **Resultados de similitud** | Ejecuta y visualiza matrices de similitud con los algoritmos implementados. |

## Visualizaciones Disponibles

Las visualizaciones se generan automáticamente a partir de los módulos de análisis.

**Ubicaciones:**
```
src/datos/graphs/location/location_bibtex.png
src/datos/graphs/timeline/timeline_areas_bibtex.png
src/datos/graphs/wordcloud/wordcloud.png
src/follow-ups/follow-up2/outputs/citation_graph_connected.png
src/follow-ups/follow-up2/outputs/cooccurrence_graph.png
src/follow-ups/follow-up3/outputs/dendrogram_*.png
```

Todas las imágenes se integran como pestañas dinámicas en la interfaz principal.

## Procesamiento y Análisis

1. **Preprocesamiento de texto:** limpieza, tokenización, eliminación de stopwords y vectorización TF-IDF.  
2. **Similitud:** cálculo de distancias entre abstracts mediante diferentes algoritmos.  
3. **Agrupamiento jerárquico:** clustering con métodos *single*, *complete* y *average linkage*.  
4. **Visualización:** gráficos comparativos, nubes de palabras, dendrogramas y redes de co-ocurrencia.

## Tecnologías Utilizadas

| Tipo | Herramientas |
|------|----------------|
| **Lenguaje base** | Python 3.11 |
| **Framework web** | Flask |
| **Frontend** | HTML5, CSS3, JavaScript (ES6) |
| **Gráficos** | Chart.js, Matplotlib |
| **Análisis de texto** | scikit-learn, NLTK, pandas, NumPy |
| **Clustering jerárquico** | SciPy (`linkage`, `dendrogram`) |
| **Embeddings (Similitud IA)** | SentenceTransformers (SBERT) |

## API REST

Las rutas principales expuestas por Flask son:

| Ruta | Método | Descripción |
|------|---------|-------------|
| `/` | GET | Carga la interfaz principal. |
| `/api/articulos` | GET | Devuelve los artículos disponibles. |
| `/api/top_autores` | GET | Retorna los 15 autores más frecuentes. |
| `/api/analisis` | POST | Ejecuta los algoritmos de similitud entre artículos seleccionados. |
| `/api/keywords_image` | GET | Devuelve la imagen de la nube de palabras. |
| `/api/graficas` | GET | Retorna rutas a las imágenes de análisis y dendrogramas. |

## Flujo de Uso

1. El usuario abre la aplicación web (vía Flask).  
2. Se cargan automáticamente los artículos disponibles (`/api/articulos`).  
3. El usuario selecciona los artículos de interés.  
4. Se ejecutan los análisis de similitud (`/api/analisis`).  
5. Los resultados y gráficos se muestran dinámicamente en la interfaz.  

## Despliegue en GitHub Codespaces

El proyecto fue desplegado mediante **GitHub Codespaces**, lo que permite su ejecución remota sin configuración local adicional.  
Actualmente el servicio se encuentra **desactivado temporalmente**, pero será **habilitado durante la sustentación y revisión** para demostración completa.

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**, permitiendo su uso y modificación con fines académicos y de investigación.
