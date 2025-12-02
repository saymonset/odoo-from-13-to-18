import json
import logging
import requests
from odoo import http
from odoo.http import request, Response
from datetime import datetime

_logger = logging.getLogger(__name__)

class MedicalReportController(http.Controller):

    @http.route('/medical_report/send_to_n8n', type='http', auth='user', methods=['POST'], csrf=False)
    def send_medical_report_to_n8n(self, **post):
        """
        Envía el reporte médico al webhook de n8n - Compatible con todas las versiones de Odoo
        """
        try:
            _logger.info("📧 Iniciando envío de reporte médico a n8n")
            
            # SOLUCIÓN: Manejo compatible de datos para todas las versiones de Odoo
            post_data = {}
            
            # Verificar si hay datos JSON en el body
            if request.httprequest.data:
                try:
                    raw_data = request.httprequest.data.decode('utf-8')
                    if raw_data:
                        json_data = json.loads(raw_data)
                        _logger.info(f"📥 Datos JSON recibidos del body: {list(json_data.keys())}")
                        
                        # Manejar formato JSON-RPC (con "params") o directo
                        if 'params' in json_data:
                            post_data = json_data.get('params', {})
                        else:
                            post_data = json_data
                except json.JSONDecodeError as e:
                    _logger.warning(f"⚠️ No se pudo decodificar JSON del body: {e}")
                    # Si falla el JSON, usar los parámetros POST normales
                    post_data = post
            else:
                # Usar parámetros POST normales
                post_data = post
            
            _logger.info(f"📥 Datos procesados: {list(post_data.keys())}")
            
            # Validar datos requeridos
            pdf_data = post_data.get('pdf_data')
            if not pdf_data:
                _logger.error("❌ No PDF data provided")
                return self._json_response({'error': 'No PDF data provided'}, 400)
            
            # Validar contacts
            contacts = post_data.get('contacts', [])
            if not contacts:
                _logger.error("❌ No contacts provided")
                return self._json_response({'error': 'No contacts provided'}, 400)
            
            # URL del webhook de n8n 
            n8n_webhook_url = request.env['ir.config_parameter'].sudo().get_param(
                'medical_report.n8n_webhook_url',
                'https://n8n.jumpjibe.com/webhook/medical-report'
            )
            
            _logger.info(f"🌐 Usando webhook n8n: {n8n_webhook_url}")
            
            # Preparar payload para n8n
            payload = {
                'pdf_data': pdf_data,
                'pdf_name': post_data.get('pdf_name', 'reporte_medico.pdf'),
                'contacts': contacts,
                'subject': post_data.get('subject', 'Reporte Médico'),
                'body': post_data.get('body', ''),
                'res_model': post_data.get('res_model'),
                'res_id': post_data.get('res_id'),
                'timestamp': post_data.get('timestamp', datetime.now().isoformat()),
                'company_name': post_data.get('company_name', ''),
                'doctor_name': post_data.get('doctor_name', ''),
                'doctor_title': post_data.get('doctor_title', '')
            }
            
            _logger.info(f"📤 Enviando a n8n: {len(payload['contacts'])} contactos")
            
            # Enviar a n8n
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Odoo-Medical-Report/1.0'
            }
            
            response = requests.post(
                n8n_webhook_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                _logger.info(f"✅ Reporte enviado exitosamente a n8n: {response.status_code}")
                result = {
                    'success': True,
                    'message': f'Reporte enviado correctamente a {len(payload["contacts"])} contacto(s)',
                    'n8n_response': response.json() if response.content else {},
                    'sent_to': [contact.get('name', 'Contacto') for contact in payload['contacts']]
                }
                return self._json_response(result)
            else:
                _logger.error(f"❌ Error de n8n: {response.status_code} - {response.text}")
                return self._json_response({
                    'error': f'Error del servidor n8n: {response.status_code}',
                    'details': response.text[:500]
                }, 500)
                
        except Exception as e:
            _logger.error(f"❌ Error inesperado en send_to_n8n: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return self._json_response({'error': f'Error inesperado: {str(e)}'}, 500)

    def _json_response(self, data, status=200):
        """Helper para devolver respuestas JSON consistentes"""
        return Response(
            json.dumps(data),
            status=status,
            content_type='application/json'
        )

    # Endpoint de debug mejorado
    @http.route('/medical_report/debug', type='http', auth='user', methods=['GET', 'POST'])
    def debug_endpoint(self, **kwargs):
        """Endpoint de debug para verificar que el controlador funciona"""
        _logger.info("🔍 Debug endpoint llamado")
        
        # Mostrar información de la request para debugging
        debug_info = {
            'status': 'ok',
            'message': 'Endpoint medical_report/send_to_n8n está funcionando',
            'timestamp': str(datetime.now()),
            'request_method': request.httprequest.method,
            'content_type': request.httprequest.content_type,
            'has_data': bool(request.httprequest.data),
            'post_params': list(kwargs.keys()) if kwargs else []
        }
        
        # Si es POST, mostrar los datos recibidos
        if request.httprequest.method == 'POST' and request.httprequest.data:
            try:
                raw_data = request.httprequest.data.decode('utf-8')
                debug_info['raw_data'] = raw_data
                if raw_data:
                    debug_info['parsed_data'] = json.loads(raw_data)
            except Exception as e:
                debug_info['data_error'] = str(e)
        
        return self._json_response(debug_info)