from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class DiagnosisVoiceController(http.Controller):  # ✅ CORREGIDO: "Controller" bien escrito
    
    @http.route('/hospital/voice_callback', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def hospital_voice_callback(self, **post):
        """Callback para recibir respuestas de voz y actualizar diagnósticos"""
        try:
            # Obtener datos de múltiples formas
            if request.httprequest.data:
                try:
                    data = json.loads(request.httprequest.data)
                except:
                    data = post
            else:
                data = post
            
            request_id = data.get('request_id') or data.get('requestId')
            final_message = data.get('final_message') or data.get('finalMessage', '')
            
            _logger.info(f"🎯 Callback recibido en hospital para request_id: {request_id}")
            
            if not request_id or not final_message:
                _logger.error("❌ Faltan request_id o final_message")
                return request.make_response(
                    json.dumps({'success': False, 'message': 'Datos incompletos'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )
            
            # 🔥 CORREGIDO: Buscar en múltiples formatos
            diagnosis_id = None
            
            # Formato diagnosis_123_...
            if request_id.startswith('diagnosis_'):
                try:
                    parts = request_id.split('_')
                    if len(parts) >= 2:
                        diagnosis_id = int(parts[1])
                except (ValueError, IndexError) as e:
                    _logger.warning(f"⚠️ No se pudo extraer diagnosis_id de {request_id}: {str(e)}")
            
            # Formato req_... pero con res_model diagnosis
            res_model = data.get('res_model')
            res_id = data.get('res_id')
            if not diagnosis_id and res_model == 'a_hospital.diagnosis' and res_id:
                diagnosis_id = res_id
            
            if diagnosis_id:
                diagnosis = request.env['a_hospital.diagnosis'].sudo().browse(diagnosis_id)
                if diagnosis.exists():
                    diagnosis.write({'description': final_message})
                    _logger.info(f"✅ Diagnóstico {diagnosis_id} actualizado: {final_message[:100]}...")
                    
                    return request.make_response(
                        json.dumps({
                            'success': True, 
                            'message': 'Diagnóstico actualizado correctamente'
                        }),
                        headers=[('Content-Type', 'application/json')]
                    )
            
            _logger.info(f"ℹ️ Request_id {request_id} no corresponde a diagnóstico, ignorando...")
            return request.make_response(
                json.dumps({'success': True, 'message': 'Mensaje recibido'}),
                headers=[('Content-Type', 'application/json')]
            )
            
        except Exception as e:
            _logger.error(f"❌ Error en callback hospital: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
            
    @http.route('/hospital/test', type='http', auth='public', methods=['GET'])
    def hospital_test(self, **kw):
        """Ruta de prueba para verificar que el controlador funciona"""
        return request.make_response(
            json.dumps({'success': True, 'message': 'Controlador hospital funcionando'}),
            headers=[('Content-Type', 'application/json')]
        )