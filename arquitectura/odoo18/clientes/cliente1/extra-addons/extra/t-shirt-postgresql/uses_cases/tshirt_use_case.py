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

class quantity_sell_total_sell_UseCase(models.TransientModel):
    _name = 'quantity_sell_total_sell.use.case'
    _description = 'quantity_sell_total_sell Use Case'

    @api.model
    def execute(self):
        try:
            
            # # Buscar hasta 20 productos
            products = request.env['product.product'].sudo().search([], limit=20)

            # # Preparar los datos
            products_data = []
            for product in products:
                products_data.append({
                    'id': product.id,
                    'name': product.name,  # nombre del producto
                    'template_name': product.product_tmpl_id.name,  # nombre de plantilla
                    'default_code': product.default_code or '',
                    'barcode': product.barcode or '',
                    'list_price': product.list_price,
                })
            

            # Implementa aquí la lógica real de verificación ortográfica
            # Por ahora devolvemos un ejemplo básaico
            return products_data

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}