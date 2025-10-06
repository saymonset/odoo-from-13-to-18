# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class ProcesarMessageController(http.Controller):
    @http.route('/webhook/procesar-messages', type='http', auth='public', methods=['POST'], csrf=False)
    def handle_n8n_messages_upsert(self, **kw):
        # Intenta obtener el JSON del cuerpo
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info("data: %s", str(data))
            service = request.env['procesar_mensaje.service'].sudo()
            #Informacion de evolution api ya procesada la info
            info = service.getInfo(data)
            
            
            # Ahora la URL usa tu instancia "odoosaymon"
            evolution_url = f"https://evolution.jumpjibe.com/message/sendText/{info.get('instance')}"
            payload = {
            "number": info.get('client_phone'),
             "text": (
                        f"host_phone: {info.get('host_phone')}\n"
                        f"instance: {info.get('instance')}\n"
                        f"message_type: {info.get('message_type')}\n"
                        f"conversation: {info.get('conversation')}"
                    )
         }
            _logger.info("payload: %s", str(payload))
            _logger.info("payload: %s", str(payload))
            
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

        
        
        
        
        
         
        
   
         