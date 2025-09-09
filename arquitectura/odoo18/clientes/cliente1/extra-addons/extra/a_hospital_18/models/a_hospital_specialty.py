# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class A_hospitalSpecialty(models.Model):
    _name = 'a_hospital.specialty'
    _description = 'A_hospitalSpecialty'

    name = fields.Char(string="Specialty Name", required=True)
    description = fields.Text()
