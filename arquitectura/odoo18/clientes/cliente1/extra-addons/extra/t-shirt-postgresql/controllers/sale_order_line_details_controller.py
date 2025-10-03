# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLineDetailsController(http.Controller):

    #@http.route('/api/sale_order_linea_details/<string:nombre_producto>', auth='public', methods=['GET'], type='http', cors='*', csrf=False)
    #def get_products(self,nombre_producto, **kw):
  
    @http.route('/api/sale_order_linea_details', auth='public', methods=['GET'], type='http', cors='*', csrf=False)
    def get_sale_order_detail(self, **kw):
        """
        Endpoint que devuelve hasta 20 productos
        """
        try:
            service = request.env['sale_order_line.service']
            nombre_producto = kw.get('nombre_producto', '')
            result = service.sale_order_line_service(nombre_producto)
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
