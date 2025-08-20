from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    pos_category_id = fields.Many2one("pos.category", string="Categoria por defecto")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_category_id = fields.Many2one(
        "pos.category", related="pos_config_id.pos_category_id", readonly=False
    )
