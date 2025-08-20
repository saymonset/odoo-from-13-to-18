from odoo import http


class PriceListController(http.Controller):
    # Ruta para obtener la lista de precios
    @http.route(
        "/delivery_orders_report/get_price_list",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def get_price_list(self, companyId=None):
        """
        Obtiene la lista de precios para una compañía específica.

        :param companyId: ID de la compañía (opcional).
        :return: Lista de precios en formato JSON.
        """
        # Obtener el modelo ProfitMargin
        profit_margin_model = http.request.env["profit_margin"]

        # Llamar al método get_price_list
        result = profit_margin_model.get_price_list(companyId)

        # Devolver el resultado como respuesta JSON
        return result
