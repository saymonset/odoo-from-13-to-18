# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time

_logger = logging.getLogger(__name__)

class CreateThreadUseCase(models.TransientModel):
    _name = 'create_thread.use.case'
    _description = 'Create Thread Use Case'

    @api.model
    def execute(self, options)->dict:
        try:
            openai = options.get('openai_client')
            # conversation = openai.conversations.create(
            #     items=[{"role": "user", "content": "what are the 5 Ds of dodgeball?"}],
            #     metadata={"user_id": "peter_le_fleur"},
            #     )
            
            thread = openai.beta.threads.create()
            return {"id": thread.id}
             

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}