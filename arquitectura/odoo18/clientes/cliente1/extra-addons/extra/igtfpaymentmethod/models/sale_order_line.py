# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Define a computed field for USD currency that cannot be changed
    currency_aux = fields.Many2one('res.currency', 
        string='Reference Currency',
        compute='_compute_currency_ref',
        store=True)

    price_unit_ref = fields.Monetary(
        string='Precio Unitario Ref',
        compute='_compute_price_unit_ref',
        store=True,
        currency_field='currency_aux'  # Changed to use currency_ref
    )
    
    price_subtotal_ref = fields.Monetary(
        string='Subtotal Ref',
        compute='_compute_price_subtotal_ref',
        store=True,
        currency_field='currency_aux'  # Changed to use currency_ref
    )

    @api.depends()
    def _compute_currency_ref(self):
        """Always set USD as reference currency"""
        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        for line in self:
            line.currency_aux = usd_currency

    @api.depends('price_unit', 'order_id.pricelist_id.currency_id')
    def _compute_price_unit_ref(self):
        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        for line in self:
            if line.order_id.pricelist_id.currency_id:
                try:
                    line.price_unit_ref = line.order_id.pricelist_id.currency_id._convert(
                        line.price_unit,
                        usd_currency,
                        line.order_id.company_id,
                        fields.Date.today()
                    )
                except Exception:
                    line.price_unit_ref = 0.0

    @api.depends('price_subtotal', 'order_id.pricelist_id.currency_id')
    def _compute_price_subtotal_ref(self):
        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        for line in self:
            if line.order_id.pricelist_id.currency_id:
                try:
                    line.price_subtotal_ref = line.order_id.pricelist_id.currency_id._convert(
                        line.price_subtotal,
                        usd_currency,
                        line.order_id.company_id,
                        fields.Date.today()
                    )
                except Exception:
                    line.price_subtotal_ref = 0.0
