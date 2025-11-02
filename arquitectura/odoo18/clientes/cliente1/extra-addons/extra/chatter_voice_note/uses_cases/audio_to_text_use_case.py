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
            user_id = self.env.uid
            db_name = self.env.cr.dbname

            # ✅ CANAL CORRECTO: Canal del usuario (res.partner)
            channel = f'["{db_name}","res.partner",{user_id}]'

            message = {
                'type': 'new_response',
                'final_message': final_message,
                'answer_ia': answer_ia,
            }

            _logger.info(f"🎯 ENVIANDO NOTIFICACIÓN BUS:")
            _logger.info(f"   Canal: {channel}")
            _logger.info(f"   Mensaje: {message}")

            # ✅ ENVIAR con nombre de evento específico
            self.env['bus.bus']._sendone(channel, 'audio_to_text_response', message)
            _logger.info(f"✅ Notificación enviada exitosamente")

            return {
                'final_message': final_message,
                'answer_ia': answer_ia
            }

        except Exception as e:
            _logger.error(f"❌ Error enviando notificación: {str(e)}", exc_info=True)
            return {"error": str(e)}


    @api.model
    def test(self):
        """Método de prueba MEJORADO con más información"""
        try:
            user_id = self.env.uid
            db_name = self.env.cr.dbname

            # ✅ CANAL CORRECTO
            channel = f'["{db_name}","res.partner",{user_id}]'

            message = {
                'type': 'new_response',
                'final_message': f'PRUEBA EXITOSA DESDE MÉTODO TEST! Usuario: {user_id} - Hora: {fields.Datetime.now()}',
                'answer_ia': f'Notificación enviada desde test() - Usuario: {user_id} - DB: {db_name}'
            }

            _logger.info(f"🎯 ENVIANDO TEST BUS:")
            _logger.info(f"   Canal: {channel}")
            _logger.info(f"   Mensaje: {message}")
            _logger.info(f"   Usuario: {user_id}")
            _logger.info(f"   Base de datos: {db_name}")

            # ✅ ENVIAR y RETORNAR
            self.env['bus.bus']._sendone(channel, 'audio_to_text_response', message)
            _logger.info(f"✅ Notificación de prueba ENVIADA al canal: {channel}")
            
            return {
                'status': 'success',
                'message': 'Notificación de prueba enviada',
                'user_id': user_id,
                'channel': channel,
                'timestamp': fields.Datetime.now().isoformat()
            }
            
        except Exception as e:
            _logger.error(f"❌ Error en test: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }

        """Método de prueba MEJORADO con más logs"""
        try:
            user_id = self.env.uid
            db_name = self.env.cr.dbname

            # ✅ CANAL CORRECTO
            channel = f'["{db_name}","res.partner",{user_id}]'

            message = {
                'type': 'new_response',
                'final_message': f'PRUEBA EXITOSA DESDE MÉTODO TEST! Usuario: {user_id}',
                'answer_ia': f'Notificación enviada desde test() - Usuario: {user_id}'
            }

            _logger.info(f"🎯 ENVIANDO TEST BUS:")
            _logger.info(f"   Canal: {channel}")
            _logger.info(f"   Mensaje: {message}")

            # ✅ ENVIAR y RETORNAR
            self.env['bus.bus']._sendone(channel, 'audio_to_text_response', message)
            _logger.info(f"✅ Notificación de prueba enviada")
            
            return {
                'status': 'success',
                'message': 'Notificación de prueba enviada',
                'user_id': user_id,
                'channel': channel
            }
            
        except Exception as e:
            _logger.error(f"❌ Error en test: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }