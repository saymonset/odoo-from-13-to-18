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

class EvolutionService(models.TransientModel):
    _name = 'evolution.service'
    _description = 'Evolution Service Layer'
    
     
    
    
    @api.model
    def getInfo(self, data):
        """GetMessageList el caso de uso"""
        use_case = self.env['get_data.use.case']
        options = { 
                   "data":data,
                   }
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
    