from odoo import models, fields, api, exceptions
from ..repository.average_sales_repositoy import AverageSale
from ..services.info_user_company_service import user_company_service


class WizardDeliveryOrder(models.TransientModel):
    _name = "wizard.average.sales"
    _description = "Informe Promedio de Ventas y Margen de Ganancias"

    pricelist_ids = fields.Many2many("product.pricelist", string="Price Lists")
    expense_percentage = fields.Float(
        string="Porcentaje de Gasto", required=True, default=0.0
    )
    sql_result = fields.Json("SQL Result")  # Define sql_result as a JSON field
    user_company_info = fields.Json(
        "User Company Info"
    )  # Define user_company_info as a JSON field

    def print_report(self):
        # Verifica la restricción antes de continuar
        self._check_pricelist_limit()

        # Obtiene el resultado de AverageSale
        sql_result0 = AverageSale.average_sale(self)

        # Llama al servicio para obtener información del usuario y la compañía
        userCompany = user_company_service(self)

        # Asegúrate de que userCompany sea un diccionario
        if isinstance(userCompany, dict):
            self.user_company_info = userCompany  # Asigna el diccionario directamente
        else:
            raise exceptions.UserError(
                "La información del usuario y la compañía no es válida."
            )

        # Asigna directamente los diccionarios a los campos JSON
        self.user_company_info = userCompany  # Asigna el diccionario directamente
        self.sql_result = sql_result0  # Asigna el diccionario directamente
        return self.env.ref(
            "delivery_orders_report.action_average_sales_report"
        ).report_action(self)

    @api.constrains("expense_percentage")
    def _check_expense_percentage(self):
        """Verifica que expense_percentage sea un número válido."""
        for record in self:
            if not isinstance(record.expense_percentage, (int, float)):
                raise exceptions.ValidationError(
                    "El porcentaje de gasto debe ser un número válido."
                )

    @api.constrains("pricelist_ids")
    def _check_pricelist_limit(self):
        """Verifica que no se seleccionen más de dos listas de precios."""
        for record in self:
            if len(record.pricelist_ids) <= 0:
                raise exceptions.ValidationError(
                    "Por favor, seleccione una o mas listas de precios. ¡Gracias!"
                )
