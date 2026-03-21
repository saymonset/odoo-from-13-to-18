from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_usd_bcv = fields.Float(
        string='Precio USD (BCV)',
        digits=(12, 4),
        compute='_compute_usd_bcv',
        store=True
    )
    
    price_subtotal_usd_bcv = fields.Float(
        string='Subtotal USD (BCV)',
        digits=(12, 2),
        compute='_compute_usd_bcv',
        store=True
    )

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_usd_bcv(self):
        for line in self:
            # Obtener la tasa BCV más reciente
            rate = self.env['res.currency.rate'].search([
                ('currency_id.name', '=', 'VES'),
                ('company_id', '=', line.order_id.company_id.id),
            ], order='name desc', limit=1)
            
            if not rate or rate.rate == 0:
                line.price_usd_bcv = 0.0
                line.price_subtotal_usd_bcv = 0.0
                continue

            bcv_value = 1.0 / rate.rate
            line.price_usd_bcv = line.price_unit / bcv_value
            line.price_subtotal_usd_bcv = line.price_usd_bcv * line.product_uom_qty
