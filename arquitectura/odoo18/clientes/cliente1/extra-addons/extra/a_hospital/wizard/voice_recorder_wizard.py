from odoo import models, fields

class VoiceRecorderWizard(models.TransientModel):
    _name = 'a_hospital.voice_recorder.wizard'
    _description = 'Wizard para grabación de voz'
    
    diagnosis_id = fields.Many2one('a_hospital.diagnosis', required=True)
    final_message = fields.Text(string='Mensaje Generado')
    
    def action_open_voice_recorder(self):
        """Abrir el grabador de voz"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'name': 'Grabador de Voz',
            'tag': 'chatter_voice_note.audio_to_text',
            'target': 'new',
            'params': {
                'resModel': self._name,
                'resId': self.id,
            }
        }
    
    def action_save_to_diagnosis(self):
        """Guardar el mensaje en el diagnóstico y cerrar wizard"""
        self.ensure_one()
        if self.final_message and self.diagnosis_id:
            self.diagnosis_id.write({
                'description': self.final_message
            })
        return {'type': 'ir.actions.act_window_close'}