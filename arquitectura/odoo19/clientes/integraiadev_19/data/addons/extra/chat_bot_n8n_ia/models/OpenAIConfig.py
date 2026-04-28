# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
#from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OpenAIConfig(models.Model):
    _name = 'openai.config'
    _description = 'OpenAI Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='OpenAI Configuration')
    api_key = fields.Char(string='API Key', required=True, help='Tu clave de API de OpenAI')
    default_model = fields.Selection([
    ('gpt-4o-mini', 'GPT-4o Mini (Recomendado)'),
    ('gpt-4.1-nano', 'GPT-4.1 Nano (Máximo Ahorro)'),
    ('gpt-5-nano', 'GPT-5 Nano (Ultra Económico)'),
    ('gpt-3.5-turbo', 'GPT-3.5 Turbo (Legacy)'),
    ('gpt-4o', 'GPT-4o (Alto Rendimiento)'),
], default='gpt-4o-mini')
    active = fields.Boolean(default=True)

    @api.constrains('api_key')
    def _check_api_key(self):
        for record in self:
            None
            #if record.api_key and not record.api_key.startswith('sk-'):
             #   raise ValidationError(_('La clave de API debe comenzar con "sk-"'))
