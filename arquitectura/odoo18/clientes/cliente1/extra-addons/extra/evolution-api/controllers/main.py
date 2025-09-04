from odoo import http
from odoo.http import request

class WhatsAppWebhook(http.Controller):
    @http.route('/whatsapp/webhook/<string:instance_name>', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_webhook(self, instance_name):
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