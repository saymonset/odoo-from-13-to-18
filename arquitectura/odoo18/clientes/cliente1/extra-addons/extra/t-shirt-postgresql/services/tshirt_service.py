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

class TshirtService(models.TransientModel):
    _name = 'tshirt.service'
    _description = 'tshirt Service Layer'
    
  
    
    @api.model
    def quantity_sell_total_sell_service(self):
        """Verificación ortográfica usando el caso de uso"""
        
        use_case = self.env['quantity_sell_total_sell.use.case']
       
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute()
    
   