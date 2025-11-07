# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields
from datetime import datetime
from odoo.http import request
_logger = logging.getLogger(__name__)

class AudioToTextUseCase(models.TransientModel):
    _name = 'audio_to_text.use.case'
    _description = 'Audio to text Use Case'
    
    # Campos para guardar la respuesta
    request_id = fields.Char(string='Request ID', required=True, index=True)  # 🔥 Asegurar index
    final_message = fields.Text(string='Final Message')
    answer_ia = fields.Text(string='Answer IA')
    create_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)
    
    @api.model
    def execute(self, options) -> dict:
        try:
            # 🔥 SOLO LOS DOS PARÁMETROS DE LA IA
            final_message = options.get('final_message', '')
            answer_ia = options.get('answer_ia', '')
            request_id = options.get('request_id')  # 🔥 Obtenemos el request_id del frontend
            
            _logger.info("=== USE CASE: DATOS DE IA ===")
            _logger.info(f"final_message: {final_message}")
            _logger.info(f"answer_ia: {answer_ia}")
            _logger.info(f"request_id recibido: {request_id}")
            
            # 🔥 VERIFICAR DATOS DE LA IA
            if not final_message and not answer_ia:
                _logger.error("❌ USE CASE: Ambos campos de IA están vacíos")
                return {
                    'status': 'error',
                    'message': 'Datos de IA vacíos'
                }
            
            # 🔥 USAR EL REQUEST_ID DEL FRONTEND O GENERAR UNO DE FALLBACK
            if not request_id:
                _logger.warning("⚠️ USE CASE: No se recibió request_id, generando uno de fallback")
                request_id = f"ia_{self.env.uid}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            else:
                _logger.info(f"✅ USE CASE: Usando request_id del frontend: {request_id}")
                
                 # 🔥 EMITIR EVENTO AL BUS
                record_id = '0'
                request.env['bus.bus']._sendone(
                    'chatter_voice_note',  # Canal
                    'voice_note_response_ready',  # Tipo de evento
                    {
                        'request_id': request_id,
                        'final_message': final_message,
                        'answer_ia': answer_ia,
                        'record_id': record_id
                    }
                )

            
            
            _logger.info(f"✅ USE CASE: Registro  request_id: {request_id}")

            return {
                'status': 'success',
                'message': 'Datos de IA procesados y guardados',
                'request_id': request_id,  # 🔥 Devolvemos el mismo request_id
                'record_id': '0'
            }
            
        except Exception as e:
            _logger.error(f"❌ Error en execute: {str(e)}", exc_info=True)
            return {"error": str(e)}