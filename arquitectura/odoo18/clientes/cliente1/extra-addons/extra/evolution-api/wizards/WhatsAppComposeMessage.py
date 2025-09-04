# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class WhatsAppComposeMessage(models.TransientModel):
    _name = 'whatsappcomposemessage'
    _description = _('WhatsAppComposeMessage')

    partner_id = fields.Many2one('res.partner', string='Partner')
    phone = fields.Char(string='Phone', required=True)
    message = fields.Text(string='Message', required=True)

    def action_send_message(self):
        self.ensure_one()
        # Obtener la configuración activa de Evolution API
        evolution_api = self.env['evolution_api'].search([('status', '=', 'connected')], limit=1)
        if evolution_api:
            success = evolution_api.send_whatsapp_message(self.phone, self.message)
            if success:
                # Registrar en el chatter del partner
                self.partner_id.message_post(
                    body=f"WhatsApp message sent: {self.message}",
                    subject="WhatsApp Message"
                )
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Message Sent',
                        'message': 'WhatsApp message sent successfully',
                        'type': 'success',
                        'sticky': False,
                    }
                }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error',
                'message': 'Failed to send WhatsApp message',
                'type': 'danger',
                'sticky': False,
            }
        }