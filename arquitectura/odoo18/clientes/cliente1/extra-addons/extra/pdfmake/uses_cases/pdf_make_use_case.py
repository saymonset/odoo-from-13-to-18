# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time

_logger = logging.getLogger(__name__)

class PdfMakeUseCase(models.TransientModel):
    _name = 'pdf_make.use.case'
    _description = 'Pdf make Use Case'

    @api.model
    def execute(self, options):
        prompt = options.get('prompt', '')
        
        try:

            return {
                "case": prompt
            }
             

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}