# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time

_logger = logging.getLogger(__name__)

class GetMessageListUseCase(models.TransientModel):
    _name = 'get_message_list.use.case'
    _description = 'Get Message List Use Case'

    @api.model
    def execute(self, options):
        try:
            openai_client = options.get('openai_client')
            thread_id = options.get('threadId')
            message_list = openai_client.beta.threads.messages.list( thread_id=thread_id)
            messages = [
                            {
                                'role': message.role,
                                'content': [content.text.value for content in message.content]
                            }
                            for message in message_list.data
                        ]

            return list(reversed(messages))
            

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}