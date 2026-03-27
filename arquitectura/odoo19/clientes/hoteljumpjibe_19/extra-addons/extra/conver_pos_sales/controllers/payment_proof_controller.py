from odoo import http
from odoo.http import request

class PaymentProofController(http.Controller):

    @http.route('/payment_proof/get_transfer_provider_id', type='json', auth='public')
    def get_transfer_provider_id(self):
        provider = request.env['payment.provider'].sudo().search([('is_wire_transfer', '=', True)], limit=1)
        return provider.id if provider else 0