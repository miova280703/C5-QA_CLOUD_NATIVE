"""
CONSUMER del contrato: el front / servicio que CONSUME la API de la Tienda.

Hace peticiones HTTP al provider (GET /api/productos) y depende de la FORMA de
la respuesta (id, nombre, categoria, precio, stock). Esa expectativa es el
CONTRATO. El cliente no sabe como esta hecho el provider por dentro.
"""
import requests


class ClienteProductos:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def listar_productos(self) -> list:
        """GET /api/productos -> lista de productos. Lanza si no es 200."""
        r = requests.get(f"{self.base_url}/api/productos", timeout=5)
        r.raise_for_status()
        return r.json()

    def resumen_catalogo(self) -> str:
        """Logica del consumer: arma un resumen con lo que muestra el front.

        Depende de que cada producto tenga 'nombre', 'categoria' y 'precio'.
        Eso es exactamente lo que el contrato Pact asegura.
        """
        productos = self.listar_productos()
        categorias = sorted({p["categoria"] for p in productos})
        mas_barato = min(productos, key=lambda p: p["precio"])
        return (
            f"{len(productos)} productos en {len(categorias)} categorias; "
            f"el mas barato es '{mas_barato['nombre']}' (${mas_barato['precio']:.2f})."
        )
