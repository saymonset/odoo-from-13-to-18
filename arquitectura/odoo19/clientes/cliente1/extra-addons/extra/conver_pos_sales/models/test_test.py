# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class TestTest(models.Model):
    _name = 'test.test'
    _description = 'TestTest'

    name = fields.Char('Name')
