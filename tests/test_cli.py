import json
from pathlib import Path

import httpx
import pytest

from litmar import Biblioteca
from litmar.cli import main
from litmar.fuentes import OpenAlex


@pytest.fixture
def openalex_simulado(monkeypatch):
    peticiones = []
    respuesta = json.loads(
        (Path(__file__).parent / "datos" / "openalex_works.json").read_text(encoding="utf-8")
    )

    def manejar(peticion):
        peticiones.append(peticion)
        return httpx.Response(200, json=respuesta)

    clientes = []

    def crear(**kwargs):
        fuente = OpenAlex(**kwargs)
        fuente.client.close()
        fuente.client = httpx.Client(transport=httpx.MockTransport(manejar))
        clientes.append(fuente.client)
        return fuente

    monkeypatch.setattr("litmar.cli.OpenAlex", crear)
    return peticiones, clientes


def test_buscar_guardar_combinar_y_exportar(tmp_path, hacer_articulo, openalex_simulado, capsys):
    ruta = tmp_path / "biblioteca.json"
    salida = tmp_path / "referencias.bib"
    original = hacer_articulo()
    Biblioteca([original]).guardar(ruta)

    for _ in range(2):
        assert main(["buscar", "bibliometrics", "-n", "2", "--guardar", str(ruta)]) == 0
    biblioteca = Biblioteca.cargar(ruta)
    assert len(biblioteca) == 3
    assert biblioteca.obtener(original.doi) == original
    assert main(["exportar", str(ruta), "--bibtex", str(salida)]) == 0
    assert salida.read_text(encoding="utf-8") == biblioteca.a_bibtex()
    assert "0 nuevos; 3 artículos" in capsys.readouterr().out
    peticiones, clientes = openalex_simulado
    assert len(peticiones) == 2
    assert all(cliente.is_closed for cliente in clientes)


def test_buscar_crea_biblioteca_y_lee_clave_del_entorno(tmp_path, openalex_simulado, monkeypatch):
    monkeypatch.setenv("OPENALEX_API_KEY", "clave-de-prueba")
    ruta = tmp_path / "nueva.json"
    assert main(["buscar", "bibliometrics", "-n", "2", "--guardar", str(ruta)]) == 0
    assert len(Biblioteca.cargar(ruta)) == 2
    assert openalex_simulado[0][0].headers["authorization"] == "Bearer clave-de-prueba"


def test_buscar_sin_guardar_muestra_resultados(openalex_simulado, capsys):
    assert main(["buscar", "bibliometrics", "-n", "2"]) == 0
    salida = capsys.readouterr().out
    assert "2 resultados" in salida
    assert "https://doi.org/10.1515/libr.1996.46.3.149" in salida


@pytest.mark.parametrize("args", [[], ["buscar", "x", "-n", "0"], ["buscar", "  "], ["exportar", "x.json"]])
def test_argumentos_invalidos(args):
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2


def test_json_invalido_no_se_sobrescribe_ni_consulta_la_red(tmp_path, openalex_simulado, capsys):
    ruta = tmp_path / "biblioteca.json"
    ruta.write_text("contenido inválido", encoding="utf-8")
    assert main(["buscar", "x", "--guardar", str(ruta)]) == 1
    assert ruta.read_text(encoding="utf-8") == "contenido inválido"
    assert openalex_simulado[0] == []
    assert "Error:" in capsys.readouterr().err


@pytest.mark.parametrize("estado", [401, 429, 503])
def test_error_http_conserva_biblioteca(tmp_path, hacer_articulo, monkeypatch, capsys, estado):
    ruta = tmp_path / "biblioteca.json"
    Biblioteca([hacer_articulo()]).guardar(ruta)
    original = ruta.read_bytes()
    with httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(estado))) as client:
        monkeypatch.setattr(
            "litmar.cli.OpenAlex", lambda **kwargs: OpenAlex(client=client, max_retries=0)
        )
        assert main(["buscar", "x", "--guardar", str(ruta)]) == 1
    assert ruta.read_bytes() == original
    assert f"HTTP {estado}" in capsys.readouterr().err


def test_error_de_red_se_explica(monkeypatch, capsys):
    def fallar(peticion):
        raise httpx.ConnectError("sin conexión", request=peticion)

    with httpx.Client(transport=httpx.MockTransport(fallar)) as client:
        monkeypatch.setattr(
            "litmar.cli.OpenAlex", lambda **kwargs: OpenAlex(client=client, max_retries=0)
        )
        assert main(["buscar", "x"]) == 1
    assert "no se pudo conectar" in capsys.readouterr().err


def test_exportar_archivo_inexistente(tmp_path, capsys):
    assert main(["exportar", str(tmp_path / "no.json"), "--bibtex", str(tmp_path / "x.bib")]) == 1
    assert "Error:" in capsys.readouterr().err


def test_exportar_no_sobrescribe_la_biblioteca(tmp_path):
    ruta = tmp_path / "biblioteca.json"
    Biblioteca().guardar(ruta)
    original = ruta.read_bytes()
    assert main(["exportar", str(ruta), "--bibtex", str(ruta)]) == 1
    assert ruta.read_bytes() == original


def test_ui_lanza_streamlit_con_el_mismo_interprete(monkeypatch):
    import sys

    llamadas = []
    monkeypatch.setattr("litmar.cli.subprocess.call", lambda args: llamadas.append(args) or 0)
    assert main(["ui"]) == 0
    [args] = llamadas
    assert args[:4] == [sys.executable, "-m", "streamlit", "run"]
    assert Path(args[4]) == Path(__file__).parent.parent / "src" / "litmar" / "ui.py"
    assert args[5:] == ["--browser.gatherUsageStats", "false"]


def test_ui_pasa_opciones_a_streamlit(monkeypatch):
    llamadas = []
    monkeypatch.setattr("litmar.cli.subprocess.call", lambda args: llamadas.append(args) or 0)
    assert main(["ui", "--server.port", "8600"]) == 0
    assert llamadas[0][-2:] == ["--server.port", "8600"]


def test_ui_sin_streamlit_explica_como_instalarlo(monkeypatch, capsys):
    monkeypatch.setattr("litmar.cli.importlib.util.find_spec", lambda nombre: None)
    monkeypatch.setattr("litmar.cli.subprocess.call", lambda args: pytest.fail("no debe lanzarse"))
    assert main(["ui"]) == 1
    assert "uv sync --extra ui" in capsys.readouterr().err
