# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)
# Ventas del día con detalles completos 
class DailySummaryQueriesController(http.Controller):
    @http.route('/api/daily_summary', auth='public', methods=['GET'], type='http', cors='*', csrf=False)
    def get_daily_summary_queries(self, **kw):
        try:
            service = request.env['daily_summary_queries.service']
             # Capturar parámetros de la URL
            date_from = kw.get('date_from')
            date_to = kw.get('date_to')
            specific_date = kw.get('specific_date')
            order_number = None
            result = service.daily_summary_queries_service(date_from, date_to, specific_date)
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
