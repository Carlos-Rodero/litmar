"""Interfaz de terminal para buscar, conservar y exportar bibliografía."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx

from litmar.biblioteca import Biblioteca
from litmar.fuentes import OpenAlex


def _positivo(valor: str) -> int:
    numero = int(valor)
    if numero < 1:
        raise argparse.ArgumentTypeError("debe ser al menos 1")
    return numero


def _consulta(valor: str) -> str:
    if not valor.strip():
        raise argparse.ArgumentTypeError("la consulta no puede estar vacía")
    return valor.strip()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Busca y organiza artículos científicos.")
    comandos = parser.add_subparsers(dest="comando", required=True)
    buscar = comandos.add_parser("buscar", help="Buscar artículos en OpenAlex")
    buscar.add_argument("consulta", type=_consulta)
    buscar.add_argument("-n", type=_positivo, default=10, help="Número máximo de resultados (10)")
    buscar.add_argument(
        "--guardar", type=Path, metavar="ARCHIVO.json",
        help="Guardar resultados; si existe, combinar sin duplicar DOI",
    )
    exportar = comandos.add_parser("exportar", help="Exportar una biblioteca JSON a BibTeX")
    exportar.add_argument("biblioteca", type=Path)
    exportar.add_argument("--bibtex", type=Path, required=True, metavar="ARCHIVO.bib")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.comando == "buscar":
            biblioteca = (
                Biblioteca.cargar(args.guardar)
                if args.guardar is not None and args.guardar.exists()
                else Biblioteca()
            )
            with OpenAlex(api_key=os.environ.get("OPENALEX_API_KEY")) as fuente:
                resultados = fuente.buscar(args.consulta, n=args.n)
            nuevos = sum(biblioteca.agregar(articulo) for articulo in resultados)
            if args.guardar is not None:
                biblioteca.guardar(args.guardar)
            for articulo in resultados:
                print(f"{articulo.short_citation}: {articulo.title}\n  https://doi.org/{articulo.doi}")
            print(f"{len(resultados)} resultados.")
            if args.guardar is not None:
                print(f"{nuevos} nuevos; {len(biblioteca)} artículos en {args.guardar}.")
        else:
            if args.biblioteca.resolve() == args.bibtex.resolve():
                raise ValueError("el archivo BibTeX debe ser distinto de la biblioteca JSON")
            biblioteca = Biblioteca.cargar(args.biblioteca)
            biblioteca.exportar_bibtex(args.bibtex)
            print(f"{len(biblioteca)} artículos exportados a {args.bibtex}.")
    except httpx.HTTPStatusError as exc:
        # No imprimir la petición ni las cabeceras: podrían contener credenciales.
        print(f"Error: OpenAlex respondió con HTTP {exc.response.status_code}.", file=sys.stderr)
        return 1
    except httpx.TransportError:
        print("Error: no se pudo conectar con OpenAlex tras los reintentos.", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0
