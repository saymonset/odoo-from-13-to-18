# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time

_logger = logging.getLogger(__name__)

class CreateMessageUseCase(models.TransientModel):
    _name = 'create_message.use.case'
    _description = 'Create Message Use Case'

    @api.model
    def execute(self, options):
        try:
            openai = options.get('openai_client')
            threadId = options.get('threadId')
            question = options.get('question')
            model = options.get('model', 'gpt-3.5-turbo')
            message = openai.beta.threads.messages.create(
                thread_id=threadId,
                role='user',
                content=question
            ) 
            return message

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}