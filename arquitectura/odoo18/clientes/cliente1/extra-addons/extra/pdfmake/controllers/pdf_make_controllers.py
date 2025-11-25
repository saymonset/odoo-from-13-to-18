# controllers/pdfmake_controller.py
import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class PdfMakeController(http.Controller):

    @http.route('/pdfmake/audioreports', type='http', auth='public', csrf=False, methods=['GET', 'POST'])
    def audioReports(self, **kw):
        try:
            _logger.info("📥 Request recibido en /pdfmake/audioreports")
            
            # Obtener prompt de diferentes formas
            prompt = kw.get('prompt') 
            if not prompt and request.httprequest.method == 'POST':
                try:
                    json_data = request.httprequest.get_json()
                    prompt = json_data.get('prompt') if json_data else None
                except:
                    pass
            
            _logger.info(f"🔍 Prompt recibido: {prompt}")
            
            if not prompt:
                return Response(
                    json.dumps({'error': 'No prompt provided'}),
                    content_type='application/json',
                    status=400
                )
            
            # CORREGIDO: Usar request.env en lugar de http.request.env
            # Y manejar posible inexistencia del modelo
            try:
                service = request.env['pdf_make.service'].sudo()
                result = service.pdfMake(prompt)
                _logger.info(f"✅ Resultado del servicio: {result}")
            except Exception as model_error:
                _logger.error(f"❌ Error accediendo al modelo: {model_error}")
                return Response(
                    json.dumps({'error': f'Model service error: {str(model_error)}'}),
                    content_type='application/json',
                    status=500
                )
            
            return Response(
                json.dumps(result),
                content_type='application/json',
                status=200
            )
            
        except Exception as e:
            _logger.error(f"💥 Error general en controlador: {str(e)}")
            return Response(
                json.dumps({'error': f'Internal server error: {str(e)}'}),
                content_type='application/json',
                status=500
            )