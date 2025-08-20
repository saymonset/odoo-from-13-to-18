from odoo import models, api


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def _load_pos_data_fields(self, config_id):
        list_fields = super()._load_pos_data_fields(config_id)
        list_fields.append("sequence")
        return list_fields
