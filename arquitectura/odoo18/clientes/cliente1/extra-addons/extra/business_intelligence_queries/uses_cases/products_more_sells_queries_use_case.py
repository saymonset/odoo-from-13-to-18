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

class ProductsMoreSellsUCase(models.TransientModel):
    _name = 'products_more_sells_queries.use.case'
    _description = 'products_more_sells_queries_use_case Use Case'

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
                            pt.name as producto,
                            pc.name as categoria,
                            SUM(sol.product_uom_qty) as cantidad_vendida,
                            SUM(sol.price_subtotal) as total_ventas,
                            ROUND(
                                AVG(
                                    sol.price_unit - 
                                    CASE 
                                        WHEN pp.standard_price IS NULL THEN 0
                                        WHEN jsonb_typeof(pp.standard_price) = 'number' THEN (pp.standard_price->>0)::numeric
                                        ELSE 0
                                    END
                                ), 2
                            ) as margen_promedio
                        FROM sale_order_line sol
                        INNER JOIN product_product pp ON sol.product_id = pp.id
                        INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                        LEFT JOIN product_category pc ON pt.categ_id = pc.id
                        INNER JOIN sale_order so ON sol.order_id = so.id   
                """
        
            params = []
            
             # Agregar filtro por fecha si se proporciona     
            if filtro_fecha:
                query += " AND DATE(so.date_order) >= DATE(%s) - INTERVAL '30 days'   "
                params.append(filtro_fecha)
            else:
                query += " AND DATE(so.date_order) >= DATE(CURRENT_DATE) - INTERVAL '30 days'"
                
            # Agregar filtro por nombre si se proporciona
            if filtro_order_number:
                    query += " AND so.state NOT IN ('cancel', 'draft') "
                
            query += """
                    GROUP BY pt.name, pc.name
                    ORDER BY cantidad_vendida DESC
                    LIMIT 15;
                """
            
            self.env.cr.execute(query, params)
            result_sql = self.env.cr.dictfetchall()
            
            # Preparar los datos
            result_data = []
            for result in result_sql:
                result_data.append({
                    'producto': result['producto'],
                    'categoria': result['categoria'],
                    'cantidad_vendida': result['cantidad_vendida'],
                    'total_ventas': result['total_ventas'],
                    'margen_promedio': result['margen_promedio'],
                })
  
            return result_data
            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}