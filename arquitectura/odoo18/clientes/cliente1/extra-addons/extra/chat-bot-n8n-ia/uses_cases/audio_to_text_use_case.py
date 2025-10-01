# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time

_logger = logging.getLogger(__name__)

class AudioToTextUseCase(models.TransientModel):
    _name = 'audio_to_text.use.case'
    _description = 'Audio to text Use Case'

    @api.model
    def execute(self, options):
        prompt = options.get('prompt', '')
        file_path = options.get('file_path')
        openai_client = options.get('openai_client')
        
        try:
            # Abre el archivo de audio en modo binario
            with open(file_path, "rb") as audio_file:
                response = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt=prompt,
                    language="es",
                    response_format="verbose_json"
                    #tipos de formto = vtt,str, verbose_json
                )
            return response
             

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}