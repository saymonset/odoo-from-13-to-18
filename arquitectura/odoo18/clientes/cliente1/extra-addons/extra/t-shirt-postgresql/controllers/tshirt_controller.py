# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import json
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

class TshirtInventario(http.Controller):
    
    @http.route('/test', auth='public', methods=['GET'], type='http', cors='*', csrf=False)
    def test_api(self, **kwargs):
        """Endpoint simple de prueba"""
        return http.Response(
            json.dumps({'status': 'API is working', 'timestamp': datetime.now().isoformat()}),
            content_type='application/json',
            headers={'Access-Control-Allow-Origin': '*'}
        )
    #@http.route('/api/tshirts',type='http', auth='public',csrf=False)
    @http.route('/api/tshirts', auth='public', methods=['GET'], type='http', cors='*', csrf=False)
    #@http.route('/api/tshirts', auth='public', methods=['GET'], type='http', csrf=False, website=False)
    def get_top10_tshirts(self, **kwargs):
        """
        Endpoint que devuelve los 10 registros principales de camisetas
        """
        try:
            # Buscar las 10 camisetas principales
            tshirts = request.env['product.product'].search([
                ('categ_id.name', 'ilike', 'camiseta')
            ], limit=10)
            
            # Preparar los datos para JSON
            tshirts_data = []
            for tshirt in tshirts:
                tshirts_data.append({
                    'id': tshirt.id,
                    'name': tshirt.name,
                    'default_code': tshirt.default_code or '',
                    'barcode': tshirt.barcode or '',
                    'list_price': tshirt.list_price,
                    'qty_available': tshirt.qty_available,
                    'category': tshirt.categ_id.name if tshirt.categ_id else '',
                    'image_url': f'/web/image/product.product/{tshirt.id}/image_128' if getattr(tshirt, 'image_128', False) else ''

                })
            
            # Devolver como JSON
            return request.make_response(
                json.dumps({
                    'success': True,
                    'count': len(tshirts_data),
                    'tshirts': tshirts_data
                }),
                headers=[('Content-Type', 'application/json')]
            )
            
        except Exception as e:
            _logger.error('Error en get_top10_tshirts: %s', str(e))
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=500
            )