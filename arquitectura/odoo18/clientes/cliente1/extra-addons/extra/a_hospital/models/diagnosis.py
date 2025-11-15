from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import logging 
_logger = logging.getLogger(__name__)

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

  
    def action_open_voice_recorder(self):
        self.ensure_one()
        if not self.id:
            raise ValidationError(_("Debe guardar el diagnóstico antes de grabar por voz."))
        return {
            'type': 'ir.actions.client',
            'tag': 'chatter_voice_note.audio_to_text',
            'target': 'new',
            'name': 'Grabador de Voz',
        }
