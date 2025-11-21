from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    n8n_webhook_url = fields.Char(
        string='URL Webhook n8n Reportes Médicos',
        config_parameter='medical_report.n8n_webhook_url',
        help='URL del webhook de n8n para enviar reportes médicos'
    )