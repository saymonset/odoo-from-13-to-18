# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class TshirtInventario(http.Controller):

    @http.route('/api/products/<string:nombre_producto>', auth='public', methods=['GET'], type='http', cors='*', csrf=False)
    # El nombre_producto viene como path parametro y no como parameter despues del? que es clave valor
    def get_products(self,nombre_producto, **kw):
        """
        Endpoint que devuelve hasta 20 productos
        """
        try:
            service = request.env['product_name_.service']
            # nombre_producto = kw.get('nombre_producto', '')
            result = service.product_name_service(nombre_producto)
            _logger.info(f"Resultado del servicio: {result}")    
            #return result;
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'result': result
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error('Error en get_products: %s', str(e))
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
