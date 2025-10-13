# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)
# Ventas del día con detalles completos 
class SalesCustomController(http.Controller):
    @http.route('/api/sales_custom_queries/<string:order_number>', auth='public', methods=['GET'], type='http', cors='*', csrf=False)
    def get_sales_custom_queries(self,order_number, **kw):
        try:
            service = request.env['sales_custom_queries.service']
            result = service.sales_custom_queries_service(order_number)
            _logger.info(f"Resultado del servicio: {result}")    
            
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
