import logging
from odoo import models, fields, api
import json
from ..services.info_user_company_service import user_company_service


_logger = logging.getLogger(__name__)


class ProfitMargin(models.Model):
    _name = "profit_margin"
    _description = "Profit Margin"

    report_data = fields.Text(
        string="Reporte de Productos"
    )  # Asegúrate de que este campo esté definido
    name = fields.Char("Name")
    pricelist_ids = fields.Many2many("product.pricelist", string="Price Lists")
    user_company_info = fields.Text(
        string="Información de la Compañía"
    )  # O el tipo de campo que necesites

    @api.model
    def create_report(self, products):
        if not products:
            raise ValueError("No se proporcionaron productos para el reporte.")

        # Llama al servicio para obtener información del usuario y la compañía
        user_company_info = json.dumps(user_company_service(self))
        report_data = json.dumps(
            products
        )  # Asegúrate de que los productos se serialicen correctamente

        try:
            wizard = self.create(
                {
                    "report_data": report_data,
                    "user_company_info": user_company_info,  # Asegúrate de que este campo esté definido
                }
            )
        except Exception as e:
            _logger.error("Error al crear el wizard: %s", e)
            raise

        return wizard.id

    def print_report(self):
        action = self.env.ref(
            "delivery_orders_report.action_profit_margin_report"
        ).report_action(self)

        # Asegúrate de que el contexto incluya 'doc' y 'report_data'
        action["context"]["doc"] = self
        action["context"]["report_data"] = self.report_data
        action["context"]["user_company_info"] = (
            self.user_company_info
        )  # Agrega la información de la compañía

        return action

    def get_dynamic_buttons(self):
        buttons = []
        for pricelist in self.pricelist_ids:
            buttons.append(
                {
                    "name": pricelist.name,
                    "action": "action_name_here",  # Define la acción que deseas realizar
                    "type": "object",  # Tipo de acción
                }
            )
        return buttons

    @api.model
    def action_name_here(self):
        # Define la lógica que deseas ejecutar cuando se presione el botón
        _logger.info("Button pressed for Price List")

    def delivery_category_group(self, pricelistId):
        # Inicializar la consulta SQL y los parámetros
        query = """
                   SELECT
                        product_pricelist.id,
                        product_pricelist.name,
                        product_category.id,
                        product_category.name
                    FROM
                        product_template
                    JOIN
                        product_category on product_category.id = product_template.categ_id
                    JOIN  -- Cambiado a LEFT JOIN
                        product_pricelist_item ON product_pricelist_item.categ_id = product_category.id
                    JOIN  -- Cambiado a LEFT JOIN
                        product_pricelist ON product_pricelist.id = product_pricelist_item.pricelist_id

                    WHERE
                    product_pricelist.id = %(pricelist_id)s
        """
        params = {
            "pricelist_id": -1 if not pricelistId else pricelistId,
        }

        query += """
            GROUP BY
                product_category.name,
                product_pricelist.name,
                product_category.id,
                product_pricelist.id
            ORDER BY
                 product_category.name;
        """

        # Ejecutar la consulta
        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()
        # Verificar si el resultado está vacío
        if not result:
            return []

        # Convertir el resultado a un formato más legible (lista de diccionarios)
        formatted_result = [
            {
                "productPricelistId": row[0],
                "productPricelistName": row[1],
                "productCategoryId": row[2],
                "productCategoryName": row[3],
            }
            for row in result
        ]

        return json.dumps(formatted_result)

    def get_price_list(self, companyId):
        # Inicializar la consulta SQL y los parámetros
        query = """
                   SELECT
                        product_pricelist.id,
                        product_pricelist.name,
                        product_pricelist.company_id
                    FROM
                        product_pricelist
                    WHERE
                    product_pricelist.company_id = %(companyId)s
        """
        # Inicializar la lista de parámetros
        params = {
            "companyId": companyId if companyId else -1,
        }

        query += """
            ORDER BY
                  product_pricelist.name;
        """
        # Ejecutar la consulta
        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()
        # Verificar si el resultado está vacío
        if not result:
            return []  # Retornar un arreglo vacío si no hay resultados

        # Convertir el resultado a un formato más legible (lista de diccionarios)
        formatted_result = [
            {
                "productPricelistId": row[0],
                "productPricelistName": row[1],
                "productCompanyId": row[2],
                "isActive": False,
            }
            for row in result
        ]

        return json.dumps(formatted_result)

    def get_product_by_ctegory(self, categ_id):
        # Obtener los productos de la categoría especificada
        products = self.env["product.template"].search([("categ_id", "=", categ_id)])
        # Formatear el resultado
        formatted_result = []
        for product in products:
            # Obtener el precio y costo del producto
            price = product.list_price  # Precio de venta
            cost = product.standard_price  # Costo
            barraValue = round(
                min(((price - cost) / cost * 100) if cost else 0.0, 100.0), 2
            )

            # Generar el HTML para la barra de progreso
            barra = f"""
            <div class="progress">
                <div class="progress-bar" role="progressbar"
                    style="width: {barraValue}%;"
                    aria-valuenow="{barraValue}"
                    aria-valuemin="0" aria-valuemax="100">
                    {barraValue}%
                </div>
            </div>
            """

            formatted_result.append(
                {
                    "productId": product.id,
                    "productName": product.name,
                    "price": price if price else 0.0,
                    "cost": cost if cost else 0.0,
                    "margin_percentage": barra,
                    "barraValue": barraValue,
                }
            )

        return json.dumps(formatted_result)
