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
            #Informacion de evolution api ya procesada la info
            info = service.getInfo(data)
           # serviceIA = http.request.env['gpt.service']
          #  result = serviceIA.orthography_check('ola mundo', max_tokens=100)
        
            
            
            # Buscamos por cliente el último registro para obtener el threadid  < a 48 horas, si no creamos uno nuevo
            service_info_whats_app = request.env['model_info_whats_app.service'].sudo()
            #Hilo de conversación de IA
            serviceIA = http.request.env['dixon.service']
            threadId = service_info_whats_app.getLastRecordInfo(info)
            if not threadId:
                id = serviceIA.createThread(None)
                threadId = id.get('id')
                _logger.info("Nuevo threadId creado: %s", str(threadId)) 
           
           
            question = info.get('conversation', '')
            
            serviceIA.createMessage(threadId,question)
            
            run = serviceIA.createRun(threadId)
            
            result = serviceIA.checkCompleteStatusRun(threadId,run.id)
            
            messages = serviceIA.getMessageList(threadId)
            
            respAssistentIA= messages[-1] if messages else {}
            
            messageIA = respAssistentIA.get('content', 'No response from AI')
            
            info['conversation_ia'] = messageIA
            
            info['thread_id'] = threadId
            
            service_info_whats_app = request.env['model_info_whats_app.service'].sudo()
            
            info = service_info_whats_app.getSaveData(info)
            
            
            
            
            
            return info
        
        except Exception as e:
            return http.Response(
                json.dumps({'status': 'error', 'detail': 'JSON inválido', 'error': str(e)}),
                status=400,
                mimetype='application/json'
            )

        
        
        
        
        
         
        
   
         