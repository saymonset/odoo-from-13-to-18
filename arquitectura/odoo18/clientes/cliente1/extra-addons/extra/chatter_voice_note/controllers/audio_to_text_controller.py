# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class AudioToTextController(http.Controller):
    
    @http.route('/chatter_voice_note/audio_to_text', auth='public', methods=['POST'], type='http', cors='*', csrf=False)
    def get_daily_summary_queries(self, **kw):
        try:
            # === OBTENER JSON DEL CUERPO DEL POST ===
            data = http.request.httprequest.get_json(silent=True) or {}
            
            # === LOG DE DATOS RECIBIDOS ===
            _logger.info("="*50)
            _logger.info("DATOS RECIBIDOS (JSON)")
            _logger.info(f"Datos crudos: {data}")

            # === ACCEDER A CAMPOS ===
            final_message = data.get('final_message', '')
            answer_ia = data.get('answer_ia', '')
            
            # === PROCESAR CON EL SERVICIO ===
            service = request.env['audio_to_text.service'].sudo()
            info = service.process_info(final_message, answer_ia)

            # === LOG DE RESULTADO ===
            _logger.info(f"Resultado procesado: {info}")
            _logger.info("="*50)

            return http.request.make_response(
                json.dumps({
                    'success': True, 
                    'received': info,
                    'message': 'Datos procesados correctamente'
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error('Error en el controlador: %s', str(e))
            return http.request.make_response(
                json.dumps({
                    'success': False, 
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=500
            )