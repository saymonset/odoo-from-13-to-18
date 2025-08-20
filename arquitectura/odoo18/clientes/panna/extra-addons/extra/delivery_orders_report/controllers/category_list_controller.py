from odoo import http


class CategoryListController(http.Controller):
    # Ruta para obtener órdenes agrupadas por categoría
    @http.route(
        "/delivery_orders_report/order_group_by_categ",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def get_delivery_category(self, pricelistId=None):
        """
        Obtiene las órdenes de entrega agrupadas por categoría.

        :param pricelistId: ID de la lista de precios (opcional).
        :return: Resultado de la agrupación de órdenes de entrega por categoría en formato JSON.
        """
        # Obtener el modelo ProfitMargin
        profit_margin_model = http.request.env["profit_margin"]

        # Llamar al método delivery_category_group
        result = profit_margin_model.delivery_category_group(pricelistId)

        # Devolver el resultado como respuesta JSON
        return result

    # Ruta para obtener productos por categoría
    @http.route(
        "/delivery_orders_report/get_product_by_ctegory",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def get_product_by_ctegory(self, categId=None):
        """
        Obtiene productos pertenecientes a una categoría específica.

        :param categId: ID de la categoría (opcional).
        :return: Lista de productos en formato JSON.
        """
        # Obtener el modelo ProfitMargin
        profit_margin_model = http.request.env["profit_margin"]

        # Llamar al método get_product_by_ctegory
        result = profit_margin_model.get_product_by_ctegory(categId)

        # Devolver el resultado como respuesta JSON
        return result
