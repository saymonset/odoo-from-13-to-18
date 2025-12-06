from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_usd_bcv = fields.Float(
        string='Precio USD (BCV)',
        digits=(12, 4),
        compute='_compute_price_usd_bcv',
        store=False
    )
    
    price_subtotal_usd_bcv = fields.Float(
        string='Subtotal USD (BCV)',
        digits=(12, 4),
        compute='_compute_price_subtotal_usd_bcv',
        store=False
    )

    bcv_rate_value = fields.Float(
        string="Tasa BCV",
        digits=(12, 4),
        compute='_compute_price_usd_bcv',
        store=False
    )

    @api.depends('price_unit')
    def _compute_price_usd_bcv(self):
        """
        Convierte el precio unitario a USD según la tasa oficial BCV.
        """
        for line in self:
            line.price_usd_bcv = 0
            line.bcv_rate_value = 0

            # Buscar la tasa BCV más reciente
            rate = self.env['res.currency.rate'].search([
                ('currency_id.name', '=', 'VES'),
                ('company_id', '=', line.order_id.company_id.id),
            ], order='name desc', limit=1)

            if not rate or rate.rate == 0:
                continue

            # Calculamos la tasa directa (1 USD = X VES)
            bcv_value = 1.0 / rate.rate
            line.bcv_rate_value = bcv_value

            # Convierte el precio_unit a USD
            line.price_usd_bcv = line.price_unit / bcv_value
    
    @api.depends('price_usd_bcv', 'product_uom_qty')
    def _compute_price_subtotal_usd_bcv(self):
        """
        Calcula el subtotal en USD (precio USD * cantidad)
        """
        for line in self:
            line.price_subtotal_usd_bcv = line.price_usd_bcv * line.product_uom_qty