# Litmar

Herramienta Python para reunir bibliografía científica: busca artículos en
OpenAlex, conserva una biblioteca local sin duplicados por DOI y exporta
referencias a BibTeX.

## Instalación

Requiere Python 3.12 o posterior y `uv`.

```powershell
uv sync
uv run litmar --help
```

## Buscar, guardar y exportar

```powershell
# Consultar hasta 30 artículos y guardar todos sus metadatos
uv run litmar buscar "machine learning" -n 30 --guardar biblioteca.json

# Ampliar la misma biblioteca con otra búsqueda
uv run litmar buscar "deep learning" -n 20 --guardar biblioteca.json

# Generar referencias para LaTeX u otras herramientas compatibles
uv run litmar exportar biblioteca.json --bibtex referencias.bib
```

Si el JSON ya existe, los resultados se combinan con los artículos guardados.
Los DOI se normalizan y, ante duplicados, se conserva el artículo original.
El guardado reemplaza el archivo de forma atómica. Un JSON inválido se rechaza
sin sobrescribirlo.

Sin `--guardar`, la búsqueda muestra las citas, los títulos y los enlaces DOI
en la terminal. `-n` indica el máximo de artículos válidos: pueden obtenerse menos
si no hay suficientes resultados con los datos requeridos. Las obras sin DOI,
título, año o autores se descartan.

La conexión utiliza los reintentos HTTP de la fuente OpenAlex. Puedes configurar
una clave mediante la variable de entorno `OPENALEX_API_KEY`; se envía en la
cabecera de autorización.

```powershell
$env:OPENALEX_API_KEY = "tu-clave"
uv run litmar buscar "bibliometrics" -n 5
```

También puedes ejecutar la CLI con `uv run python -m litmar`.
Los errores operativos devuelven código de salida 1 y los argumentos inválidos, 2.
La exportación reemplaza el archivo BibTeX de destino si existe.

## Uso desde Python

```python
from litmar import Biblioteca
from litmar.fuentes import OpenAlex

with OpenAlex() as fuente:
    biblioteca = Biblioteca(fuente.buscar("bibliometrics", n=10))

biblioteca.guardar("biblioteca.json")
recuperada = Biblioteca.cargar("biblioteca.json")
recuperada.exportar_bibtex("referencias.bib")
```

El JSON contiene una lista de artículos con `title`, `authors`, `year`, `doi`,
`journal`, `abstract` y `citations`. Se conservan los caracteres Unicode y el
orden de inserción. `abstract` y `citations` son opcionales al cargar y toman
los valores `""` y `0`.

## Tests

```powershell
uv run pytest
```

Los tests usan respuestas HTTP simuladas y una respuesta guardada de OpenAlex;
no necesitan conexión a la API ni una clave. Cubren los modelos, la deduplicación,
los reintentos, la persistencia y el flujo de la CLI hasta la exportación BibTeX.
