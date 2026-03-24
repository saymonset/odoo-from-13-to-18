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
        #usd = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        usd = self.env.ref('base.USD', raise_if_not_found=False)
        if not usd:
            # Podemos usar _logger para advertencia o asignar None
            # y en el campo amount_total_usd manejar el caso.
            # Por simplicidad, puedes lanzar un UserError o simplemente no asignar.
            # Aquí elegimos asignar None y luego en amount_total_usd poner 0 si currency_aux es None.
            usd = None
        
        for order in self:
            order.currency_aux = usd
