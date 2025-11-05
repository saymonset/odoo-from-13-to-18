# -*- coding: utf-8 -*-
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class AudioToTextUseCase(models.TransientModel):
    _name = 'audio_to_text.use.case'
    _description = 'Audio to text Use Case'
    
    @api.model
    def execute(self, options) -> dict:
        try:
            # 🔥 OBTENER DATOS REALES DE LA SOLICITUD
            notes = options.get('notes', [])
            contacts = options.get('contacts', [])
            request_id = options.get('request_id', 'unknown')
            
            _logger.info(f"📥 Procesando solicitud {request_id}")
            _logger.info(f"📝 Notas recibidas: {len(notes)}")
            _logger.info(f"👥 Contactos recibidos: {len(contacts)}")
            
            # 🔥 SIMULAR PROCESAMIENTO (reemplaza con tu lógica real)
            import time
            time.sleep(2)  # Simular procesamiento
            
            # 🔥 GENERAR RESPUESTAS DE PRUEBA REALES
            final_message = f"Mensaje procesado para {len(contacts)} contactos"
            answer_ia = f"Análisis IA completado para {len(notes)} notas de audio"
            
            channel_name = "audio_to_text_channel_1"
            
            payload = {
                'final_message': final_message,
                'answer_ia': answer_ia,
                'request_id': request_id,
                'notes_count': len(notes),
                'contacts_count': len(contacts)
            }
            
            # 🔥 ENVIAR AL BUS
            self.env['bus.bus']._sendone(channel_name, 'new_response', payload)
            _logger.info(f"✅ Enviado a bus: {channel_name} - {payload}")
            
            # 🔥 RETORNAR RESPUESTA INMEDIATA
            return {
                'status': 'processing',
                'message': 'Solicitud recibida y en procesamiento',
                'request_id': request_id,
                'final_message': final_message,  # 🔥 NO null
                'answer_ia': answer_ia  # 🔥 NO null
            }
            
        except Exception as e:
            _logger.error(f"❌ Error en execute: {str(e)}", exc_info=True)
            return {"error": str(e)}