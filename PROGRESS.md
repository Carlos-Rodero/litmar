# PROGRESS — estado y registro de litmar

Memoria viva del proyecto. Cómo se usa y cuándo se actualiza: `AGENTS.md`, §1.
«Estado actual» y «Próximos pasos» se reescriben para que siempre sean ciertos;
el registro solo crece (entradas nuevas arriba).

## Estado actual

_Actualizado: 2026-11-18._

- **`main`**: al día con `origin/main`. Último trabajo: las herramientas
  `buscar_articulos` y `listar_fuentes` (paso 6, ver registro).
- **Curso**: Clase 1 (*Busca*, 17/11/2026) completa respecto a las
  diapositivas. La siguiente es la Clase 2 (*Lee*), el **18/11/2026**; sus
  diapositivas están en `docs/Clase2.pdf` y su plan, abajo. Se está
  construyendo como ensayo, encargo a encargo: hechos los pasos 1 a 6 (`.env.example`, `resumir`, `llm.py`, Práctica 1,
  flujo LangGraph, herramientas), probados con un modelo real (Anthropic).
- **Calidad**: 273 tests pasan, sin red, en ~1,5 s; `ruff check` y
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
  - `resumir(articulo, pregunta, modelo)` → `ResumenArticulo` (Pydantic,
    `with_structured_output`), en `src/litmar/resumen.py`;
  - `crear_modelo()` en `src/litmar/llm.py`: modelo de `LITMAR_MODELO` con
    `init_chat_model`, límite de llamadas por minuto y errores claros;
  - `litmar revisar "pregunta"`: flujo LangGraph de seis pasos
    (`src/litmar/flujo.py`) con verificación de citas por código; guarda
    `revision.md` y `revision.bib` (solo lo citado) en
    `ejemplos/revisiones/<fecha_hora_pregunta>/` (ignorado en git);
  - herramientas de LangChain `buscar_articulos` y `listar_fuentes`
    (`src/litmar/herramientas.py`), listas para el agente;
  - configuración por `.env` (plantilla en `.env.example`; todo opcional salvo
    Zotero).

## Próximos pasos

Por orden de prioridad sugerido; nada está empezado.

0. [ ] **Comprobar el arnés de memoria**. `SessionStart` **funciona**: el
   18/11/2026, al reanudar la sesión, inyectó el estado de este fichero y de git.
   Falta ver en una sesión real que `Stop` pide anotar el progreso cuando hay
   trabajo sin registrar (los casos se probaron a mano con un repo de prueba).
1. [ ] **Clase 2**: seguir el «Plan de la Clase 2» (abajo). El usuario lanza
   los prompts de las diapositivas uno a uno (ensayo). Siguiente: la
   votación de clase (paso 7) y el agente con Deep Agents (paso 8). Pendiente: probar con Gemini (solo se ha probado con
   Anthropic). Ojo: con el límite por defecto la primera llamada espera ~6 s (el
   limitador empieza vacío).
2. [ ] **Permisos del JSON**: `Biblioteca.guardar` deja `0600`; aplicar la umask
   con `os.chmod` antes de `os.replace`. Propuesto en la PR #10.
3. [ ] **Mover el helper `cliente` de `tests/test_fuentes.py` a `conftest.py`**,
   para que `test_pangaea.py` no importe de otro fichero de tests.
4. [ ] **`pyproject.toml`**: cambiar `description = "Add your description here"`.
5. [ ] **«Desde el año» en la UI**: `buscar_en_fuentes` ya admite `desde`; falta
   el campo en `ui.py`.
6. [ ] **Ideas para la UI** (sin pedir aún): guardar/cargar la biblioteca JSON,
   filtrar u ordenar resultados, mostrar de qué fuente viene cada artículo.

## Plan de la Clase 2 (de `docs/Clase2.pdf`)

Los encargos que se lanzan «en directo», en orden. Cada uno trae en la
diapositiva una columna «En qué fijarse»: el resultado debe superarla. Consultar
la documentación actual de LangChain, LangGraph y deepagents antes de programar
(cambian rápido) y proponer plan antes de código.

1. [x] **`.env`** (diapositiva 4; en `.env.example` el 18/11): `LITMAR_MODELO=google_genai:gemini-3.8-flash`
   + `GOOGLE_API_KEY`, o `anthropic:claude-sonnet-5-5` + `ANTHROPIC_API_KEY`. El
   plan gratuito de Gemini tiene límites por minuto (429) y Google puede usar lo
   enviado: solo datos públicos.
