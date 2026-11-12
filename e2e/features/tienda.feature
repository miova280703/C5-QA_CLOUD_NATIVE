# language: en
Feature: Tienda de Malabares
    Como usuario de la Tienda
    Quiero navegar por el catálogo, gestionar el carrito y confirmar pedidos
    Para asegurar el correcto funcionamiento de la Tienda

    # @TC<n> = ID del Test Case en Azure Test Plans (enlaza el resultado al caso)
    @catalogo @TC4
    Scenario: Visualizar y filtrar productos en el catálogo
        Given que estoy en la página del catálogo de la Tienda
        When selecciono la categoría "clavas"
        Then debería ver en la cuadrícula los productos que pertenecen a la categoría "clavas"

    @carrito @TC5
    Scenario: Agregar un producto al carrito desde el detalle
        Given que estoy en la página del catálogo de la Tienda
        When hago clic en los detalles del primer producto
        And hago clic en "Agregar al carrito" desde la vista de detalles
        Then el contador del carrito debería mostrar "1"

    @pedidos @TC6
    Scenario: Completar un pedido exitosamente
        Given que tengo un producto en el carrito
        When accedo a la vista del carrito
        And ingreso mi correo electrónico "iovasqa@gmail.com"
        And hago clic en "Confirmar pedido"
        Then debería ver un mensaje de confirmación del pedido con un número de orden

    @carrito @borde @TC7
    Scenario: Carrito vacío muestra mensaje
        Given que estoy en la vista del carrito y este se encuentra vacío
        Then debería ver un mensaje que indique que el carrito está vacío
