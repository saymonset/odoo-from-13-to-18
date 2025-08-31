from odoo import http


class Openai(http.Controller):
    @http.route('/react-odoo/openai', type='json', auth='public')
    def list(self, **kw):
        records = http.request.env['reactodoo.micontacto'].search([])
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
            'root': '/react-odoo',
            'contacts': result,
            'saymon': 'Hola Saymon desde OpenAI',
        }
        # return http.request.render(
        #     'react-odoo.listing',
        #     {
        #         'root': '/react-odoo',
        #         'objects': http.request.env['reactodoo.micontacto'].search([]),
        #         'saymon':'Hola Saymon desde OpenAI',
        #     },
        # )

    @http.route('/react-odoo/objects/<model("reactodoo.micontacto"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('react-odoo.object', {'object': obj})