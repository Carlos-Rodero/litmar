from litmar.articulo import Articulo
from litmar.biblioteca import Biblioteca

__all__ = ["Articulo", "Biblioteca", "main"]


def main() -> None:
    from litmar.cli import main as ejecutar

    raise SystemExit(ejecutar())
