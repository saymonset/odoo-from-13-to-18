# Copyright (C) Wisenetic Technologies.
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_pos_logo = fields.Boolean(
        related="pos_config_id.enable_pos_logo", readonly=False
    )
    custom_logo = fields.Binary(related="pos_config_id.custom_logo", readonly=False)
    logo_option = fields.Selection(related="pos_config_id.logo_option", readonly=False)

    enable_saver_background = fields.Boolean(
        related="pos_config_id.enable_saver_background", readonly=False
    )
    saver_background = fields.Binary(
        related="pos_config_id.saver_background", readonly=False
    )
    timer_color = fields.Char(related="pos_config_id.timer_color", readonly=False)
