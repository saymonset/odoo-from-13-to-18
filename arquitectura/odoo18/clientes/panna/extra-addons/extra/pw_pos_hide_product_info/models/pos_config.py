from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    pw_hide_product_info = fields.Boolean(string="Hide Product Info")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pw_hide_product_info = fields.Boolean(
        related="pos_config_id.pw_hide_product_info", readonly=False
    )
