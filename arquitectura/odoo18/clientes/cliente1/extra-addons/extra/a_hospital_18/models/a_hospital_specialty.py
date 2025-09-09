# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class A_hospitalSpecialty(models.Model):
    _name = 'a_hospital.specialty'
    _description = 'A_hospitalSpecialty'
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Specialty name must be unique!'),
    ]

    name = fields.Char(string="Specialty Name", required=True)
    description = fields.Text()
    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name:
                raise ValidationError(_("Specialty name is required."))
            if len(record.name) > 100:
                raise ValidationError(_("Specialty name cannot exceed 100 characters."))