2. [x] **Resumen estructurado** (18/11, `resumen.py`; probar con modelo real): `resumir(articulo, pregunta, modelo)` → objeto
   Pydantic `ResumenArticulo` (objetivo, método, hallazgos, relevancia 1-5
   respecto a la pregunta, limitaciones) con `with_structured_output`. Cada
   campo con descripción (el modelo la lee). Sin resumen → no llamar al modelo.
   Test con modelo falso, sin clave ni red.
3. [x] **Modelo intercambiable** (18/11, `llm.py`): `src/litmar/llm.py` con `crear_modelo()` que lee
   `LITMAR_MODELO` y usa `init_chat_model`; límite de llamadas por minuto para el
   plan gratuito; si falta la clave, error claro que diga qué poner en el `.env`.
   Ningún nombre de modelo ni clave en el código; cambiar de modelo = cambiar el
   `.env`.
4. [x] **Práctica 1** (18/11) de los alumnos: `ejemplos/resumir.py` (busca 3 artículos y
   los resume). Puede convenir tenerlo hecho como referencia.
5. [x] **Flujo LangGraph** (18/11; D-17, D-18) (`src/litmar/flujo.py`): estado `TypedDict`
   (`EstadoRevision`: pregunta, artículos, resúmenes, informe…); nodos
   `planificar` (LLM: pregunta → 2-3 búsquedas), `buscar` y `filtrar` (código:
   fuentes y Biblioteca; con resumen, sin duplicados, los N mejores),
   `resumir_articulos` (con `resumir()`), `sintetizar` (LLM, cita por DOI) y
   `verificar_citas` (código: cada DOI citado está entre los seleccionados; si
   no, vuelve a `sintetizar`, máximo 2 veces). Comando `litmar revisar
   "pregunta" --modo flujo` que muestra cada paso (ver demo, diapositiva 21) y
   guarda el informe y el BibTeX de lo citado. Primero plan y diagrama Mermaid.
6. [x] **Herramientas** (18/11, D-20) (`src/litmar/herramientas.py`): `buscar_articulos(consulta,
   fuente, n)` (reutiliza `crear_fuente`) y `listar_fuentes` (usa
   `fuentes_disponibles`), con `@tool` de LangChain. Máximo 10 en el código;
   errores como mensaje; devuelven título, año, DOI, citas y resumen recortado;
   docstrings pensados para el modelo; avisar de que PANGAEA da datos, no
   artículos. Tests sin red.
7. [ ] **Votación en clase** (una de tres): Zotero por MCP
   (`github.com/Sapere-IA/zotero-mcp`, solo herramientas de lectura, arranque en
   el `.env`; el MCP solo para PDFs y notas, sin duplicar la búsqueda), Semantic
   Scholar como herramienta de citas, o una fuente de CSV/BD local del grupo.
8. [ ] **Agente con Deep Agents**: `litmar revisar … --modo agente` con
   `create_deep_agent` y `herramientas.py`; instrucciones: planificar con lista
   de tareas, buscar en varias fuentes, citar solo DOIs que den las herramientas
   y decir lo que no encontró. Mismo formato de informe y BibTeX que el flujo.
   Subagente buscador. `--aprobar` con `interrupt_on` para pedir permiso antes de
   buscar. Límite de pasos (si se alcanza, escribir hasta dónde llegó) con test de
   modelo falso.
9. [ ] **Pestaña «Revisión» en la UI**: pregunta, modo flujo/agente, fuentes y
   número de artículos; pasos en vivo; informe con los DOI como enlaces; mensaje
   claro si falta la clave. Reutilizar las funciones de revisión (refactor
   mínimo si imprimen por pantalla) sin romper la terminal.
10. [ ] **Para la Clase 3**: los alumnos deben comprobar `docker run hello-world`.

## Cabos sueltos

- **Europe PMC deja HTML en títulos y resúmenes** (`<i>…</i>`, `&lt;i&gt;`),
  visto el 18/11 al probar `buscar_articulos`. Afecta a la tabla de la CLI, al
  BibTeX y a lo que ve el modelo. Limpiarlo en `fuentes/europepmc.py` (con
  `html.unescape` y quitar etiquetas) y añadir un test con un título así.
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

### 2026-11-18 — Sesión 2: herramientas (Clase 2, encargo 6)

- Prompt literal de la diapositiva 28. `src/litmar/herramientas.py`:
  `buscar_articulos(consulta, fuente="OpenAlex", n=5)` y `listar_fuentes()` con
  `@tool(parse_docstring=True)`; `HERRAMIENTAS` para el agente. D-20.
