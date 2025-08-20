# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hide_in_receipt = fields.Boolean(string="Hide In Receipt ?")


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ["hide_in_receipt"]
        return params
