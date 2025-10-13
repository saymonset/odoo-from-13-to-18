# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time
from odoo.http import request

_logger = logging.getLogger(__name__)

class Product_names_UseCase(models.TransientModel):
    _name = 'produt_name.use.case'
    _description = 'produt_name Use Case'

    @api.model
    def execute(self, options)->dict:
        try:
            filtro_nombre = options.get('nombre_producto')
            # Consulta más simple
            query = """
                SELECT 
                    pp.id,
                    pp.default_code as codigo,
                    COALESCE(pt.name->>'es_VE',pt.name->>'en_US') as nombre_producto,
                    SUM(sm.product_uom_qty) as cantidad_vendida,
                    AVG(sol.price_unit) as precio_promedio,
                    SUM(sol.price_unit * sm.product_uom_qty) as valor_total_ventas
                FROM stock_move sm
                INNER JOIN product_product pp ON sm.product_id = pp.id
                INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                INNER JOIN stock_picking sp ON sm.picking_id = sp.id
                INNER JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
                LEFT JOIN sale_order_line sol ON sm.sale_line_id = sol.id
                WHERE sm.state = 'done'  -- Movimientos completados
                AND spt.code = 'outgoing'  -- Solo salidas (ventas)
                """
        
            params = []
                # Agregar filtro por nombre si se proporciona
            if filtro_nombre:
                    query += " AND (COALESCE(pt.name->>'es_VE',pt.name->>'en_US') ILIKE %s)"
                    params.append(f'%{filtro_nombre}%')
                
            query += """
                    GROUP BY pp.id, pp.default_code, pt.name
                    ORDER BY valor_total_ventas DESC;
                """
            
            self.env.cr.execute(query, params)
            products_sql = self.env.cr.dictfetchall()
            
            # Preparar los datos
            products_data = []
            for product in products_sql:
                products_data.append({
                    'id': product['id'],
                    'name': product['nombre_producto'],
                    'template_name': product['nombre_producto'],  # mismo que name
                    'default_code': product['codigo'] or '',
                    'cantidad_vendida': product['cantidad_vendida'] or '',
                    'precio_promedio': product['precio_promedio'],
                    'valor_total_ventas': product['valor_total_ventas'],
                })
            

            # Implementa aquí la lógica real de verificación ortográfica
            # Por ahora devolvemos un ejemplo básaico
            return products_data

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}