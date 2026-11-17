"""Creación de fuentes configuradas con variables de entorno (ver .env.example)."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping

from litmar.fuentes import Arxiv, Crossref, EuropePMC, Fuente, OpenAlex, Pangaea, Zotero


def _valor(entorno: Mapping[str, str], clave: str) -> str | None:
    """Valor de la variable sin espacios; None si falta o está vacía."""
    valor = entorno.get(clave, "").strip()
    return valor or None


def _zotero(entorno: Mapping[str, str]) -> Zotero:
    return Zotero(
        user_id=_valor(entorno, "ZOTERO_USER_ID"),
        group_id=_valor(entorno, "ZOTERO_GROUP_ID"),
        api_key=_valor(entorno, "ZOTERO_API_KEY"),
    )


_CONSTRUCTORES: dict[str, Callable[[Mapping[str, str]], Fuente]] = {
    "OpenAlex": lambda e: OpenAlex(api_key=_valor(e, "OPENALEX_API_KEY")),
    "Crossref": lambda e: Crossref(mailto=_valor(e, "CROSSREF_MAILTO")),
    "Europe PMC": lambda e: EuropePMC(),
    "arXiv": lambda e: Arxiv(),
    "PANGAEA": lambda e: Pangaea(),
    "Zotero": _zotero,
}

FUENTES: tuple[str, ...] = tuple(_CONSTRUCTORES)


def fuentes_disponibles(entorno: Mapping[str, str] | None = None) -> list[str]:
    """Fuentes que se pueden usar con la configuración actual.

    Todas funcionan sin configurar nada salvo Zotero, que necesita saber en qué
    biblioteca buscar (ZOTERO_USER_ID o ZOTERO_GROUP_ID).
    """
    entorno = os.environ if entorno is None else entorno
    zotero = _valor(entorno, "ZOTERO_USER_ID") or _valor(entorno, "ZOTERO_GROUP_ID")
    return [nombre for nombre in FUENTES if nombre != "Zotero" or zotero]


def crear_fuente(nombre: str, entorno: Mapping[str, str] | None = None) -> Fuente:
    """Crea la fuente `nombre` (uno de FUENTES) con sus claves del entorno."""
    try:
        constructor = _CONSTRUCTORES[nombre]
    except KeyError:
        raise ValueError(f"fuente desconocida: {nombre!r}") from None
    return constructor(os.environ if entorno is None else entorno)
