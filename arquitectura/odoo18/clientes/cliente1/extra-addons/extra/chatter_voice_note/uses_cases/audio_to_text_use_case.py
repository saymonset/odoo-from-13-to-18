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
    def execute(self, options) -> dict:
        final_message = options.get('final_message', '')
        answer_ia = options.get('answer_ia')
        
        try:
            response = {
                'final_message': final_message,
                'answer_ia': answer_ia,
            }
            # Abre el archivo de audio en modo binario
            return response
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}