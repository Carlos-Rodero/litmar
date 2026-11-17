import pytest

from litmar import Articulo


@pytest.fixture
def hacer_articulo():
    """Fábrica de artículos válidos; los tests sobrescriben solo lo que les importa."""

    def _hacer(**cambios) -> Articulo:
        datos = {
            "title": "Aprendizaje profundo para la clasificación de textos",
            "authors": ["García, Ana", "López, Juan", "Pérez, Marta"],
            "year": 2021,
            "doi": "10.1000/xyz123",
            "journal": "Revista de Informática",
            "abstract": "Un estudio sobre redes neuronales.",
            "citations": 42,
        }
        datos.update(cambios)
        return Articulo(**datos)

    return _hacer
