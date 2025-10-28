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

class SalesCustomQueriesUCase(models.TransientModel):
    _name = 'sales_custom_queries.use.case'
    _description = 'sales_custom_queries Use Case'

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
            filtro_order_number = options.get('order_number')
            filtro_fecha = options.get('fecha')  # Opcional: '2024-01-15'
            # Consulta más simple
            query = """
                      SELECT 
                            so.name as numero_pedido,
                            rp.name as cliente,
                            so.amount_total as total,
                            so.date_order as fecha_pedido,
                            so.amount_untaxed as subtotal,
                            so.amount_tax as impuestos,
                            so.state as estado,
                            rp_comercial.name as comercial,
                            so.validity_date as fecha_vencimiento
                        FROM sale_order so
                        INNER JOIN res_partner rp ON so.partner_id = rp.id
                        LEFT JOIN res_partner rp_comercial ON so.user_id = rp_comercial.id
                        
                """
        
            params = []
            
             # Agregar filtro por fecha si se proporciona     
            if filtro_fecha:
                query += " AND DATE(so.date_order) = DATE(%s) "
                params.append(filtro_fecha)
            else:
                query += " AND DATE(so.date_order) = CURRENT_DATE "
                
            # Agregar filtro por nombre si se proporciona
            if filtro_order_number:
                # WHERE DATE(so.date_order) = CURRENT_DATE
                #             
                #         
                    query += " AND so.state NOT IN ('cancel', 'draft') "
                    #params.append(f'%{filtro_order_number}%')
                
            query += """
                   ORDER BY so.date_order DESC;  
                """
            
            self.env.cr.execute(query, params)
            result_sql = self.env.cr.dictfetchall()
            
            # Preparar los datos
            result_data = []
            for result in result_sql:
                result_data.append({
                    'numero_pedido': result['numero_pedido'],
                    'cliente': result['cliente'],
                    'total': result['total'],
                    'fecha_pedido': self.format_date(result['fecha_pedido']),  # Ahora funciona
                    'fecha_vencimiento': self.format_date(result['fecha_vencimiento']),  # Ahora funciona
                    'subtotal': result['subtotal'],
                    'impuestos': result['impuestos'] or '',
                    'estado': result['estado'] or '',
                    'comercial': result['comercial'],
                })
  
            return result_data
            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}