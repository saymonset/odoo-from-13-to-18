# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError

class conversion(models.Model):
    # _inherit = 'pos.order'
    _name = 'conversion.conversion'
    _description = 'conversion'
    _order = 'id desc'

    name = fields.Char(string="Name", default="Valor  del Dolar")  # Campo tipo string
    dateCurrency = fields.Date(string="Currency Date")  # Campo tipo fecha
   # mount = fields.Float(string="Amount", digits=(16, 2))  # Campo tipo float con dos decimales
    currency_id = fields.Many2one('res.currency', string='Tipo de moneda', default=lambda self: self.env.company.currency_id.id)
    rent_amount = fields.Monetary('Rent Amount', help="Enter rent amount per month") 
    
    # def compute_custom_tax_totals(self):
    #     # Ejemplo de cálculo personalizado
    #     for order in self:
    #         order.custom_tax_total = sum(line.price_subtotal for line in order.lines) * 0.1  # 10% de impuestos


