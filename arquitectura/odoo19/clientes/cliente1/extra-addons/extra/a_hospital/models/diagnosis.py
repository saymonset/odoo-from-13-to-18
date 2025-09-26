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

    description = fields.Text()

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

      
    description = fields.Text()
 
     