# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class WhatsAppWebhook(http.Controller):
    
    @http.route('/webhook/messages-upsert', type='http', auth='none', methods=['POST'], csrf=False)
    def handle_messages_upsert(self, **kw):
        # Intenta obtener el JSON del cuerpo
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info("data: %s", str(data))
            service = http.request.env['evolution.service']
            info = service.getInfo(data)
           # serviceIA = http.request.env['gpt.service']
          #  result = serviceIA.orthography_check('ola mundo', max_tokens=100)
            return info
        
        except Exception as e:
            return http.Response(
                json.dumps({'status': 'error', 'detail': 'JSON inválido', 'error': str(e)}),
                status=400,
                mimetype='application/json'
            )
    @http.route('/webhook/n8n-messages-upsert', type='http', auth='none', methods=['POST'], csrf=False)
    def handle_n8n_messages_upsert(self, **kw):
        # Intenta obtener el JSON del cuerpo
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info("data: %s", str(data))
            service = http.request.env['evolution.service']
            info = service.getInfo(data)
           # serviceIA = http.request.env['gpt.service']
          #  result = serviceIA.orthography_check('ola mundo', max_tokens=100)
            return info
        
        except Exception as e:
            return http.Response(
                json.dumps({'status': 'error', 'detail': 'JSON inválido', 'error': str(e)}),
                status=400,
                mimetype='application/json'
            )

        
        
        
        
        
         
        
   
         