- «En qué fijarse»: (1) una herramienta para todas las fuentes, con `fuente`
  como parámetro; (2) los docstrings dicen qué devuelve, cuándo usarla, que solo
  se citen sus DOI y que PANGAEA da datos; (3) `n = max(1, min(n, 10))` en el
  código; (4) si una fuente falla, el modelo recibe «Error: OpenAlex respondió
  con HTTP 503. Prueba con otra fuente.», sin la URL.
- Refactor: `busqueda.mensaje_de_error()` (lo usan `buscar_en_fuentes` y la
  herramienta), con un caso para errores inesperados (solo el tipo).
- `tests/test_herramientas.py` (23 tests, sin red). 273 tests.
- Prueba real: las dos herramientas contra las APIs (Europe PMC, PANGAEA, una
  fuente inexistente) y `bind_tools` con Claude: pidió
  `buscar_articulos(consulta="ocean acidification coral", n=3)`. Se vio HTML en
  los títulos de Europe PMC (anotado en «Cabos sueltos»).

### 2026-11-18 — Sesión 2: salidas de `litmar revisar` en `ejemplos/revisiones/`

- Petición del usuario: guardar las salidas en `ejemplos/`, cada una en su
  subdirectorio. Decidió (herramienta de preguntas) nombre con fecha, hora y
  pregunta, y no versionarlas (D-19).
- `cli.py`: `nombre_carpeta()` y `carpeta_revision()`; `--informe` y `--bibtex`
  ya no tienen valor por defecto (si faltan, van a la carpeta de la ejecución).
  `.gitignore`: `ejemplos/revisiones/`. 4 tests nuevos (nombre, no pisar, CLI
  sin rutas, una revisión que falla no deja carpeta). 250 tests.

### 2026-11-18 — Sesión 2: flujo LangGraph y `litmar revisar` (Clase 2, encargo 5)

- Prompt literal de la diapositiva 19. Primero plan y diagrama Mermaid; el
  usuario pidió alinearlo con la diapositiva 18 (cambio: `planificar` da 2-3
  búsquedas, no 1-3) y decidió, con la herramienta de preguntas: «mejores» = más
  citados (D-17), marcar las citas inválidas tras 2 reescrituras (D-18), estado
  en inglés (D-2), y commit previo de la Práctica 1 (3416434, ya en `origin`).
- `src/litmar/flujo.py`: `EstadoRevision` (TypedDict; `warnings` con reductor
  `operator.add`), seis nodos como clausuras dentro de `crear_flujo(modelo,
  fuentes, n, desde, crear_fuente)`, arista condicional `decidir`. Límites en
  código: 3 consultas, 10 seleccionados, 2 reescrituras. `planificar` y
  `resumir` usan `method="json_schema"`. `sintetizar` sin resúmenes no llama al
  modelo; al reescribir le pasa su informe y los DOI inválidos. Las citas se
  extraen con una regex (`[doi:…]` o `doi.org/…`) y se normalizan con
  `normalizar_doi`. `describir_paso` da las líneas de la demo (no imprime: la
  UI la reutilizará). Las referencias del informe las genera el código.
- CLI: `litmar revisar "pregunta" [--modo flujo] [--fuente] [-n ≤10] [--desde]
  [--informe revision.md] [--bibtex revision.bib]`, con `stream(stream_mode=
  ["updates", "values"])`. Errores del modelo → mensaje y código 1.
- Dependencia nueva: `langgraph` (1.2.22). `tests/test_flujo.py` (16 tests):
  aristas del grafo = diagrama, recorrido completo, reescritura, máximo de 2,
  sin artículos, resumen que falla, CLI. 245 tests.
- Prueba real (Anthropic) con la pregunta de la demo: 3 consultas, 50
  artículos, 6 seleccionados, informe con 5 citas, todas verificadas, 1:35 min.
  El filtro por citas metió dos trabajos generales sobre olas de calor: buen
  ejemplo para la Práctica 2. No se vio una reescritura real (el modelo no
  inventó); el camino está cubierto por tests.
- A petición del usuario, `docs/flujo.md`: el diagrama Mermaid didáctico (LLM /
  CÓDIGO, como la diapositiva 18), una tabla de qué lee y escribe cada nodo en
  el estado, y el Mermaid que genera LangGraph (`get_graph().draw_mermaid()`).
  Un test falla si este último deja de coincidir con el grafo. 246 tests.

### 2026-11-18 — Sesión 2: Práctica 1 (`ejemplos/resumir.py`) y prueba real

