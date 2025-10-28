# -*- coding: utf-8 -*-
import os
import sys
import json
import logging
from odoo import http
from werkzeug.urls import url_decode

_logger = logging.getLogger(__name__)

class AudioToTextController(http.Controller):
    @http.route('/chatter_voice_note/audio_to_text', auth='public', methods=['POST'], type='http', cors='*', csrf=False)
    def get_daily_summary_queries(self, **kw):
        try:
            # === OBTENER JSON DEL CUERPO DEL POST ===
            data = http.request.httprequest.get_json(silent=True) or {}
            
            # === IMPRIMIR TODO ===
            print("\n" + "="*50)
            print("DATOS RECIBIDOS (JSON)")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("="*50 + "\n")

            # === ACCEDER A CAMPOS ===
            final_message = data.get('final_message')
            answer_ia = data.get('answer_ia')

            print(f"final_message: {final_message}")
            print(f"answer_ia: {answer_ia}")

            return http.request.make_response(
                json.dumps({'success': True, 'received': data}),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error('Error: %s', str(e))
            return http.request.make_response(
                json.dumps({'success': False, 'error': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )