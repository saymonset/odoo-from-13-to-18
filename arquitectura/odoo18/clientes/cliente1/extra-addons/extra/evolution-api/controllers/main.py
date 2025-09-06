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
        except Exception as e:
            return http.Response(
                json.dumps({'status': 'error', 'detail': 'JSON inválido', 'error': str(e)}),
                status=400,
                mimetype='application/json'
            )

        # Extraer información relevante
        remote_jid = data.get('data', {}).get('key', {}).get('remoteJid')
        message = data.get('data', {}).get('message', {}).get('conversation')
        apikey = data.get('apikey')
        instance = data.get('instance')

        respuesta = f"Hola, recibimos tu mensaje: '{message}'"

        payload = {
            "jid": remote_jid,
            "message": respuesta,
            "instance": instance,
            "apikey": apikey
        }

        evolution_url = "https://odoosaymon.evolution.jumpjibe.com/webhook/send-message"

        try:
            headers = {'Content-Type': 'application/json', 'apikey': apikey }
            resp = requests.post(evolution_url, data=json.dumps(payload), headers=headers, timeout=10)
            resp.raise_for_status()
            return http.Response(
                json.dumps({"status": "success", "detail": "Mensaje enviado"}),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            return http.Response(
                json.dumps({"status": "error", "detail": str(e)}),
                status=500,
                mimetype='application/json'
            )
        
   
        data = request.jsonrequest
        instance = request.env['evolution_api'].sudo().search([('name', '=', instance_name)], limit=1)
        if not instance:
            return {'error': 'Instancia no encontrada'}, 404

        event = data.get('event')
        if event == 'messages.upsert':
            # Procesar mensaje recibido
            messages = data.get('data', {}).get('messages', [])
            for msg in messages:
                sender = msg.get('key', {}).get('remoteJid', '').split('@')[0]
                text = msg.get('message', {}).get('conversation', '') or msg.get('message', {}).get('extendedTextMessage', {}).get('text', '')
                # Ejemplo: Registrar en chatter de un contacto (asumiendo res.partner con phone = sender)
                partner = request.env['res.partner'].sudo().search([('phone', '=', sender)], limit=1)
                if partner:
                    partner.message_post(body=_('Mensaje recibido de WhatsApp: %s') % text)
        elif event == 'connection.update':
            # Actualizar estado de conexión
            status = data.get('data', {}).get('state')
            if status:
                instance.update_status(status)  # Mapear a 'connected', etc.

        return {'status': 'ok'}