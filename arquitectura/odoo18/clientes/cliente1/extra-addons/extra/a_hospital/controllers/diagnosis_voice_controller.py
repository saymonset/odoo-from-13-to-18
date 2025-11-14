from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class DiagnosisVoiceController(http.Controller):
    
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
            
            # Buscar si este request_id está relacionado con un diagnóstico
            if request_id.startswith('diagnosis_'):
                try:
                    # Extraer diagnosis_id del request_id (formato: diagnosis_123_abc123)
                    parts = request_id.split('_')
                    if len(parts) >= 2:
                        diagnosis_id = int(parts[1])
                        diagnosis = request.env['a_hospital.diagnosis'].sudo().browse(diagnosis_id)
                        
                        if diagnosis.exists():
                            diagnosis.write({'description': final_message})
                            _logger.info(f"✅ Diagnóstico {diagnosis_id} actualizado desde voz: {final_message[:100]}...")
                            
                            return request.make_response(
                                json.dumps({
                                    'success': True, 
                                    'message': 'Diagnóstico actualizado correctamente'
                                }),
                                headers=[('Content-Type', 'application/json')]
                            )
                        else:
                            _logger.warning(f"⚠️ Diagnóstico {diagnosis_id} no encontrado")
                    else:
                        _logger.warning(f"⚠️ Formato de request_id inválido: {request_id}")
                        
                except (ValueError, IndexError) as e:
                    _logger.error(f"❌ Error extrayendo diagnosis_id de {request_id}: {str(e)}")
            
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