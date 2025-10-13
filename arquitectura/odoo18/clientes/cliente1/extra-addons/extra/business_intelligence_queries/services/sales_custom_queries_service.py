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

class SalesCustomQueriesService(models.TransientModel):
    _name = 'sales_custom_queries.service'
    _description = 'sales_custom_queries Service Layer'
    
  
    
    @api.model
    def sales_custom_queries_service(self, order_number):
        """Obtiene nombre de los productos usando el caso de uso"""
        
        use_case = self.env['sales_custom_queries.use.case']
        
        options = { 
                   "order_number":order_number
                   }
       
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
   