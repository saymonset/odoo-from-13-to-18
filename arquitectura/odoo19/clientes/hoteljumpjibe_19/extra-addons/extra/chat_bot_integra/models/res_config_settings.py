# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    chat_bot_webhook_url = fields.Char(
        string="ChatBot Webhook URL",
        config_parameter="chat_bot_integra.webhook_url",
        help="Webhook URL used by the website chatbot."
    )