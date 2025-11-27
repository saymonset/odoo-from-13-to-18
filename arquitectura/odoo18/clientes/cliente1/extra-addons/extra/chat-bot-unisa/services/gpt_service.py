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

class GptService(models.TransientModel):
    _name = 'gpt.service'
    _description = 'GPT Service Layer'
    
    @api.model
    def _get_openai_config(self):
        """Obtiene la configuración de OpenAI"""
        config = self.env['openai.config'].sudo().search([('active', '=', True)], limit=1)
        if not config:
            raise ValidationError(_('Configura la clave de API de OpenAI en Ajustes.'))
        return config
    
    @api.model
    def orthography_check(self, prompt, max_tokens=None):
        """Verificación ortográfica usando el caso de uso"""
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['orthography.use.case']
        options = {"prompt": prompt,
                   "max_tokens": max_tokens,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
         
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
    @api.model
    def textToAudio(self, prompt, voice=None):
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['text_to_audio.use.case']
        options = {"prompt": prompt,
                   "voice": voice,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
         
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    @api.model
    def getAudio(self, file_id):
        # Obtener la ruta base donde se guardan los audios
            folder_path = Path(__file__).parent.resolve() / '../generated/audios/'
            folder_path = folder_path.resolve()
            
            # Construir la ruta completa del archivo
            file_path = folder_path / f"{file_id}.mp3"
            if not file_path.exists():
                raise ValidationError(_('El archivo de audio no existe.'))
            return str(file_path)
        
        
    @api.model
    def audioToText(self, file_path, prompt=''):
            config = self._get_openai_config()
            openai_client = OpenAI(api_key=config.api_key)
            use_case = self.env['audio_to_text.use.case']
            options = {"prompt": prompt,
                    "file_path": file_path,
                    "openai_client": openai_client
                    }
            
            # Implementa aquí la lógica real de verificación ortográfica
            # Por ahora devolvemos un ejemplo básaico
            return use_case.execute(options)
            

