# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ModelInfo_whats_app(models.Model):
    _name = 'model.info_whats_app'
    _description = 'ModelInfo_whats_app'

    name = fields.Char('Name')
