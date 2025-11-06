# -*- coding: utf-8 -*-
import logging
from odoo import models, api
from datetime import datetime

_logger = logging.getLogger(__name__)

class AudioToTextUseCase(models.TransientModel):
    _name = 'audio_to_text.use.case'
    _description = 'Audio to text Use Case'
    
    @api.model
    def execute(self, options) -> dict:
        try:
            # 🔥 SOLO LOS DOS PARÁMETROS DE LA IA
            final_message = options.get('final_message', '')
            answer_ia = options.get('answer_ia', '')
            
            _logger.info("=== USE CASE: DATOS DE IA ===")
            _logger.info(f"final_message: {final_message}")
            _logger.info(f"answer_ia: {answer_ia}")
            
            # 🔥 VERIFICAR DATOS DE LA IA
            if not final_message and not answer_ia:
                _logger.error("❌ USE CASE: Ambos campos de IA están vacíos")
                return {
                    'status': 'error',
                    'message': 'Datos de IA vacíos'
                }
            
            # 🔥 GENERAR REQUEST_ID ÚNICO (para el bus)
            request_id = f"ia_{self.env.uid}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            channel_name = "audio_to_text_channel_1"
            
            payload = {
                'final_message': final_message,
                'answer_ia': answer_ia,
                'request_id': request_id
            }
            
            # En tu backend, agrega estos logs adicionales para confirmar:
            _logger.info(f"🎯 PREPARANDO ENVÍO AL BUS - CANAL: {channel_name}")
            _logger.info(f"📤 MENSAJE A ENVIAR: {payload}")
            _logger.info(f"🔍 TIPO DE MENSAJE: new_response")

            # 🔥 ENVIAR AL BUS
            _logger.info("✅ ENVÍO AL BUS COMPLETADO SIN ERRORES")
            self.env['bus.bus']._sendone(channel_name, 'new_response', payload)
            _logger.info(f"✅✅✅ USE CASE: ENVIADO AL BUS - {payload}")

            # 🔥 VERIFICAR QUE NO HAY ERRORES
           
            # 🔥 ENVIAR AL BUS
           
            # 🔥 RETORNAR RESPUESTA
            return {
                'status': 'success',
                'message': 'Datos de IA procesados y enviados al bus',
                'request_id': request_id,
                'final_message': final_message,
                'answer_ia': answer_ia
            }
            
        except Exception as e:
            _logger.error(f"❌ Error en execute: {str(e)}", exc_info=True)
            return {"error": str(e)}