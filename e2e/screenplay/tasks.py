"""Tasks: acciones de negocio de alto nivel (se componen de interactions)."""
from .interactions import Abrir, HacerClic, Escribir, Seleccionar
from .abilities import NavegarConElNavegador


def _page(actor):
    return actor.habilidad(NavegarConElNavegador).page


class AbrirElCatalogo:
    def ejecutar_como(self, actor):
        actor.intenta(Abrir.la_pagina("/"))
        # Esperar a que el grid tenga al menos un producto
        _page(actor).wait_for_selector(
            '[data-testid="grid-productos"] .card', timeout=10000
        )


class FiltrarPorCategoria:
    def __init__(self, categoria: str):
        self.categoria = categoria

    @staticmethod
    def llamada(categoria: str) -> "FiltrarPorCategoria":
        return FiltrarPorCategoria(categoria)

    def ejecutar_como(self, actor):
        actor.intenta(Seleccionar.el_valor(self.categoria).en("filtro-categoria"))


class VerElDetalleDelPrimerProducto:
    def ejecutar_como(self, actor):
        _page(actor).locator('[data-testid^="ver-"]').first.click()
        _page(actor).wait_for_selector(
            '[data-testid="vista-detalle"].activa', timeout=10000
        )


class AgregarDesdeElDetalle:
    """El boton del detalle agrega el producto y lleva directo al carrito."""

    def ejecutar_como(self, actor):
        actor.intenta(HacerClic.en("detalle-agregar"))
        _page(actor).wait_for_selector(
            '[data-testid="vista-carrito"].activa', timeout=10000
        )


class AgregarElPrimerProductoAlCarrito:
    def ejecutar_como(self, actor):
        _page(actor).locator('[data-testid^="agregar-"]').first.click()


class AbrirElCarrito:
    def ejecutar_como(self, actor):
        actor.intenta(HacerClic.en("abrir-carrito"))
        _page(actor).wait_for_selector(
            '[data-testid="vista-carrito"].activa', timeout=10000
        )


class IngresarElCorreo:
    def __init__(self, correo: str):
        self.correo = correo

    @staticmethod
    def con(correo: str) -> "IngresarElCorreo":
        return IngresarElCorreo(correo)

    def ejecutar_como(self, actor):
        actor.intenta(Escribir.el_texto(self.correo).en("input-email"))


class ConfirmarElPedido:
    def ejecutar_como(self, actor):
        actor.intenta(HacerClic.en("confirmar-pedido"))
        # El pedido se crea via fetch (async) y luego cambia la vista:
        # esperar la confirmacion antes de seguir.
        _page(actor).wait_for_selector(
            '[data-testid="vista-exito"].activa', timeout=10000
        )
