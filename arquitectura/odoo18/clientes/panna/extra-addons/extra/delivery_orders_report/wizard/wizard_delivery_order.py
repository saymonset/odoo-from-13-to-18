from odoo import models, fields, exceptions
from ..repository.order_group_by_categ_repository import DeliveryCategoryGroup
from ..repository.order_repository import DeliveryOrerGroup
from ..services.info_user_company_service import user_company_service


class WizardDeliveryOrder(models.TransientModel):
    _name = "wizard.delivery.order"
    _description = "Wizard Informe de Órdenes de Entrega"

    name = fields.Char("Nombre")
    scheduled_date = fields.Date("Fecha Programada")
    # date_to = fields.Date("Hasta Fecha Programada")
    warehouse_ids = fields.Many2many("stock.warehouse", string="Almacén")
    place_of_delivery_ids = fields.Many2many("res.partner", string="Lugar de Entrega")
    stock_picking_type_ids = fields.Many2many(
        "stock.picking.type", string="Tipo de Transferencia"
    )
    # Este es la ubicación de origen del almacén
    stock_locations_ids = fields.Many2many("stock.location", string="Almacen de Origen")
    group_category = fields.Boolean("Agrupar por Categoria")

    sale_order_line_ids = fields.Many2many("sale.order.line", string="Lineas")
    group_category = fields.Boolean("Agrupar por Categoria")
    sql_result = fields.Json("SQL Result")  # Define sql_result as a JSON fiel
    user_company_info = fields.Json(
        "User Company Info"
    )  # Define user_company_info as a JSON field
    report_header = fields.Char(
        "Report Header", default="Tipo de Informe en la cabezera del reporte"
    )

    def print_report(self):
        # Llama al servicio para obtener información del usuario y la compañía
        userCompany = user_company_service(self)

        # Asegúrate de que userCompany sea un diccionario
        if isinstance(userCompany, dict):
            self.user_company_info = userCompany  # Asigna el diccionario directamente
        else:
            raise exceptions.UserError(
                "La información del usuario y la compañía no es válida."
            )

        if self.group_category:
            # Obtiene el resultado de AverageSale
            sql_result0 = DeliveryCategoryGroup.delivery_category_group(self)
            self.sql_result = sql_result0  # Asigna el diccionario directamente
            self.report_header = "categoria"
            return self.env.ref(
                "delivery_orders_report.action_report_wizard_category_report"
            ).report_action(self)
        else:
            print("Agrupar por Orden de entrega")
            sql_result0 = DeliveryOrerGroup.delivery_order_group(self)
            self.sql_result = sql_result0  # Asigna el diccionario directamente
            self.report_header = "orden_entrega"
            return self.env.ref(
                "delivery_orders_report.action_report_wizard_order"
            ).report_action(self)

    def get_category_name(self, id):
        if not id:
            return False
        return self.env["product.category"].browse(id).name or False
