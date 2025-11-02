# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields
from datetime import datetime, timedelta
import json

_logger = logging.getLogger(__name__)

class AudioToTextUseCase(models.TransientModel):
    _name = 'audio_to_text.use.case'
    _description = 'Audio to text Use Case'
    
    # ✅ ALMACENAR RESPUESTAS TEMPORALES
    _response_cache = {}
    
    @api.model
    def check_for_response(self, params):
        """Método para polling - verificar si hay respuesta"""
        try:
            user_id = params.get('user_id', self.env.uid)
            db_name = self.env.cr.dbname
            cache_key = f"{db_name}_{user_id}"
            
            _logger.info(f"🔍 Polling check para: {cache_key}")
            
            # ✅ SIMULAR RESPUESTA PARA PRUEBAS
            # En producción, esto vendría de una base de datos o cache real
            response = {
                'status': 'response_available',
                'final_message': f'RESPUESTA DE PRUEBA via POLLING - Usuario: {user_id}',
                'answer_ia': f'Esta es una respuesta simulada - Hora: {fields.Datetime.now()}',
                'timestamp': fields.Datetime.now().isoformat()
            }
            
            _logger.info(f"✅ Respuesta simulada enviada: {cache_key}")
            return response
                
        except Exception as e:
            _logger.error(f"❌ Error en check_for_response: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
        @api.model
        def test(self):
            """Método de prueba que también guarda en cache"""
            try:
                user_id = self.env.uid
                db_name = self.env.cr.dbname

                channel = f'["{db_name}","res.partner",{user_id}]'

                message = {
                    'type': 'new_response',
                    'final_message': f'PRUEBA EXITOSA DESDE MÉTODO TEST! Usuario: {user_id} - Hora: {fields.Datetime.now()}',
                    'answer_ia': f'Notificación enviada desde test() - Usuario: {user_id} - DB: {db_name}'
                }

                _logger.info(f"🎯 ENVIANDO TEST BUS:")
                _logger.info(f"   Canal: {channel}")
                _logger.info(f"   Mensaje: {message}")

                # ✅ GUARDAR EN CACHE PARA POLLING
                cache_key = f"{db_name}_{user_id}"
                self._response_cache[cache_key] = {
                    'status': 'response_available',
                    'final_message': message['final_message'],
                    'answer_ia': message['answer_ia'],
                    'timestamp': fields.Datetime.now().isoformat()
                }
                
                _logger.info(f"✅ Respuesta guardada en cache: {cache_key}")

                # ✅ INTENTAR ENVÍO POR BUS (puede fallar)
                try:
                    self.env['bus.bus']._sendone(channel, 'audio_to_text_response', message)
                    _logger.info(f"✅ Notificación enviada por BUS")
                except Exception as bus_error:
                    _logger.warning(f"⚠️ Bus no disponible: {bus_error}")

                return {
                    'status': 'success',
                    'message': 'Notificación enviada (bus + cache)',
                    'user_id': user_id,
                    'channel': channel,
                    'cache_key': cache_key,
                    'timestamp': fields.Datetime.now().isoformat()
                }
                
            except Exception as e:
                _logger.error(f"❌ Error en test: {str(e)}", exc_info=True)
                return {
                    'status': 'error',
                    'message': str(e)
                }

    @api.model
    def check_for_response(self, params):
        """Método para polling - verificar si hay respuesta"""
        try:
            user_id = params.get('user_id', self.env.uid)
            db_name = self.env.cr.dbname
            cache_key = f"{db_name}_{user_id}"
            
            _logger.info(f"🔍 Polling check para: {cache_key}")
            
            response = self._response_cache.get(cache_key)
            
            if response:
                _logger.info(f"✅ Respuesta encontrada en cache: {cache_key}")
                # Limpiar cache después de enviar
                del self._response_cache[cache_key]
                return response
            else:
                _logger.info(f"⏳ No hay respuesta aún para: {cache_key}")
                return {
                    'status': 'no_response',
                    'message': 'Aún no hay respuesta disponible'
                }
                
        except Exception as e:
            _logger.error(f"❌ Error en check_for_response: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }