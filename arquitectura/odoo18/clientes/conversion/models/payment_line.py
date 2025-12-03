# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class PaymentLine(models.Model):
    _inherit = 'pos.payment'

    amount_saymon = fields.Monetary(
        string='Rent Amount Saymon',
        compute='_compute_amount_saymon',  # Declaramos el campo como computado
        store=True,  # Guardamos el valor en la base de datos
        help="Enter rent amount per month"
    )

    @api.depends('amount')  # Indicamos que depende del campo 'amount'
    def _compute_amount_saymon(self):
        for line in self:
            _logger.info("************************start**************************")
            amount = line.amount  # Obtén el monto original
            _logger.debug(f"Monto original: {amount}")
            # Aplica tu lógica personalizada (ejemplo: dividir entre 60)
            line.amount_saymon = amount / 60 if amount else 0.0
            _logger.info(f"Monto personalizado: {line.amount_saymon}")
            _logger.info("************************end**************************")