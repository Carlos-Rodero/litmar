# DECISIONS — decisiones de diseño y de proceso

Por qué litmar es como es, para no volver a discutir lo ya decidido. Cada entrada:
fecha, decisión, motivo y alternativas descartadas. No se borran: si una decisión
cambia, se marca **Sustituida por D-N** y se añade la nueva al final.

---

### D-1 · uv, layout `src/` y `uv_build` — 2026-11-17
uv gestiona entorno, dependencias y lockfile con un solo comando y es mucho más
rápido que venv + pip. El layout `src/` evita importar por accidente el código
sin instalar. El proyecto sigue siendo instalable con `pip install .`.

### D-2 · Idioma: español, salvo atributos de clase en inglés — 2026-11-17
Petición del usuario. Clases, métodos, funciones, variables, docstrings y
mensajes en español; atributos (`title`, `authors`, `max_retries`…) en inglés.
Commits en inglés.

### D-3 · El DOI es la identidad de un artículo — 2026-11-17
`Articulo` exige DOI (normalizado) y al menos un autor; `Biblioteca` deduplica
por DOI y conserva el primero. Las fuentes descartan lo que no cumpla. Así la
deduplicación entre fuentes es trivial y fiable. Descartado: deduplicar por
título (frágil) o permitir artículos sin DOI.

### D-4 · Reintentos en la clase base `Fuente` — 2026-11-17
Todas las fuentes comparten la misma política: reintento ante errores de red,
429 y 5xx, espera exponencial, `Retry-After` y `max_wait` para no esperar horas
cuando se agota un cupo diario. `sleep` y `client` son inyectables para tests.

### D-5 · Tests sin red con respuestas reales guardadas — 2026-11-17
`httpx.MockTransport` + JSON/XML reales en `tests/datos/`. Los tests son
deterministas, rápidos y no gastan cupo de las APIs.

### D-6 · Una fuente por servicio; ante PRs duplicadas se elige una — 2026-11-17
Con varias PRs para el mismo servicio se acepta la más completa y correcta, y se
cierran las demás con un comentario que explica el motivo e invita a aportar sus
mejoras sobre la elegida. Las PRs se integran desde local con un commit «Merge
pull request #N from usuario/rama» y push a `main`; GitHub las marca MERGED.

### D-7 · `.env` bloqueado para el agente — 2026-11-17
Reglas `deny` de `Read` en `.claude/settings.json` para `.env` y `.env.*`, con
excepción de `.env.example` construida con rangos de caracteres (los globs no
admiten negación). Las reglas no cubren Bash: el agente tampoco usa `cat` con él.

### D-8 · Configuración por variables de entorno y `.env` — 2026-11-17
Claves y datos de fuentes en variables (`OPENALEX_API_KEY`, `CROSSREF_MAILTO`,
`ZOTERO_*`), cargadas desde `.env` con python-dotenv **solo en la entrada del
comando `litmar`** (para que los tests no lean el `.env` real). Las variables ya
definidas tienen prioridad. `configuracion.py` es el único sitio que traduce
variables en fuentes. Descartado: `uv run --env-file` (no sirve con pip).

### D-9 · Streamlit como dependencia opcional (`ui`) — 2026-11-17
Streamlit arrastra pandas, pyarrow y más; quien use la librería o la CLI no lo
necesita. Se instala con `uv sync --extra ui` o `pip install 'litmar[ui]'`, y
está también en el grupo dev. `litmar ui` lanza `streamlit run` con el mismo
intérprete, reenvía las opciones extra y desactiva las estadísticas de uso.

### D-10 · Memoria del proyecto en el repositorio — 2026-11-17
`AGENTS.md` (estable), `PROGRESS.md` (vivo) y `DECISIONS.md` (este), versionados
en git y compartidos con los colaboradores. El agente actualiza `PROGRESS.md` por
su cuenta al terminar cada tarea, y los hooks de Claude Code inyectan el estado
al empezar y recuerdan anotar al terminar. Descartado: memoria privada del
agente (no la ven otros agentes ni personas, y se pierde al cambiar de máquina).

### D-11 · `desde` como parámetro de `Fuente.buscar`, filtrado en la API y en local — 2026-11-17
Para `litmar buscar --desde AÑO` (demo de la Clase 1). Cada fuente pasa el año a
su API (comprobado contra las APIs reales) y además descarta con `_admite` lo
anterior, porque cada API fecha distinto (arXiv usa la primera versión; Zotero
no filtra). Descartado: filtrar solo los resultados ya descargados, porque con
`-n 5` podrían quedar menos de 5.

### D-12 · Búsqueda multifuente compartida en `busqueda.py` — 2026-11-17
CLI y UI usan `buscar_en_fuentes`: si una fuente falla se sigue con las demás y
se devuelven los errores (sin cabeceras ni peticiones). En la CLI, si fallan
todas es un error (código 1, no se guarda nada); si falla alguna, solo un aviso.

