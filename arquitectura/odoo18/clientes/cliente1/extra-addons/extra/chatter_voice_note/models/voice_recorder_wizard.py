# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VoiceRecorderWizard(models.TransientModel):
    _name = 'chatter_voice_note.voice_recorder_wizard'
    _description = 'Voice Recorder Wizard'
    
    # Campos para almacenar la información del registro relacionado
    res_model = fields.Char(string='Related Model', required=True)
    res_id = fields.Integer(string='Related Record ID', required=True)
    custom_request_id = fields.Char(string='Custom Request ID')
    
    # 🔥 MÉTODO PARA CERRAR Y GUARDAR
    def action_save_and_close(self):
        """Guarda el resultado y cierra el wizard"""
        return {'type': 'ir.actions.act_window_close'}
    
    # 🔥 MÉTODO PARA OBTENER EL REGISTRO RELACIONADO
    def get_related_record(self):
        """Obtiene el registro relacionado basado en res_model y res_id"""
        if self.res_model and self.res_id:
            return self.env[self.res_model].browse(self.res_id)
        return None
    
    # 🔥 MÉTODO PARA ACTUALIZAR EL REGISTRO RELACIONADO CON LA RESPUESTA
    def update_related_record(self, final_message):
        """Actualiza el registro relacionado con el mensaje final"""
        record = self.get_related_record()
        if record and final_message:
            # Si el modelo es diagnóstico, actualiza el campo description
            if self.res_model == 'a_hospital.diagnosis' and hasattr(record, 'description'):
                record.write({'description': final_message})
                return True
            # Para otros modelos, podrías adaptar según sea necesario
        return False