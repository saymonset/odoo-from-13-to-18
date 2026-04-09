from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_usd_bcv = fields.Float(
        string='Precio USD (BCV)',
        digits=(12, 4),
        readonly=True
    )

    bcv_rate_value = fields.Float(
        string='Tasa BCV',
        digits=(12, 4),
        readonly=True
    )

    @api.model
    def create(self, vals):
        line = super(AccountMoveLine, self).create(vals)
        # Copiar precio USD(BCV) si viene de la línea de venta
        if 'sale_line_ids' in vals and vals['sale_line_ids']:
            sale_line = self.env['sale.order.line'].browse(vals['sale_line_ids'][0][2][0])
            line.price_usd_bcv = sale_line.price_usd_bcv
            line.bcv_rate_value = sale_line.bcv_rate_value
        return line