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
            user_id = 2
            db_name = self.env.cr.dbname

            # ✅ CANAL CORRECTO: Canal del usuario (res.partner)
            channel = f'["{db_name}","res.partner",{user_id}]'

            # ✅ ESTRUCTURA CORRECTA: Sin payload anidado
            message = {
                'type': 'new_response',
                'final_message': final_message,
                'answer_ia': answer_ia,
            }

            _logger.info(f"🎯 ENVIANDO NOTIFICACIÓN BUS:")
            _logger.info(f"   Canal: {channel}")
            _logger.info(f"   Evento: audio_to_text_response")
            _logger.info(f"   Mensaje: {message}")
            _logger.info(f"   Usuario: {user_id}")
            _logger.info(f"   Base de datos: {db_name}")

            # ✅ ENVIAR con nombre de evento específico
            self.env['bus.bus']._sendone(channel, 'audio_to_text_response', message)
            _logger.info(f"✅ Notificación enviada exitosamente a canal: {channel}")

            return {
                'final_message': final_message,
                'answer_ia': answer_ia
            }

        except Exception as e:
            _logger.error(f"❌ Error enviando notificación: {str(e)}", exc_info=True)
            return {"error": str(e)}

    @api.model
    def test(self):
        user_id = self.env.uid
        # user_id = 2
        db_name = self.env.cr.dbname

        # ✅ CANAL CORRECTO
        channel = f'["{db_name}","res.partner",{user_id}]'

        # ✅ ESTRUCTURA CORRECTA
        message = {
            'type': 'new_response',
            'final_message': 'PRUEBA EXITOSA DESDE MÉTODO TEST! ' + str(user_id),
            'answer_ia': 'Notificación enviada desde audio_to_text.use.case.test() - Usuario: ' + str(user_id)
        }

        _logger.info(f"🎯 ENVIANDO TEST BUS:")
        _logger.info(f"   Canal: {channel}")
        _logger.info(f"   Mensaje: {message}")

        # ✅ ENVIAR y RETORNAR
        try:
            self.env['bus.bus']._sendone(channel, 'audio_to_text_response', message)
            _logger.info(f"✅ Notificación de prueba enviada al canal: {channel}")
            
            return {
                'status': 'success',
                'message': 'Notificación de prueba enviada',
                'user_id': user_id,
                'channel': channel
            }
        except Exception as e:
            _logger.error(f"❌ Error en test: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }