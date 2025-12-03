# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'
    is_igtf = fields.Boolean(string='¿Este pago incluye un impuesto?', default=False)
    igtf_percentage = fields.Float(string='Porcentaje del impuesto', default=0.0, help='Porcentaje del impuesto que se aplica a esta transacción. Si desea incluir este impuesto, marque la opción anterior.')

    
    @api.model
    def _load_pos_data_fields(self, config_id):
        # Llama al método original para obtener los campos existentes
        params = super(PosPaymentMethod, self)._load_pos_data_fields(config_id)
        # Añade los nuevos campos a la lista de parámetros
        params += ['is_igtf', 'igtf_percentage']
        return params
