from odoo import http
import logging

_logger = logging.getLogger(__name__)

class GptController(http.Controller):

    @http.route('/react-odoo/gpt',type='json', auth='public',csrf=False)
    def gpt(self, **kw):
        try:
            prompt = kw.get('prompt', '')
            if not prompt:
                return {'error': 'No prompt provided'}
            
            service = http.request.env['gpt.service']
            result = service.orthography_check(prompt)
            return result
        except Exception as e:
            return {'error': str(e)}