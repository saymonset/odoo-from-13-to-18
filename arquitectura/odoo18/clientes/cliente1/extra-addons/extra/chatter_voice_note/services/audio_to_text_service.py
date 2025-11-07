# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields
from datetime import datetime

_logger = logging.getLogger(__name__)

class AudioToTextService(models.Model):
    _name = 'audio_to_text.service'
    _description = 'Audio to Text Service'

    def process_info(self, final_message, answer_ia, request_id):
        """Procesa la información recibida de N8N"""
        try:
            _logger.info("🎯 INICIANDO PROCESAMIENTO EN SERVICIO")
            _logger.info(f"Request ID: {request_id}")
            _logger.info(f"Final Message length: {len(final_message) if final_message else 0}")
            _logger.info(f"Answer IA length: {len(answer_ia) if answer_ia else 0}")
            
            use_case = self.env['audio_to_text.use.case']
            options={
                'final_message': final_message,
                'answer_ia': answer_ia,
                'request_id': request_id
            }
            result = use_case.execute(options)
            
            _logger.info(f"✅ RESULTADO USE CASE: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"❌ ERROR EN SERVICIO: {str(e)}", exc_info=True)
            return {'error': str(e)}