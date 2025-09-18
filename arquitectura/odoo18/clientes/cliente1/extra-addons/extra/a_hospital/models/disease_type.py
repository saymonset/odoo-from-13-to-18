from odoo import models, fields

class DiseaseType(models.Model):
    """
    Modelo para clasificar enfermedades por tipo.
    """
    _name = 'a_hospital.disease.type'
    _description = 'Disease Type'

    name = fields.Char(string="Type Name", required=True)
    description = fields.Text()
    disease_ids = fields.One2many(
        comodel_name='a_hospital.disease',
        inverse_name='disease_type_id',  # CORREGIDO
        string='Diseases of this Type',
    )
