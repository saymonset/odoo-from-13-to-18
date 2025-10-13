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

class ProductNameService(models.TransientModel):
    _name = 'product_name_.service'
    _description = 'product_name_ Service Layer'
    
  
    
    @api.model
    def product_name_service(self, nombre_producto):
        """Obtiene nombre de los productos usando el caso de uso"""
        
        use_case = self.env['produt_name.use.case']
        
        options = { 
                   "nombre_producto":nombre_producto
                   }
       
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
   