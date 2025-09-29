# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class TshirtInventario(http.Controller):

    @http.route('/api/tshirts', auth='public', methods=['GET'], type='http', cors='*', csrf=False)
    def get_products(self, **kwargs):
        """
        Endpoint que devuelve hasta 20 productos
        """
        try:
            # # Buscar hasta 20 productos
            # products = request.env['product.product'].sudo().search([], limit=20)

            # # Preparar los datos
            # products_data = []
            # for product in products:
            #     products_data.append({
            #         'id': product.id,
            #         'name': product.name,  # nombre del producto
            #         'template_name': product.product_tmpl_id.name,  # nombre de plantilla
            #         'default_code': product.default_code or '',
            #         'barcode': product.barcode or '',
            #         'list_price': product.list_price,
            #     })
             
            
            service = request.env['tshirt.service']
            result = service.quantity_sell_total_sell_service()
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
