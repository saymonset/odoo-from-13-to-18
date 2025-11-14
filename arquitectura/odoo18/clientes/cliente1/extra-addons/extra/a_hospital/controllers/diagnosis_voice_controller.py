from odoo import http
from odoo.http import request
import json

class DiagnosisVoiceController(http.Controller):
    
    @http.route('/hospital/diagnosis/update_voice_description', type='json', auth='user', methods=['POST'])
    def update_voice_description(self, **kwargs):
        """Endpoint para actualizar el diagnóstico desde el módulo de voz"""
        try:
            diagnosis_id = kwargs.get('diagnosis_id')
            final_message = kwargs.get('final_message')
            
            if not diagnosis_id or not final_message:
                return {'success': False, 'message': 'Datos incompletos'}
            
            diagnosis = request.env['a_hospital.diagnosis'].browse(int(diagnosis_id))
            if diagnosis.exists():
                diagnosis.update_description_from_voice(final_message)
                return {
                    'success': True, 
                    'message': 'Diagnóstico actualizado correctamente desde voz'
                }
            return {'success': False, 'message': 'Diagnóstico no encontrado'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}