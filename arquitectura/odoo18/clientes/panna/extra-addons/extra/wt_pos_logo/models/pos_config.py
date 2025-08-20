# Copyright (C) Wisenetic Technologies.
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_pos_logo = fields.Boolean(string="POS Logo")
    custom_logo = fields.Binary(string="Upload Logo")
    logo_option = fields.Selection(
        [("company", "Company"), ("custom", "Custom Image"), ("none", "No Logo")],
        string="Disable POS Logo Option",
        default="company",
    )
    enable_saver_background = fields.Boolean(string="Screen Saver Background")
    saver_background = fields.Binary(string="Screen Saver Background")
    timer_color = fields.Char("Timer Color", default="#495057")
