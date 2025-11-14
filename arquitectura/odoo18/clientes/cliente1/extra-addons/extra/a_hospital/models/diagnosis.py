from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import uuid

class Diagnosis(models.Model):
    """
    Model representing a diagnosis within the hospital system.

    Each diagnosis is linked to a specific visit, doctor, patient,
    and disease, with an option for approval by a mentor doctor if
    the diagnosing doctor is an intern.

    Fields:
        - visit_id (Many2one): Reference to the visit in which the diagnosis
        was made.
        - doctor_id (Many2one): Reference to the doctor who made the diagnosis.
        - disease_id (Many2one): Reference to the diagnosed disease.
        - patient_id (Many2one): Reference to the patient who received
        the diagnosis.
        - description (Text): Additional information or notes regarding
        the diagnosis.
        - is_approved (Boolean): Indicates if the diagnosis was approved
        by a mentor doctor.
        - doctor_approved (Char): Name of the mentor doctor who approved
        the diagnosis.
        - disease_type_id (Many2one): Related field showing
        the type of the diagnosed disease.
    """
    _name = 'a_hospital.diagnosis'
    _description = 'Diagnosis'
    
    # Agrega este campo para los archivos adjuntos
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

    # ⭐⭐ SOLO UNA DEFINICIÓN DEL CAMPO DESCRIPTION - ELIMINAR LA DUPLICADA ⭐⭐
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

    # ⭐⭐ ELIMINAR ESTA LÍNEA DUPLICADA ⭐⭐
    # description = fields.Text()  ← ¡QUITAR ESTA LÍNEA!
    
    # Método para actualizar desde el módulo de voz
    def update_description_from_voice(self, final_message):
        """Actualiza el campo description con el mensaje del módulo de voz"""
        if final_message:
            self.write({'description': final_message})
        return True
    
    


    def action_open_voice_recorder(self):
        """Abre el grabador de voz con un request_id que incluye el diagnosis_id"""
        self.ensure_one()
        
        # Generar request_id que incluya el diagnosis_id
        request_id = f"diagnosis_{self.id}_{uuid.uuid4().hex[:8]}"
        
        return {
            'type': 'ir.actions.client',
            'name': 'Grabador de Voz para Diagnóstico',
            'tag': 'chatter_voice_note.audio_to_text',
            'target': 'new',
            'params': {
                'resModel': self._name,
                'resId': self.id,
                'custom_request_id': request_id,  # ⭐⭐ ENVIAR REQUEST_ID PERSONALIZADO ⭐⭐
            }
        }