from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    hide_unavailable_product = fields.Boolean("POS Hide Unavailable Product")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hide_unavailable_product = fields.Boolean(
        related="pos_config_id.hide_unavailable_product", readonly=False
    )
