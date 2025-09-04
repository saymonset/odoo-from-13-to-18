# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def send_whatsapp(self):
        instance = self.env['evolution_api'].sudo().search([('status', '=', 'connected')], limit=1)
        if instance and self.phone:
            message = "Hola, este es un mensaje de prueba desde Odoo."
            instance.send_message(self.phone, message)
            self.message_post(body=_('Mensaje WhatsApp enviado: %s') % message)
        else:
            raise UserError(_('No hay instancia conectada o número de teléfono.'))
