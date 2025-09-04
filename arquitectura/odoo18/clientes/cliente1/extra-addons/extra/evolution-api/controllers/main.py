from odoo import http


class Main(http.Controller):
    @http.route('/evolution-api/objects', type='http', auth='public')
    def list(self, **kw):
        return http.request.render(
            'evolution-api.listing',
            {
                'root': '/evolution-api',
                'objects': http.request.env['main'].search([]),
            },
        )

    @http.route('/evolution-api/objects/<model("main"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('evolution-api.object', {'object': obj})