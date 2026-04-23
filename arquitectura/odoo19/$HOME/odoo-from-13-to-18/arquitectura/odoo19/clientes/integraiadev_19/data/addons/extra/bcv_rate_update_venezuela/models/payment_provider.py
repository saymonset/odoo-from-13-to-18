from odoo import fields, models

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    is_wire_transfer = fields.Boolean(string="Es transferencia bancaria")