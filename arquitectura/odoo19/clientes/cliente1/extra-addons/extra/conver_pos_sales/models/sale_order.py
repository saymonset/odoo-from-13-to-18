from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Campos en el pedido (NO en las líneas)
    price_usd_bcv = fields.Float(
        string='Precio USD (BCV)',
        digits=(12, 4),
        compute='_compute_price_usd_bcv_total',
        store=True
    )

    bcv_rate_value = fields.Float(
        string="Tasa BCV",
        digits=(12, 4),
        compute='_compute_bcv_rate_global',
        store=False
    )
    
    currency_aux = fields.Many2one(
        'res.currency',
        string='Moneda Auxiliar USD',
        compute='_compute_currency_aux',
        store=True
    )
    
    @api.depends('currency_id')
    def _compute_currency_aux(self):
        for order in self:
            usd = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            order.currency_aux = usd or order.currency_id
    
    def _compute_bcv_rate_global(self):
        for order in self:
            # Buscar la tasa BCV más reciente
            rate = self.env['res.currency.rate'].search([
                ('currency_id.iso_code', '=', 'VES'),
                ('company_id', '=', order.company_id.id),
            ], order='name desc', limit=1)
            
            if rate and rate.rate != 0:
                order.bcv_rate_value = 1.0 / rate.rate
            else:
                order.bcv_rate_value = 0.0
    
    def _compute_price_usd_bcv_total(self):
        for order in self:
            order.price_usd_bcv = sum(line.price_usd_bcv for line in order.order_line)