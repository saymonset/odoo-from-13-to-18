from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Disease(models.Model):
    """
    Modelo que representa una enfermedad en el sistema hospitalario.
    Soporta jerarquía y clasificación por tipo.
    """
    _name = 'a_hospital.disease'
    _description = 'Hospital Disease'
    _parent_store = True
    _parent_name = "parent_id"
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string="Disease Name", required=True)
    complete_name = fields.Char(
        compute='_compute_complete_name',
        recursive=True,
        store=True)
    description = fields.Text()
    parent_id = fields.Many2one(
        comodel_name='a_hospital.disease',
        string='Parent Disease',
        ondelete='cascade',
    )
    child_ids = fields.One2many(
        comodel_name='a_hospital.disease',
        inverse_name='parent_id',
        string='Child Diseases',
    )
    parent_path = fields.Char(index=True)
    disease_type_id = fields.Many2one(
        comodel_name='a_hospital.disease.type',
        string='Disease Type',
        required=False
    )

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """
        Previene la creación de jerarquías cíclicas.
        """
        for record in self:
            if record._has_cycle():
                raise ValidationError(_('You cannot create recursive hierarchy.'))

    def _has_cycle(self):
        """
        Detecta si hay un ciclo en la jerarquía.
        """
        if not self.parent_id:
            return False
        visited_ids = {self.id}
        current_parent = self.parent_id
        while current_parent:
            if current_parent.id in visited_ids:
                return True
            visited_ids.add(current_parent.id)
            current_parent = current_parent.parent_id
        return False

    @api.depends('name', 'parent_id')
    def _compute_complete_name(self):
        """
        Genera el nombre completo jerárquico.
        """
        for disease in self:
            if disease.parent_id:
                disease.complete_name = '%s / %s' % (
                    disease.parent_id.complete_name,
                    disease.name)
            else:
                disease.complete_name = disease.name