# -*- coding: utf-8 -*-
import logging
import json
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

_logger = logging.getLogger(__name__)

class GptService(models.TransientModel):
    _name = 'gpt.service'
    _description = 'GPT Service Layer'
    
    @api.model
    def _get_openai_client(self):
        api_key = self.env['openai.config'].sudo().search([('active', '=', True)], limit=1).api_key
        if not api_key:
            None
            raise ValidationError(_('Configura la clave de API de OpenAI en Ajustes.'))
        return OpenAI(api_key=api_key)
    
    @api.model
    def orthography_check(self, prompt, max_tokens=None):
        """Verificación ortográfica usando el caso de uso"""
        openai_client = self._get_openai_client()
        use_case = self.env['orthography.use.case']
        options = {"prompt": prompt,
                   "max_tokens": max_tokens,
                   "openai_client": openai_client,
                   }
         
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
