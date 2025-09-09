# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class WhatsAppWebhook(http.Controller):
    #https://n8n.jumpjibe.com/webhook/webhook0
    #@http.route('/webhook/n8n-messages-upsert', type='http', auth='public', methods=['POST'], csrf=False)
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
           
            threadId = service_info_whats_app.getLastRecordInfo(info)
            
            
            
            #Hilo de conversación de IA
            serviceIA = http.request.env['dixon.service']
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
            
            
            
            # Ahora la URL usa tu instancia "odoosaymon"
            evolution_url = f"https://evolution.jumpjibe.com/message/sendText/{info.get('instance')}"
            payload = {
            "number": info.get('client_phone'),
            "text": info.get('conversation_ia') 
         }
            try:
                headers = {'Content-Type': 'application/json', 'apikey': info.get('apikey')}
                resp = requests.post(evolution_url, json=payload, headers=headers, timeout=10)
                resp.raise_for_status()
                return http.Response(
                    json.dumps({"status": "success", "detail": "Mensaje enviado"}),
                    status=200,
                    mimetype='application/json'
                )
            except Exception as e:
                _logger.error("Error enviando mensaje a Evolution: %s", str(e))
                return http.Response(
                    json.dumps({"status": "error", "detail": str(e)}),
                    status=500,
                    mimetype='application/json'
                )
            
            
            
            
            
            return info
        
        except Exception as e:
            return http.Response(
                json.dumps({'status': 'error', 'detail': 'JSON inválido', 'error': str(e)}),
                status=400,
                mimetype='application/json'
            )

        
        
        
        
        
         
        
   
         