# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
       # Define a computed field for USD currency that cannot be changed
    currency_ref = fields.Many2one('res.currency', 
        string='Reference Currency',
        compute='_compute_currency_ref',
        store=True)

    #price_total_ref = fields.Float(string='Total', digits='Product Price', default=0.0)
    price_total_ref = fields.Float(
        digits='Product Price', default=0.0,
        string='Total Referencia',
        compute='_compute_price_total_ref',
        store=True,
        currency_field='currency_ref' 
    )
    
    
    
    
    def action_update_prices(self):
        self.ensure_one()
        self.onchange_pricelist_id()
        # Aquí puedes agregar la lógica para refrescar la vista
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
        total_ref = 0.0
        for order in self:
            #Recuperamos la moneda actual de la orden
            from_currency = order.pricelist_id.currency_id
            #Buscamos la moneda USD
            to_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            # Llama al método _recompute_prices para actualizar los precios
            order._recompute_prices()
            #Si hay un valor valido en el campo pricelist_id que es el select para escojer moneda entonces
            if order.pricelist_id:
                #Buscamos cada linea de orden 
                for line in order.order_line:
                    currency_id = order.pricelist_id.currency_id
                    
                    if currency_id.name != 'USD':
                        #Clculamos el valor en USD de precio unitario y lo colocamos en price_unit_ref
                        line.price_unit_ref =self.convert_price_to_currency(line.price_unit, from_currency, to_currency)
                       # line.price_unit_ref = price_unit_in_usd
                        
                        price_subtotal_in_usd = self.convert_price_to_currency(line.price_subtotal, from_currency, to_currency)
                        line.price_subtotal_ref = price_subtotal_in_usd
                        total_ref += price_subtotal_in_usd
                        # Asigna el total de referencia al pedido
                        order.price_total_ref = total_ref
                    else:
                        line.price_unit_ref = line.price_unit  
                        line.price_subtotal_ref = line.price_subtotal
                        total_ref += line.price_subtotal
                        # Asigna el total de referencia al pedido
                        order.price_total_ref = total_ref
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
                
                
            
                

    def _recompute_prices(self):
        lines_to_recompute = self.order_line
        lines_to_recompute.invalidate_recordset(['pricelist_item_id'])
        lines_to_recompute.with_context(force_price_recomputation=True)._compute_price_unit()
        # Restablece el descuento a 0.0
        lines_to_recompute.discount = 0.0
        lines_to_recompute._compute_discount()
        self.show_update_pricelist = False

    @api.model
    def convert_price_to_currency(self, price_unit, from_currency, to_currency):
        """
        Convierte un precio unitario de una moneda a otra utilizando los tipos de cambio.

        :param price_unit: Precio unitario a convertir.
        :param from_currency: Moneda de origen (objeto currency_id).
        :param to_currency: Moneda de destino (objeto currency_id).
        :return: Precio convertido a la moneda de destino.
        """
        if from_currency == to_currency:
            # Si las monedas son iguales, no se realiza conversión
            return price_unit

        # Obtiene los tipos de cambio
        exchange_rate_to_currency = self._get_exchange_rate(to_currency)
        exchange_rate_from_currency = self._get_exchange_rate(from_currency)

        # Calcula el precio convertido
        converted_price = price_unit * (exchange_rate_to_currency / exchange_rate_from_currency)
        return converted_price
    
    def _get_exchange_rate(self, currency):
        # Asegúrate de que el objeto currency es válido
        if not currency:
            return 1.0  # Retorna 1.0 si no hay moneda

        # Busca la moneda en la base de datos
        currency_record = self.env['res.currency'].search([('id', '=', currency.id)], limit=1)
        
        if currency_record:
            # Retorna el tipo de cambio a USD
            return currency_record.rate  # Asegúrate de que 'rate' es el campo correcto que contiene el tipo de cambio
        else:
            return 1.0  # Valor por defecto si no se encuentra la moneda
 # Cambia esto por la lógica real
    
    @api.depends('order_line.price_subtotal_ref')
    def _compute_price_total_ref(self):
        for order in self:
            order.price_total_ref = sum(line.price_subtotal_ref for line in order.order_line)
    
    @api.depends()
    def _compute_currency_ref(self):
        """Always set USD as reference currency"""
        #usd_currency = self.env.ref('base.USD')
        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        for line in self:
            line.currency_ref = usd_currency