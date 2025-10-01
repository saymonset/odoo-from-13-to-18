from odoo import http


class Openai(http.Controller):
    @http.route('/chat-bot-n8n-ia/openai', type='json', auth='public')
    def list(self, **kw):
        records = http.request.env['reactodoo.micontacto'].sudo().search([])
        result = []
        # Llamar al método generar_descripcion_ai para cada registro
        for record in records:
            record.generar_descripcion_ai()
            result.append({
                'id': record.id,
                'name': record.display_name,
                'es_preferido': record.es_preferido,
                'descripcion_ai': record.descripcion_ai
            })
        return {
            'root': '/chat-bot-n8n-ia',
            'contacts': result,
            'saymon': 'Hola Saymon desde OpenAI',
        }
