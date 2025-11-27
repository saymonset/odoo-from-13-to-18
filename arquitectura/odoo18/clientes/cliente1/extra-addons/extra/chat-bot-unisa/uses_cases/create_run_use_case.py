# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time

_logger = logging.getLogger(__name__)

class CreateRunUseCase(models.TransientModel):
    _name = 'create_run.use.case'
    _description = 'Create Run Use Case'

    @api.model
    def execute(self, options):
        try:
            openai = options.get('openai_client')
            threadId = options.get('threadId')
            assitentId = "asst_ohlyvfkzPK64kSig4JCqX68B"

            run = openai.beta.threads.runs.create( 
                thread_id=threadId,
                assistant_id=assitentId ) 
            return run

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}