### D-13 · ruff con línea de 100 y reglas E, W, F, I, UP, B — 2026-11-17
Lo enseña la Clase 1. 100 en lugar de 88 porque el código ya estaba escrito así y
evita partir líneas sin ganar legibilidad. Al adoptarlo se formateó todo el
proyecto de una vez, en el mismo commit que `--fuente`/`--desde`.

### D-14 · Variables del LLM: `LITMAR_MODELO` + clave del proveedor; se mantiene `CROSSREF_MAILTO` — 2026-11-17
Lo fijan las diapositivas de la Clase 2: `LITMAR_MODELO=proveedor:modelo` (p. ej.
`google_genai:gemini-3.8-flash` o `anthropic:claude-sonnet-5-5`) y la clave con
el nombre estándar de cada proveedor (`GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`),
que es el que leen las librerías de LangChain. Sustituye a la idea de
`GEMINI_API_KEY` de la Clase 1. Las diapositivas también nombran
`CROSSREF_MAILTO`, así que no se renombra a `LITMAR_EMAIL`.

### D-15 · LangChain y los dos proveedores como dependencias normales — 2026-11-18
`langchain` (por `init_chat_model`), `langchain-core`, `langchain-google-genai`
y `langchain-anthropic` van en `dependencies`, no en un extra opcional como
Streamlit (D-9): resumir y revisar son el centro de la Clase 2 y los alumnos
deben poder usar Gemini o Claude tras `uv sync`, sin pasos extra. Otro proveedor
se añade con `uv add langchain-<proveedor>` y su variable de clave en
`llm._CLAVES` (si no está, `crear_modelo` deja que LangChain lo compruebe).

### D-16 · Límite de llamadas por minuto en el modelo, configurable — 2026-11-18
`crear_modelo()` pasa un `InMemoryRateLimiter` de LangChain a `init_chat_model`:
10 llamadas por minuto por defecto (plan gratuito de Gemini), cambiable con
`LITMAR_LLAMADAS_POR_MINUTO` (0 = sin límite, p. ej. con una clave de pago).
`max_bucket_size=1` espacia las llamadas en vez de permitir ráfagas. La clave se
comprueba antes de crear el modelo para dar un error que diga qué línea añadir
al `.env`. Como D-8, `llm.py` lee el entorno y no carga `.env`: lo hace el
comando `litmar`; los scripts propios llaman a `load_dotenv()`.

### D-17 · Flujo de revisión: «los N mejores» son los más citados — 2026-11-18
`filtrar` se queda con los artículos con resumen y los ordena por citas. Es
fácil de explicar y de comprobar, aunque favorece lo antiguo (en la prueba real
entraron revisiones generales sobre olas de calor). Cambiar el criterio es el
ejercicio natural de la Práctica 2. Descartado de momento: por año, o el orden de
relevancia de cada API. Lo eligió el usuario.

### D-18 · Citas inventadas tras agotar las reescrituras: se marcan — 2026-11-18
Tras `MAX_REESCRITURAS` (2), `verificar_citas` sustituye cada DOI que no está
entre los resumidos por «[cita no verificada]» y añade un aviso. Así ningún DOI
sin comprobar llega al informe ni al BibTeX. Descartado: guardar el informe tal
cual con un aviso, o fallar sin guardar nada. «Seleccionados» son los artículos
que el modelo vio (los resumidos), no todos los que pasaron `filtrar`. Las
referencias del informe las genera el código a partir de los DOI verificados.
Lo eligió el usuario. Los campos del estado (`EstadoRevision`) van en inglés por
D-2, aunque la diapositiva diga «pregunta, artículos…».

### D-19 · Cada revisión, en su carpeta de `ejemplos/revisiones/`, fuera de git — 2026-11-18
Petición del usuario: las salidas de `litmar revisar` no se mezclan en el
directorio de trabajo. Cada ejecución crea
`ejemplos/revisiones/AAAA-MM-DD_HHMM_<pregunta-sin-acentos>/` con `revision.md`
y `revision.bib` (nombre recortado a 50 caracteres sin partir palabras; si ya
existe, `-2`, `-3`…). La carpeta se crea al final, para que una revisión que
falla no deje carpetas vacías. `ejemplos/revisiones/` va en `.gitignore`: cada
alumno tiene las suyas y no aparecen en sus PRs (una de muestra se puede añadir
con `git add -f`). `--informe` y `--bibtex` siguen permitiendo otra ruta. La
ruta es relativa al directorio desde el que se ejecuta `litmar`. Descartado:
nombrar solo por pregunta (se pisan) o solo por fecha (no dice de qué trata).
