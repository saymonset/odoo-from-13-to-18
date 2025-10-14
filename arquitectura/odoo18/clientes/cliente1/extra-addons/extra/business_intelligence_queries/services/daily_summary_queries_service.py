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

class DailySummaryQueriesService(models.TransientModel):
    _name = 'daily_summary_queries.service'
    _description = 'daily_summary_queries Service Layer'
    
  
    
    @api.model
    def daily_summary_queries_service(self, date_from, date_to, specific_date):
        """Obtiene nombre de los productos usando el caso de uso"""
        
        use_case = self.env['daily_summary_queries.use.case']
        
        options = { 
                   "date_from":date_from,
                   "date_to":date_to,
                   "specific_date":specific_date,
                   }
       
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico

        return use_case.execute(options)
    
   