"""
TEST DEL CONSUMER (lado consumer de Pact) - GET /api/productos

1. Levanta un mock provider controlado por Pact.
2. Declara el CONTRATO: "al pedir GET /api/productos espero 200 con una LISTA
   de productos (al menos 1) y cada uno con id, nombre, categoria, precio, stock".
3. Corre el cliente REAL contra el mock.
4. Si funciona, Pact ESCRIBE el contrato en PACT_DIR (frontend-tienda-api.json).

Aqui NO se toca el provider real: eso lo hace verificar_provider.py.

Correr:  pip install -r requirements.txt && pytest -v
"""
import atexit
import os

import pytest
from pact import Consumer, Provider, Like, EachLike

from cliente_productos import ClienteProductos

PACT_MOCK_HOST = "localhost"
PACT_MOCK_PORT = 1234
PACT_DIR = os.environ.get("PACT_DIR", "../pacts")

pact = Consumer("front-tienda").has_pact_with(
    Provider("tienda-api"),
    host_name=PACT_MOCK_HOST,
    port=PACT_MOCK_PORT,
    pact_dir=PACT_DIR,
)
pact.start_service()
atexit.register(pact.stop_service)


@pytest.fixture
def cliente():
    return ClienteProductos(f"http://{PACT_MOCK_HOST}:{PACT_MOCK_PORT}")


def test_listar_productos(cliente):
    # Pact valida la FORMA (tipos), no los valores exactos.
    producto = {
        "id": Like(1),
        "nombre": Like("Clava Profesional PX3 THX"),
        "categoria": Like("clavas"),
        "precio": Like(485.39),
        "stock": Like(56),
    }

    (
        pact
        .given("existen productos en el catalogo")          # provider state
        .upon_receiving("una peticion de la lista de productos")
        .with_request("get", "/api/productos")
        .will_respond_with(200, body=EachLike(producto, minimum=1))
    )

    with pact:
        resumen = cliente.resumen_catalogo()
        assert "productos" in resumen
        assert "$" in resumen
