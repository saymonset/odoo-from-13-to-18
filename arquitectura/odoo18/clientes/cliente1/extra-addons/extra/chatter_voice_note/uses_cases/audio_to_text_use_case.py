# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields
from datetime import datetime

_logger = logging.getLogger(__name__)

class AudioToTextUseCase(models.TransientModel):
    _name = 'audio_to_text.use.case'
    _description = 'Audio to text Use Case'
    
    request_id = fields.Char(string='Request ID', required=True, index=True)
    final_message = fields.Text(string='Final Message')
    answer_ia = fields.Text(string='Answer IA')
    create_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)
    
    @api.model
    def execute(self, options) -> dict:
        try:
            final_message = options.get('final_message', '').strip()
            answer_ia = options.get('answer_ia', '').strip()
            request_id = options.get('request_id')

            _logger.info("=== USE CASE: DATOS DE IA ===")
            _logger.info(f"final_message: {final_message}")
            _logger.info(f"answer_ia: {answer_ia}")
            _logger.info(f"request_id: {request_id}")

            # Validación
            if not final_message and not answer_ia:
                _logger.error("USE CASE: Ambos campos vacíos")
                return {
                    'status': 'error',
                    'message': 'Datos de IA vacíos'
                }

            # Generar request_id si no viene
            if not request_id:
                request_id = f"ia_{self.env.uid}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                _logger.warning(f"Generado request_id fallback: {request_id}")
            else:
                _logger.info(f"Usando request_id del frontend: {request_id}")

            # BUSCAR SI YA EXISTE
            existing = self.search([('request_id', '=', request_id)], limit=1)

            vals = {
                'request_id': request_id,
                'final_message': final_message,
                'answer_ia': answer_ia,
            }

            if existing:
                existing.write(vals)
                _logger.info(f"Actualizado registro existente: {request_id}")
            else:
                record = self.create(vals)
                _logger.info(f"Creado nuevo registro: {request_id} | ID: {record.id}")

            # ELIMINADO: bus.bus (no lo necesitas con polling)
            # request.env['bus.bus']._sendone(...)

            return {
                'status': 'success',
                'message': 'Datos guardados correctamente',
                'request_id': request_id,
                'found': True,  # Para que el frontend sepa que ya existe
                'final_message': final_message,
                'answer_ia': answer_ia
            }

        except Exception as e:
            _logger.error(f"Error en execute: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }