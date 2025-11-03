# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class AudioToTextUseCase(models.Model):
    _name = 'audio_to_text.use.case'
    _description = 'Audio to text Use Case'

    name = fields.Char(string="Name", default="Diagnostic Tool")

    
    @api.model
    def test_bus_diagnostic(self):
        """Método de diagnóstico completo del BUS - CORREGIDO"""
        try:
            user_id = self.env.uid
            db_name = self.env.cr.dbname

            # ✅ CANALES CORRECTOS PARA ODOO 18
            channels = [
                f'["{db_name}","res.partner",{user_id}]',  # Canal de usuario estándar
                f'["{db_name}","audio_to_text.use.case",{user_id}]',  # Canal específico
                '["broadcast"]'  # Canal de broadcast general
            ]
            
            message = {
                'type': 'audio_to_text_response',
                'final_message': f'🚀 DIAGNÓSTICO BUS EXITOSO - Usuario: {user_id}',
                'answer_ia': f'Prueba de diagnóstico completada - {fields.Datetime.now()}',
                'user_id': user_id,
                'timestamp': fields.Datetime.now().isoformat(),
                'diagnostic': True,
                'status': 'success'
            }

            _logger.info("🎯 DIAGNÓSTICO BUS INICIADO:")
            _logger.info(f"   Usuario: {user_id}")
            _logger.info(f"   Base de datos: {db_name}")

            # ✅ ENVIAR A MÚLTIPLES CANALES
            bus_env = self.env['bus.bus'].sudo()
            success_count = 0
            
            for channel in channels:
                try:
                    bus_env._sendone(channel, 'audio_to_text_response', message)
                    _logger.info(f"✅ Mensaje enviado a canal: {channel}")
                    success_count += 1
                except Exception as e:
                    _logger.error(f"❌ Error enviando a {channel}: {str(e)}")

            if success_count > 0:
                return {
                    'status': 'success',
                    'message': f'Mensajes enviados a {success_count} canales',
                    'user_id': user_id,
                    'channels': channels,
                    'diagnostic': 'completed'
                }
            else:
                return {
                    'status': 'error', 
                    'message': 'No se pudo enviar a ningún canal'
                }

        except Exception as e:
            _logger.error(f"❌ Error crítico en diagnóstico BUS: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error crítico: {str(e)}'
            }
        """Método de diagnóstico completo del BUS - CORREGIDO"""
        try:
            user_id = self.env.uid
            db_name = self.env.cr.dbname

            # ✅ CANAL CORREGIDO - usar el modelo correcto
            channel = f'["{db_name}","audio_to_text.use.case",{user_id}]'
            
            message = {
                'type': 'audio_to_text_response',
                'final_message': f'🚀 DIAGNÓSTICO BUS EXITOSO - Usuario: {user_id}',
                'answer_ia': f'Prueba de diagnóstico completada - {fields.Datetime.now()}',
                'user_id': user_id,
                'timestamp': fields.Datetime.now().isoformat(),
                'diagnostic': True,
                'status': 'success'
            }

            _logger.info("🎯 DIAGNÓSTICO BUS INICIADO:")
            _logger.info(f"   Usuario: {user_id}")
            _logger.info(f"   Base de datos: {db_name}")
            _logger.info(f"   Canal: {channel}")

            # ✅ USAR SUPERUSER PARA OPERACIONES BUS
            bus_env = self.env['bus.bus'].sudo()
            
            # ✅ SOLO USAR _sendone (método recomendado)
            try:
                bus_env._sendone(channel, 'audio_to_text_response', message)
                _logger.info("✅ _sendone ejecutado correctamente con SUPERUSER")
                
                return {
                    'status': 'success',
                    'message': 'Mensaje enviado por BUS correctamente',
                    'user_id': user_id,
                    'channel': channel,
                    'diagnostic': 'completed',
                    'timestamp': fields.Datetime.now().isoformat()
                }
                
            except Exception as e:
                _logger.error(f"❌ _sendone falló: {str(e)}")
                return {
                    'status': 'error', 
                    'message': f'Error enviando mensaje BUS: {str(e)}'
                }

        except Exception as e:
            _logger.error(f"❌ Error crítico en diagnóstico BUS: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error crítico: {str(e)}'
            }