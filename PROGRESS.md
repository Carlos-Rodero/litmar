# PROGRESS — estado y registro de litmar

Memoria viva del proyecto. Cómo se usa y cuándo se actualiza: `AGENTS.md`, §1.
«Estado actual» y «Próximos pasos» se reescriben para que siempre sean ciertos;
el registro solo crece (entradas nuevas arriba).

## Estado actual

_Actualizado: 2026-11-17._

- **`main`**: al día con `origin/main`. Último trabajo: la CLI de la demo de la
  Clase 1 (`--fuente`, `--desde`, `--bibtex`, tabla) y ruff.
- **Curso**: Clase 1 (*Busca*, 17/11/2026) completa respecto a las
  diapositivas. La siguiente es la Clase 2 (*Lee*: LLM con Gemini, LangGraph,
  agente), prevista para el **18/11/2026**; aún no hay diapositivas suyas en
  `docs/`. Ver `AGENTS.md` §2.
- **Calidad**: 204 tests pasan, sin red, en menos de 1 s; `ruff check` y
  `ruff format --check` en verde.
- **PRs abiertas**: ninguna.
- **Funciona**:
  - modelo `Articulo` y `Biblioteca` (dedup por DOI, BibTeX, CSV, JSON);
  - seis fuentes: OpenAlex, Crossref, Europe PMC, arXiv, PANGAEA, Zotero; todas
    admiten `desde` (año mínimo);
  - CLI: `litmar buscar "…" --fuente openalex,europepmc --desde 2020 --bibtex
    refs.bib --guardar biblioteca.json`, con salida en tabla; `litmar exportar`;
    `litmar ui`;
  - interfaz web con Streamlit: búsqueda en varias fuentes, tabla y descargas
    BibTeX/CSV;
  - configuración por `.env` (plantilla en `.env.example`; todo opcional salvo
    Zotero).

## Próximos pasos

Por orden de prioridad sugerido; nada está empezado.

0. [ ] **Comprobar el arnés de memoria al abrir la sesión**. Los hooks se
   crearon en la sesión 1 y aún no se han probado en una sesión real. Si al
   empezar no llegó el bloque «Memoria del proyecto (hook SessionStart…)»,
   revisar con `/hooks` que `.claude/settings.json` los carga, y anotar el
   resultado aquí.
1. [ ] **Preparar la Clase 2**: `GEMINI_API_KEY` en `.env.example` (las
   diapositivas lo piden para la clase siguiente). Las diapositivas usan también
   `LITMAR_EMAIL`; aquí la variable equivalente es `CROSSREF_MAILTO`: **el
   usuario debe decidir** si se renombra. Cuando lleguen las diapositivas de la
   Clase 2, leerlas y planificar con el usuario (resúmenes con LLM, LangGraph,
   agente) antes de escribir código.
2. [ ] **Permisos del JSON**: `Biblioteca.guardar` deja `0600`; aplicar la umask
   con `os.chmod` antes de `os.replace`. Propuesto en la PR #10.
3. [ ] **Mover el helper `cliente` de `tests/test_fuentes.py` a `conftest.py`**,
   para que `test_pangaea.py` no importe de otro fichero de tests.
4. [ ] **`pyproject.toml`**: cambiar `description = "Add your description here"`.
5. [ ] **«Desde el año» en la UI**: `buscar_en_fuentes` ya admite `desde`; falta
   el campo en `ui.py`.
6. [ ] **Ideas para la UI** (sin pedir aún): guardar/cargar la biblioteca JSON,
   filtrar u ordenar resultados, mostrar de qué fuente viene cada artículo.

## Cabos sueltos

- **Memoria privada del agente duplicada**: en la máquina del usuario queda
  `~/.claude/projects/-Users-presindev-dev-scratch-litmar/memory/atributos-en-ingles.md`
  (y su línea en `MEMORY.md` de esa carpeta) con la convención de atributos en
  inglés, que ya está en `AGENTS.md` §7. El sistema de permisos impidió borrarla;
  puede borrarla el usuario. No molesta, pero no hay que mantenerla.
- **El PDF de `docs/` incluye el correo y el LinkedIn del usuario** (portada y
  cierre); el repositorio es público. El usuario lo subió a sabiendas.

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

### 2026-11-17 — Sesión 1 (cierre): memoria lista para la siguiente sesión

- Repaso completo de los ficheros de memoria para que una sesión con contexto
  vacío pueda retomar: calendario del curso (`AGENTS.md` §2), cómo trabaja el
  usuario (§10), procedimiento para revisar PRs de alumnos (§11), acciones que
  bloquea el sistema de permisos (§9), «Cabos sueltos» y el paso 0 (comprobar los
  hooks) en este fichero.
- Estado al cerrar: `main` sincronizado con `origin/main`, árbol limpio, 204
  tests y ruff en verde, ninguna PR abierta.

### 2026-11-17 — Sesión 1 (cont.): CLI de la demo y ruff

- **CLI como en la diapositiva 8 de `docs/Clase1.pdf`**: `--fuente` (varias,
  separadas por comas, sin distinguir mayúsculas), `--desde AÑO`, `--bibtex` en
  `buscar`, `--n` además de `-n`, y salida en tabla `AÑO CITAS AUTORES TÍTULO`
  ajustada a la terminal (ya no imprime los DOI: van en BibTeX/JSON). Era lo que
  se propuso a @eloyleonorozco en la PR #10; lo hizo el mantenedor.
- **`desde` en las seis fuentes** (D-11): filtros comprobados contra las APIs
  reales. Nuevo `tests/test_desde.py`.
- **`busqueda.py`** (D-12): la búsqueda multifuente que tenía `ui.py` pasa a un
  módulo compartido; la CLI y la UI lo usan. `Articulo.short_authors` nuevo.
  Zotero sin configurar da un error que explica qué variable falta.
- **ruff** (D-13): grupo dev, configuración en `pyproject.toml`, todo el
  proyecto formateado y en verde.
- Probado de verdad: la búsqueda de la demo devuelve los mismos artículos que la
  diapositiva; `--fuente openalex,europepmc --desde 2020 --bibtex` exporta 20.
- Ruido en el diff: el formateo de ruff toca casi todos los ficheros de
  colaboradores. Si alguien tiene una PR abierta contra el `main` anterior, puede
  tener conflictos de formato: que haga `uv run ruff format` tras actualizar.

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
