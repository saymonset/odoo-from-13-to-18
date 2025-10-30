# -*- coding: utf-8 -*-

import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class AudioToTextUseCase(models.TransientModel):
    _name = 'audio_to_text.use.case'
    _description = 'Audio to text Use Case'

    @api.model
    def execute(self, options) -> dict:
        final_message = options.get('final_message', '')
        answer_ia = options.get('answer_ia', '')

        try:
            channel_name = "audio_to_text_channel_1"  # CANAL PÚBLICO FIJO

            payload = {
                'final_message': final_message,
                'answer_ia': answer_ia,
            }

            # USA _sendone CON CANAL PÚBLICO (sin usuario)
            self.env['bus.bus']._sendone(channel_name, 'new_response', payload)

            _logger.info(f"ENVIADO a canal público: {channel_name}")
            return {'final_message': final_message, 'answer_ia': answer_ia}

        except Exception as e:
            _logger.error(f"Error: {str(e)}", exc_info=True)
            return {"error": str(e)}