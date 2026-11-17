# PROGRESS — estado y registro de litmar

Memoria viva del proyecto. Cómo se usa y cuándo se actualiza: `AGENTS.md`, §1.
«Estado actual» y «Próximos pasos» se reescriben para que siempre sean ciertos;
el registro solo crece (entradas nuevas arriba).

## Estado actual

_Actualizado: 2026-11-17._

- **`main`**: al día con `origin/main`. Último trabajo: harness de memoria
  (`AGENTS.md`, `PROGRESS.md`, `DECISIONS.md`, hooks) y diapositivas de la
  Clase 1 en `docs/`.
- **Curso**: Clase 1 (*Busca*) casi completa; siguiente, Clase 2 (*Lee*: LLM,
  LangGraph, agente). Ver `AGENTS.md` §2.
- **Tests**: 181 pasan, sin red, en menos de 1 s.
- **PRs abiertas**: ninguna.
- **Funciona**:
  - modelo `Articulo` y `Biblioteca` (dedup por DOI, BibTeX, CSV, JSON);
  - seis fuentes: OpenAlex, Crossref, Europe PMC, arXiv, PANGAEA, Zotero;
  - CLI `litmar buscar | exportar | ui` (la búsqueda por CLI solo usa OpenAlex);
  - interfaz web con Streamlit (`litmar ui`): búsqueda en varias fuentes, tabla
    y descargas BibTeX/CSV;
  - configuración por `.env` (plantilla en `.env.example`; todo opcional salvo
    Zotero).

## Próximos pasos

Por orden de prioridad sugerido; nada está empezado.

1. [ ] **CLI como en la demo de la Clase 1** (`docs/Clase1.pdf`, diapositiva 8):
   ```
   uv run litmar buscar "posidonia carbon" --fuente openalex,europepmc \
       --desde 2020 --bibtex refs.bib
   ```
   y salida en tabla `AÑO  CITAS  AUTORES  TÍTULO`. Falta: `--fuente` (varias,
   separadas por comas, reutilizando `configuracion.crear_fuente`; propuesto a
   @eloyleonorozco en la PR #10), `--desde` (filtrar por año), `--bibtex`
   directo en `buscar`, la tabla, y aceptar también `--n` (hoy solo `-n`).
2. [ ] **ruff** (lo enseña la Clase 1): añadirlo al grupo dev, configurarlo en
   `pyproject.toml`, dejar `ruff check` y `ruff format` en verde y mencionarlo en
   `AGENTS.md` §3 y el README.
3. [ ] **Preparar la Clase 2**: `GEMINI_API_KEY` en `.env.example` (las
   diapositivas lo piden para la clase siguiente). Las diapositivas usan también
   `LITMAR_EMAIL`; aquí la variable equivalente es `CROSSREF_MAILTO`: decidir si
   se renombra.
4. [ ] **Permisos del JSON**: `Biblioteca.guardar` deja `0600`; aplicar la umask
   con `os.chmod` antes de `os.replace`. Propuesto en la PR #10.
5. [ ] **Mover el helper `cliente` de `tests/test_fuentes.py` a `conftest.py`**,
   para que `test_pangaea.py` no importe de otro fichero de tests.
6. [ ] **`pyproject.toml`**: cambiar `description = "Add your description here"`.
7. [ ] **Ideas para la UI** (sin pedir aún): guardar/cargar la biblioteca JSON,
   filtrar u ordenar resultados, mostrar de qué fuente viene cada artículo.

## Pendiente de terceros

Mejoras pedidas a colaboradores en comentarios de PR. Si llega una PR, revisarla
contra esto.

- **arXiv** (@ddietor, comentario en #11): aplicar la pausa de 3 s también a los
  reintentos (`backoff=3.0`) y pasar los nombres a español.
- **Zotero** (@acanari, #12 cerrada por duplicada): se le invitó a aportar sus
  mejoras sobre la fuente existente: DOI desde el campo «Extra» y usar
  `/items/top`.
- **Throttle genérico** (@rsune8, #9 cerrada por duplicada): se le invitó a
  proponer su hook `_antes_de_peticion` en `Fuente`.

## Registro de sesiones

### 2026-11-17 — Sesión 1: del proyecto vacío a seis fuentes, CLI e interfaz web

Todo el proyecto se construyó en esta sesión (Roberto Bada con Claude Code).

- **Arranque**: proyecto uv con layout `src/` (`30725fa`) y push a
  `Sapere-IA/litmar`.
- **Modelo** (`0083af3`): `Articulo`, `Biblioteca` con BibTeX, clase abstracta
  `Fuente` con reintentos y fuente OpenAlex con test offline. El usuario pidió
  **atributos de clase en inglés** y el resto en español.
- **PRs de colaboradores**, revisadas y comentadas una a una:
  - aceptadas: #3 Crossref (@mattosnh), #6 PANGAEA (@pablo-icm), #4 Europe PMC
    (@aleixop), #7 Zotero (@PurpleFunkyBird), #11 arXiv (@ddietor), #10 CLI y
    persistencia JSON (@eloyleonorozco);
  - cerradas: #8, #9 (arXiv) y #12 (Zotero) por duplicadas, explicando el motivo
    e invitando a aportar sus mejoras (ver «Pendiente de terceros»); #8 además
    tenía un test que fallaba. #2 y #5 las cerró otra persona.
  - #10 tenía conflicto en el README: se fusionaron los dos y se añadió una
    sección por fuente.
- **Seguridad** (`d342dcd`, `621bae5`): `.claude/settings.json` bloquea leer
  `.env` y `.env.*` salvo `.env.example`. Hicieron falta varios intentos por las
  limitaciones de los globs (ver `AGENTS.md` §9).
- **Interfaz web** (`00411b7`, `fae30af`): `src/litmar/ui.py` con Streamlit
  (fuentes, número de resultados, tabla con enlace al DOI, descargas BibTeX y
  CSV), `litmar ui`, `configuracion.py`, `Biblioteca.a_csv()`, `.env.example`,
  carga de `.env` con python-dotenv. Estadísticas de uso de Streamlit
  desactivadas. Probada con búsqueda real en cinco fuentes (25 artículos).
- **Harness de memoria**: `AGENTS.md`, `CLAUDE.md`, `PROGRESS.md`,
  `DECISIONS.md` y hooks `SessionStart`/`Stop`. El usuario eligió: ficheros en el
  repo, el agente anota el progreso solo, y hooks además de instrucciones.
- **Diapositivas**: el usuario añadió `docs/Clase1.pdf` (Clase 1 del curso). De
  ellas salen el contexto del curso y la hoja de ruta de `AGENTS.md` §2, y los
  próximos pasos 1-3 (CLI de la demo, ruff, preparación de la Clase 2).
