# services/openai_service.py
import logging
from odoo import api, models, _
from odoo.exceptions import UserError, ValidationError

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

_logger = logging.getLogger(__name__)

class OpenAIService(models.TransientModel):
    _name = 'openai.service'
    _description = 'OpenAI Service Layer'

    @api.model
    def _get_openai_client(self):
        api_key = self.env['openai.config'].sudo().search([('active', '=', True)], limit=1).api_key
        if not api_key:
            None
            raise ValidationError(_('Configura la clave de API de OpenAI en Ajustes.'))
        return OpenAI(api_key=api_key)

    @api.model
    def generate_text(self, prompt, model="gpt-3.5-turbo", max_tokens=1000, temperature=0.7):
        client = self._get_openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
