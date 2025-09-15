from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _


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

      
    description = fields.Text()
 
     