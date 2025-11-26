# -*- coding: utf-8 -*-
import os
from pathlib import Path
import logging
import json
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)

class PdfMakeService(models.TransientModel):
    _name = 'pdf_makexx.service'
    _description = 'Pdf Service Layer'
    
    @api.model
    def pdfMake(self, prompt):
        """ el caso de uso"""
        use_case = self.env['pdf_make.use.case']
        options = { 
                   "prompt":prompt,
                   }
        return use_case.execute(options)