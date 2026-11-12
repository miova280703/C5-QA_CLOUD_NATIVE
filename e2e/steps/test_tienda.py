"""Steps de tienda.feature (pytest-bdd) sobre el patron Screenplay.

Los steps NO tocan Playwright directamente: delegan en tasks/questions del
paquete screenplay. La URL base viene del fixture `base_url` (BASE_URL).
"""
from pytest_bdd import scenarios, given, when, then, parsers

from screenplay.tasks import (
    AbrirElCatalogo,
    FiltrarPorCategoria,
    VerElDetalleDelPrimerProducto,
    AgregarDesdeElDetalle,
    AgregarElPrimerProductoAlCarrito,
    AbrirElCarrito,
    IngresarElCorreo,
    ConfirmarElPedido,
)
from screenplay.questions import (
    ContadorCarrito,
    CategoriasVisibles,
    NumeroDePedido,
    MensajeDeExitoVisible,
    MensajeCarritoVacioVisible,
)

scenarios("tienda.feature")


# ── GIVEN ─────────────────────────────────────────────────────────
@given("que estoy en la página del catálogo de la Tienda")
def abrir_catalogo(actor):
    actor.intenta(AbrirElCatalogo())


@given("que tengo un producto en el carrito")
def producto_en_el_carrito(actor):
    actor.intenta(AbrirElCatalogo(), AgregarElPrimerProductoAlCarrito())


@given("que estoy en la vista del carrito y este se encuentra vacío")
def carrito_vacio(actor):
    actor.intenta(AbrirElCatalogo(), AbrirElCarrito())


# ── WHEN ──────────────────────────────────────────────────────────
@when(parsers.parse('selecciono la categoría "{categoria}"'))
def filtrar_categoria(actor, categoria):
    actor.intenta(FiltrarPorCategoria.llamada(categoria))


@when("hago clic en los detalles del primer producto")
def ver_detalle(actor):
    actor.intenta(VerElDetalleDelPrimerProducto())


@when('hago clic en "Agregar al carrito" desde la vista de detalles')
def agregar_desde_detalle(actor):
    actor.intenta(AgregarDesdeElDetalle())


@when("accedo a la vista del carrito")
def ir_al_carrito(actor):
    actor.intenta(AbrirElCarrito())


@when(parsers.parse('ingreso mi correo electrónico "{correo}"'))
def ingresar_correo(actor, correo):
    actor.intenta(IngresarElCorreo.con(correo))


@when('hago clic en "Confirmar pedido"')
def confirmar_pedido(actor):
    actor.intenta(ConfirmarElPedido())


# ── THEN ──────────────────────────────────────────────────────────
@then(
    parsers.parse(
        'debería ver en la cuadrícula los productos que pertenecen a la categoría "{categoria}"'
    )
)
def verificar_categoria(actor, categoria):
    categorias = actor.pregunta(CategoriasVisibles.lista())
    assert categorias, "No se encontraron productos en la cuadrícula"
    assert all(c == categoria for c in categorias), (
        f"Se esperaban solo '{categoria}', pero hay: {set(categorias)}"
    )


@then(parsers.parse('el contador del carrito debería mostrar "{numero}"'))
def verificar_contador(actor, numero):
    assert actor.pregunta(ContadorCarrito.valor()) == int(numero)


@then("debería ver un mensaje de confirmación del pedido con un número de orden")
def verificar_pedido(actor):
    assert actor.pregunta(MensajeDeExitoVisible.estado()) is True
    assert actor.pregunta(NumeroDePedido.texto()) != ""


@then("debería ver un mensaje que indique que el carrito está vacío")
def verificar_carrito_vacio(actor):
    assert actor.pregunta(MensajeCarritoVacioVisible.estado()) is True