- `ejemplos/resumir.py`: carga `.env`, crea el modelo (si falta algo, imprime el
  error y sale con 1), busca en OpenAlex los 3 primeros artículos sobre «ocean
  acidification» que tienen resumen (pide 12) y muestra el resumen de cada uno
  con su enlace al DOI. Si un resumen falla (p. ej. 429), sigue con los demás.
  `TEMA` y `PREGUNTA` arriba para que cada alumno ponga los suyos. Test en
  `tests/test_ejemplos.py` con fuente y modelo falsos.
- **Primera prueba real** (el usuario ya tiene `anthropic:claude-sonnet-5-5` en
  el `.env`): los tres resúmenes salen bien y marcan lo que no está en el
  resumen («No consta…»). `langchain-anthropic` avisaba de que el método por
  defecto (`function_calling`) puede fallar en ese modelo: `resumir` pasa ahora
  `method="json_schema"`, válido también en Gemini. Trampa anotada en
  `AGENTS.md` §9.
- 229 tests.

### 2026-11-18 — Sesión 2: `llm.py` (Clase 2, encargo 3)

- Prompt literal de la diapositiva 12. `src/litmar/llm.py`: `crear_modelo()` lee
  `LITMAR_MODELO` (formato `proveedor:modelo`), comprueba la clave del proveedor
  (`GOOGLE_API_KEY`/`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) y
  llama a `init_chat_model` con un `InMemoryRateLimiter`. Si falta algo,
  `ErrorDeConfiguracion` con la línea exacta que hay que añadir al `.env`.
- Límite: 10 llamadas/min por defecto, `LITMAR_LLAMADAS_POR_MINUTO` (0 = sin
  límite). Decisiones D-15 (dependencias) y D-16 (límite, `.env` no se carga en
  `llm.py`).
- Dependencias nuevas: `langchain`, `langchain-google-genai`,
  `langchain-anthropic` («En qué fijarse» 3).
- `.env.example`: sección del modelo de lenguaje. README: tabla de variables y
  ejemplo con `crear_modelo`.
- `tests/test_llm.py` (16 tests): crean el objeto del modelo con claves falsas,
  sin llamarlo. 227 tests.
- Prueba real: no se pudo, el `.env` no tiene `LITMAR_MODELO` (se vio el
  mensaje de error, que es el punto 2 de la diapositiva).

### 2026-11-18 — Sesión 2: `resumir` (Clase 2, encargo 2)

- Prompt literal de la diapositiva 11. Nuevo `src/litmar/resumen.py`:
  `ResumenArticulo` (Pydantic) con `objective`, `method`, `findings` (lista),
  `relevance` (1-5, validado con `ge`/`le`) y `limitations`, todos con
  descripción porque el modelo las lee. `resumir()` devuelve `None` sin llamar
  al modelo si no hay resumen, y las instrucciones piden usar solo título y
  resumen y escribir «No consta en el resumen.» en vez de inventar.
- Campos en inglés aunque la diapositiva los nombra en español: convención D-2.
- El modelo se recibe como parámetro (lo creará `llm.py`); `resumen.py` no lee
  claves ni conoce proveedores. Dependencias nuevas: `pydantic` y
  `langchain-core` (de ahí viene `with_structured_output`).
- `tests/test_resumen.py`: modelo falso propio (solo `with_structured_output` e
  `invoke`), sin clave ni red. 211 tests. Sección en el README.
- Sin probar con un modelo real: falta `llm.py` (siguiente encargo).

### 2026-11-18 — Sesión 2: comprobación de los hooks

- El hook `SessionStart` funciona en una sesión real (al reanudar inyectó el
  estado de `PROGRESS.md` y de git). Paso 0 actualizado.
- Dudas del usuario sobre `Stop`: se ejecuta al final de **cada turno** (no al
  salir, ni con Esc, ni si se apaga el ordenador; para la salida existe
  `SessionEnd`, que no puede pedir nada al agente). Cuesta 0 tokens cuando deja
  terminar; si bloquea, ~100 tokens más la edición de `PROGRESS.md`, una vez por
  turno. Se le ofreció una versión más silenciosa (ignorar commits ya hechos);
  de momento se queda como está.
- Sin cambios de código. La Clase 2 sigue sin empezar.

### 2026-11-17 — Sesión 1 (cierre 2): diapositivas de la Clase 2

- El usuario añadió `docs/Clase2.pdf`. De ella salen: el «Plan de la Clase 2»
  de este fichero, la hoja de ruta y los principios de `AGENTS.md` §2, y D-14
  (variables `LITMAR_MODELO` + clave del proveedor; `CROSSREF_MAILTO` se queda),
  que resuelve la duda pendiente sobre `LITMAR_EMAIL`.
- No se ha escrito código de la Clase 2. Queda por preguntar al usuario si se
  construye ya o en directo en clase.

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
