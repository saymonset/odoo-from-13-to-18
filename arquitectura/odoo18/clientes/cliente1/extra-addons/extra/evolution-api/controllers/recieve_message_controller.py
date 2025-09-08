# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class WhatsAppWebhook(http.Controller):
    
    @http.route('/webhook/n8n-messages-upsert', type='http', auth='public', methods=['POST'], csrf=False)
    def handle_n8n_messages_upsert(self, **kw):
        # Intenta obtener el JSON del cuerpo
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info("data: %s", str(data))
            service = request.env['evolution.service'].sudo()
            info = service.getInfo(data)
           # serviceIA = http.request.env['gpt.service']
          #  result = serviceIA.orthography_check('ola mundo', max_tokens=100)
          # O usando el método auxiliar
            #whatsapp_record = request.env['model.info_whats_app'].sudo().create_from_dto(info)
            
            # Forzar el commit de la transacción
            whatsapp_record = request.env['model.info_whats_app'].sudo().create_from_dto(info)
            request.env.cr.commit()  # Confirmar la transacción explícitamente
            
            _logger.info("Record created successfully with ID: %s", whatsapp_record.id)
            
            # Verificar que el registro existe realmente
            record_exists = request.env['model.info_whats_app'].sudo().search([('id', '=', whatsapp_record.id)])
            _logger.info("Record verification - exists: %s", bool(record_exists))
            
            
            return info
        
        except Exception as e:
            return http.Response(
                json.dumps({'status': 'error', 'detail': 'JSON inválido', 'error': str(e)}),
                status=400,
                mimetype='application/json'
            )

        
        
        
        
        
         
        
   
         