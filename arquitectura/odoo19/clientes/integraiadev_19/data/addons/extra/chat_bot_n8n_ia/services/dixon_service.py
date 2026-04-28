# -*- coding: utf-8 -*-
import os
from pathlib import Path
import logging
import json
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

_logger = logging.getLogger(__name__)

class DixonService(models.TransientModel):
    _name = 'dixon.service'
    _description = 'Dixon Service Layer'
    
    @api.model
    def _get_openai_config(self):
        """Obtiene la configuración de OpenAI"""
        config = self.env['openai.config'].sudo().search([('active', '=', True)], limit=1)
        if not config:
            raise ValidationError(_('Configura la clave de API de OpenAI en Ajustes.'))
        return config
    
    @api.model
    def createThread(self, threadId):
        """threadId el caso de uso"""
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['create_thread.use.case']
        options = { 
                   "threadId":threadId,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
         
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
    @api.model
    def createMessage(self, threadId,question):
        """Message el caso de uso"""
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['create_message.use.case']
        options = { 
                   "threadId":threadId,
                   "question":question,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
         
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
    @api.model
    def createRun(self, threadId):
        """Message el caso de uso"""
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['create_run.use.case']
        options = { 
                   "threadId":threadId,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
    @api.model
    def checkCompleteStatusRun(self, threadId, runId):
        """CheckCompleteStatus el caso de uso"""
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['check_complete_status.use.case']
        options = { 
                   "threadId":threadId,
                   "runId":runId,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    @api.model
    def checkCompleteStatusRun(self, threadId, runId):
        """CheckCompleteStatus el caso de uso"""
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['check_complete_status.use.case']
        options = { 
                   "threadId":threadId,
                   "runId":runId,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
    @api.model
    def getMessageList(self, threadId):
        """GetMessageList el caso de uso"""
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['get_message_list.use.case']
        options = { 
                   "threadId":threadId,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
    