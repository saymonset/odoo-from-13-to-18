from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _

class Diagnosis(models.Model):
    _name = 'a_hospital.diagnosis'
    _description = 'Diagnosis'
    
    # Campos
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Archivos Adjuntos',
        help='Documentos, imágenes u otros archivos relacionados con el diagnóstico'
    )
    
    visit_id = fields.Many2one(
        comodel_name='a_hospital.visit',
        string='Visit',
    )

    doctor_id = fields.Many2one(
        comodel_name='a_hospital.doctor',
        string='Doctor',
    )

    disease_id = fields.Many2one(
        comodel_name='a_hospital.disease',
        string='Disease',
    )

    patient_id = fields.Many2one(
        comodel_name='a_hospital.patient',
        string='Patient',
    )

    # ⭐⭐ SOLO UNA DEFINICIÓN - YA CORREGIDO
    description = fields.Text(
        string='Diagnosis Description',
        help='Additional information or notes regarding the diagnosis'
    )

    is_approved = fields.Boolean(
        string='Approved',
        default=False,
        help="""This sign indicates that the given diagnosis,
                made by the mentor doctor,
                has been verified and approved by his mentor."""
    )

    doctor_approved = fields.Char(
        string='Doctor approved'
    )

    disease_type_id = fields.Many2one(
        related='disease_id.disease_type_id',
        comodel_name='a_hospital.disease.type',
        string='Disease Type',
        store=True,
        readonly=True
    )

    # Método para actualizar desde el módulo de voz
    def update_description_from_voice(self, final_message):
        """Actualiza el campo description con el mensaje del módulo de voz"""
        if final_message:
            self.write({'description': final_message})
        return True

    # 🔥 CORREGIDO: Método para abrir el grabador de voz
    def action_open_voice_recorder(self):
        """Abre el wizard de grabación de voz para este diagnóstico"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Grabar Diagnóstico por Voz',
            'res_model': 'chatter_voice_note.voice_recorder_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 'a_hospital.diagnosis',
                'default_res_id': self.id,
                'default_custom_request_id': f'diagnosis_{self.id}',  # 🔥 PREFIJO ESPECÍFICO
            }
        }