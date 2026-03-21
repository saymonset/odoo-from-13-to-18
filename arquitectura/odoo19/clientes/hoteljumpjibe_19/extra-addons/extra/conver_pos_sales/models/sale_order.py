from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    currency_aux = fields.Many2one(
        'res.currency',
        string='Moneda Auxiliar USD',
        compute='_compute_currency_aux',
        store=True
    )

    amount_total_usd = fields.Monetary(
        string='Total USD (BCV)',
        currency_field='currency_aux',
        compute='_compute_amount_total_usd',
        store=True
    )

    @api.depends('order_line.price_subtotal_usd_bcv')
    def _compute_amount_total_usd(self):
        for order in self:
            order.amount_total_usd = sum(line.price_subtotal_usd_bcv for line in order.order_line)

    @api.depends('currency_id')
    def _compute_currency_aux(self):
        usd = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        for order in self:
            order.currency_aux = usd or order.currency_id
