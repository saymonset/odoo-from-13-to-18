# -*- coding: utf-8 -*-
import os
from pathlib import Path
import logging
import json
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class IaService(models.TransientModel):
    _name = 'ia.service'
    _description = 'IA Service Layer'
    
      
    
    @api.model
    def generateThreadIdAndAnswerIA(self, data):
        """GetMessageList el caso de uso"""
        use_case = self.env['ia.use.case']
        options = { 
                   "data":data,
                   }
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
     
    
    