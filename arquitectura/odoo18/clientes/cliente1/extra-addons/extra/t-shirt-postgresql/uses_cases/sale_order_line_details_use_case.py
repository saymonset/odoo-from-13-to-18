# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time
from datetime import datetime
from odoo.http import request

_logger = logging.getLogger(__name__)

class Sale_order_line_details_UseCase(models.TransientModel):
    _name = 'Sale_order_line_details.use.case'
    _description = 'Sale_order_line_details Use Case'

    @staticmethod
    def format_date(date_value):
        """Método estático para formatear fechas"""
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        elif isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            except:
                return date_value
        return ''
    
    @api.model
    def execute(self, options)->dict:
        try:
            filtro_nombre = options.get('nombre_producto')
            # Consulta más simple
            query = """
                        SELECT 
                            so.name as order_number,
                            so.date_order as order_date,
                            partner.name as customer_name,
                            shipping_address.street as shipping_street,
                            shipping_address.city as shipping_city,
                            shipping_address.state_id as shipping_state,
                            shipping_address.country_id as shipping_country,
                            pt.name as product_name,
                            sol.product_uom_qty as quantity,
                            sol.price_unit as unit_price,
                            sol.price_subtotal as subtotal
                        FROM 
                            sale_order so
                        JOIN 
                            res_partner partner ON so.partner_id = partner.id
                        LEFT JOIN 
                            res_partner shipping_address ON so.partner_shipping_id = shipping_address.id
                        JOIN 
                            sale_order_line sol ON so.id = sol.order_id
                        JOIN 
                            product_product product ON sol.product_id = product.id
                        JOIN 
                            product_template pt ON product.product_tmpl_id = pt.id

                """
        
            params = []
            # Agregar filtro por nombre si se proporciona
            if filtro_nombre:
                None
                #    query += " AND (COALESCE(pt.name->>'es_VE',pt.name->>'en_US') ILIKE %s)"
                #    params.append(f'%{filtro_nombre}%')
                
            query += """
                   ORDER BY so.id, sol.id;
                """
            
            self.env.cr.execute(query, params)
            products_sql = self.env.cr.dictfetchall()
            
            # Preparar los datos
            products_data = []
            for product in products_sql:
                products_data.append({
                    'order_number': product['order_number'],
                    'order_date': self.format_date(product['order_date']),  # Ahora funciona
                    'customer_name': product['customer_name'],
                    'shipping_street': product['shipping_street'] or '',
                    'shipping_city': product['shipping_city'] or '',
                    'shipping_state': product['shipping_state'],
                    'shipping_country': product['shipping_country'],
                    'product_name': product['product_name'],
                    'quantity': product['quantity'],
                    'unit_price': product['unit_price'],
                    'subtotal': product['subtotal'],
                })
  
            return products_data
            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}