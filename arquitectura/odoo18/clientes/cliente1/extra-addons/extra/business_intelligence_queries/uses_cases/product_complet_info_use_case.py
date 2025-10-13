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

class Product_complete_info_UseCase(models.TransientModel):
    _name = 'product_complet_info_use_case'
    _description = 'produt complet info Use Case'

    @api.model
    def execute(self, options)->dict:
        try:
            filter_search_term = options.get('search_term')
            # Consulta más simple
            query = """
                
                """
        
            params = []
                # Agregar filtro por nombre si se proporciona
            if filtro_nombre:
                #    query += " AND (COALESCE(pt.name->>'es_VE',pt.name->>'en_US') ILIKE %s)"
                #    params.append(f'%{filtro_nombre}%')
                
            # query += """
            #         GROUP BY pp.id, pp.default_code, pt.name
            #         ORDER BY valor_total_ventas DESC;
            #     """
            
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