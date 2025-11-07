# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class AudioToTextController(http.Controller):
    @http.route('/chatter_voice_note/audio_to_text', auth='public', 
            methods=['POST'], type='http', cors='*', csrf=False)
    def get_daily_summary_queries(self, **kw):
        try:
            # === OBTENER DATOS DE MÚLTIPLES FUENTES ===
            data = http.request.httprequest.get_json(silent=True) or {}
            params = request.httprequest.args or {}
            
            _logger.info("="*60)
            _logger.info("🎯 CALLBACK RECIBIDO DE N8N")
            _logger.info(f"📦 JSON Body: {data}")
            _logger.info(f"🔗 Parámetros URL: {params}")
            
            # 🔥 BUSCAR request_id EN MÚLTIPLES UBICACIONES
            request_id = (data.get('request_id') or 
                        params.get('request_id') or 
                        data.get('requestId') or 
                        params.get('requestId'))
            
            final_message = data.get('final_message', '') or data.get('finalMessage', '')
            answer_ia = data.get('answer_ia', '') or data.get('answerIa', '') or data.get('answer_ia', '')
            
            _logger.info(f"🔥 REQUEST_ID ENCONTRADO: {request_id}")
            _logger.info(f"📝 FINAL_MESSAGE: {final_message}")
            _logger.info(f"🤖 ANSWER_IA: {answer_ia}")
            
            if not request_id:
                _logger.error("❌ NO SE ENCONTRÓ REQUEST_ID EN NINGUNA FUENTE")
                return http.request.make_response(
                    json.dumps({'success': False, 'error': 'No request_id found'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )
            
            # === PROCESAR CON EL SERVICIO ===
            service = request.env['audio_to_text.service'].sudo()
            info = service.process_info(final_message, answer_ia, request_id)
            
            
           
            _logger.info(f"✅ RESULTADO DEL PROCESAMIENTO: {info}")
            _logger.info("="*60)

            return http.request.make_response(
                json.dumps({
                    'success': True, 
                    'received': info,
                    'message': 'Datos procesados correctamente'
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error('❌ ERROR EN CALLBACK: %s', str(e), exc_info=True)
            return http.request.make_response(
                json.dumps({'success': False, 'error': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    # Endpoint para consultar respuestas
    @http.route('/chatter_voice_note/get_response', type='json', auth='user', methods=['POST'], csrf=False)
    def get_response(self, **kwargs):
        """Endpoint para que el frontend consulte respuestas"""
        try:
            request_data = request.httprequest.get_json(silent=True) or {}
            request_id = request_data.get('request_id')
            
            _logger.info(f"🔍 Buscando respuesta para request_id: {request_id}")
            
            if not request_id:
                _logger.error("❌ No se proporcionó request_id")
                return {
                    'found': False,
                    'error': 'No se proporcionó request_id'
                }
            
            # Buscar en el modelo use.case
            record = request.env['audio_to_text.use.case'].sudo().search([
                ('request_id', '=', request_id)
            ], limit=1)
            
            if record:
                _logger.info(f"✅ Respuesta encontrada: {record.final_message[:100]}...")
                return {
                    'final_message': record.final_message,
                    'answer_ia': record.answer_ia or '',
                    'request_id': record.request_id,
                    'found': True
                }
            else:
                _logger.info(f"⚠️ No se encontró respuesta para: {request_id}")
                return {
                    'found': False,
                    'message': 'Respuesta no disponible aún'
                }
                
        except Exception as e:
            _logger.error(f'Error en get_response: {str(e)}')
            return {
                'error': str(e),
                'found': False
            }