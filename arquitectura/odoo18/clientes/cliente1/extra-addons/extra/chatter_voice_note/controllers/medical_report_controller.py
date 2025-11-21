import json
import logging
import requests
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class MedicalReportController(http.Controller):

    @http.route('/medical_report/send_to_n8n', type='json', auth='user', methods=['POST'], csrf=False)
    def send_medical_report_to_n8n(self, **post):
        """
        Envía el reporte médico al webhook de n8n
        """
        try:
            # Los datos vienen en el cuerpo de la petición JSON
            # Para type='json', Odoo automáticamente parsea el JSON
            pdf_data = post.get('pdf_data')
            if not pdf_data:
                return {'error': 'No PDF data provided'}
            
            # URL del webhook de n8n, test: test-medical-report
            # n8n_webhook_url = request.env['ir.config_parameter'].sudo().get_param(
            #     'medical_report.n8n_webhook_url',
            #     'https://n8n.jumpjibe.com/webhook/test-medical-report'
            # )
            # URL del webhook de n8n, produccion: medical-report
            n8n_webhook_url = request.env['ir.config_parameter'].sudo().get_param(
                'medical_report.n8n_webhook_url',
                'https://n8n.jumpjibe.com/webhook/medical-report'
            )
            
            # Preparar los datos para n8n
            payload = {
                'pdf_data': pdf_data,
                'pdf_name': post.get('pdf_name'),
                'contacts': post.get('contacts', []),
                'subject': post.get('subject'),
                'body': post.get('body'),
                'res_model': post.get('res_model'),
                'res_id': post.get('res_id'),
                'timestamp': post.get('timestamp'),
                'company_name': post.get('company_name'),
                'doctor_name': post.get('doctor_name'),
                'doctor_title': post.get('doctor_title')
            }
            
            _logger.info(f"Enviando reporte médico a n8n: {post.get('pdf_name')}")
            
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
            
            if response.status_code in [200, 201]:
                _logger.info(f"✅ Reporte enviado exitosamente a n8n: {response.status_code}")
                return {
                    'success': True,
                    'message': 'Reporte enviado correctamente a n8n',
                    'n8n_response': response.json() if response.content else {}
                }
            else:
                _logger.error(f"❌ Error de n8n: {response.status_code} - {response.text}")
                return {
                    'error': f'Error del servidor n8n: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            _logger.error(f"❌ Error inesperado: {str(e)}")
            return {'error': f'Error inesperado: {str(e)}'}