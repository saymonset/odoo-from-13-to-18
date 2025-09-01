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
    def orthography_check(self, prompt, max_tokens=None):
        """Verificación ortográfica usando el caso de uso"""
        use_case = self.env['orthography.use.case']
        options = {"prompt": prompt}
        if max_tokens:
            options["max_tokens"] = max_tokens
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básico
        return use_case.execute(options)
