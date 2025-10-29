# -*- coding: utf-8 -*-
import os
from pathlib import Path
import logging
import json
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class AudioToTextService(models.TransientModel):
    _name = 'audio_to_text.service'
    _description = 'audio_to_text Service Layer'
    
     
    
    
    @api.model
    def process_info(self, final_message, answer_ia) -> dict:
        """GetMessageList el caso de uso"""
        use_case = self.env['audio_to_text.use.case']
        options = { 
                   "final_message":final_message,
                    "answer_ia":answer_ia,
                   }
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
    