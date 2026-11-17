"""Interfaz web de litmar con Streamlit. Se abre con `litmar ui`."""

from __future__ import annotations

import httpx
import streamlit as st

from litmar.biblioteca import Biblioteca
from litmar.configuracion import crear_fuente, fuentes_disponibles

MAX_RESULTADOS = 200


def buscar(consulta: str, nombres: list[str], n: int) -> tuple[Biblioteca, list[str]]:
    """Busca en cada fuente y junta los resultados sin duplicar DOI.

    Si una fuente falla se sigue con las demás; devuelve también los errores.
    """
    biblioteca = Biblioteca()
    errores = []
    for nombre in nombres:
        try:
            with crear_fuente(nombre) as fuente:
                for articulo in fuente.buscar(consulta, n):
                    biblioteca.agregar(articulo)
        # No mostrar la petición ni las cabeceras: podrían contener credenciales.
        except httpx.HTTPStatusError as exc:
            errores.append(f"{nombre} respondió con HTTP {exc.response.status_code}.")
        except httpx.TransportError:
            errores.append(f"No se pudo conectar con {nombre} tras los reintentos.")
        except ValueError as exc:
            errores.append(f"{nombre}: {exc}")
    return biblioteca, errores


def filas(biblioteca: Biblioteca) -> list[dict[str, object]]:
    """Filas de la tabla de resultados."""
    return [
        {
            "Año": articulo.year,
            "Citas": articulo.citations,
            "Autores": "; ".join(articulo.authors),
            "Título": articulo.title,
            "DOI": f"https://doi.org/{articulo.doi}",
        }
        for articulo in biblioteca
    ]


def app() -> None:
    st.set_page_config(page_title="litmar", page_icon="📚", layout="wide")
    st.title("litmar")
    st.caption("Busca literatura científica en varias fuentes y exporta las referencias.")

    disponibles = fuentes_disponibles()
    with st.form("busqueda"):
        consulta = st.text_input("Búsqueda", placeholder="ocean acidification")
        nombres = st.multiselect("Fuentes", disponibles, default=["OpenAlex"])
        n = st.number_input(
            "Resultados por fuente", min_value=1, max_value=MAX_RESULTADOS, value=10
        )
        enviado = st.form_submit_button("Buscar", type="primary")
    if "Zotero" not in disponibles:
        st.caption("Para buscar en Zotero, indica ZOTERO_USER_ID o ZOTERO_GROUP_ID en `.env`.")

    if enviado:
        if not consulta.strip():
            st.warning("Escribe algo que buscar.")
        elif not nombres:
            st.warning("Elige al menos una fuente.")
        else:
            with st.spinner("Buscando…"):
                # Se guarda en la sesión para que sobreviva a las recargas que
                # provocan los botones de descarga.
                st.session_state.resultado = buscar(consulta.strip(), nombres, int(n))

    if "resultado" not in st.session_state:
        return
    biblioteca, errores = st.session_state.resultado
    for error in errores:
        st.error(error)
    if not len(biblioteca):
        st.info("No hay resultados.")
        return

    st.subheader(f"{len(biblioteca)} artículos")
    st.dataframe(
        filas(biblioteca),
        hide_index=True,
        width="stretch",
        column_config={
            "Año": st.column_config.NumberColumn(format="%d"),
            "DOI": st.column_config.LinkColumn(display_text=r"https://doi\.org/(.*)"),
        },
    )
    bibtex, csv = st.columns(2)
    bibtex.download_button(
        "Descargar BibTeX",
        biblioteca.a_bibtex(),
        file_name="litmar.bib",
        mime="application/x-bibtex",
        width="stretch",
    )
    csv.download_button(
        "Descargar CSV",
        # Con BOM para que Excel reconozca el UTF-8 (tildes, eñes...).
        biblioteca.a_csv().encode("utf-8-sig"),
        file_name="litmar.csv",
        mime="text/csv",
        width="stretch",
    )


if __name__ == "__main__":
    app()
