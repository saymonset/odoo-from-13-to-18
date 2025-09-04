# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import logging
_logger = logging.getLogger(__name__)


class Evolution_api(models.Model):
    _name = 'evolution_api'
    _description = 'Evolution_api'

    name = fields.Char(string='Name', required=True)
    api_url = fields.Char(string='API URL', required=True, default='https://evolution.jumpjibe.com')
    api_key = fields.Char(string='API Key', required=True)
    instance_id = fields.Char(string='Instance ID')
    status = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connected', 'Connected'),
        ('error', 'Error')
    ], string='Status', default='disconnected')
    qr_code = fields.Text(string='QR Code', readonly=True)
    
    def test_connection(self):
        self.ensure_one()
        try:
            url = f"{self.api_url}/instance/connectionState/{self.instance_id}"
            headers = {
                'apikey': self.api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.status = 'connected' if data.get('state') == 'open' else 'disconnected'
                self.status = 'connected'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Test',
                        'message': f'Connection successful! Status: {data.get("state")}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                self.status = 'error'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Test',
                        'message': f'Error: {response.text}',
                        'type': 'danger',
                        'sticky': False,
                    }
                }
        except Exception as e:
            _logger.error(f"Error testing connection: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Test',
                    'message': f'Error: {str(e)}',
                    'type': 'danger',
                    'sticky': False,
                }
            }
    def create_instance(self):
        self.ensure_one()
        try:
            url = f"{self.api_url}/instance/create"
            headers = {
                'apikey': self.api_key,
                'Content-Type': 'application/json'
            }
            data = {
                'instanceName': self.instance_id,
                'qrcode': True,
                'webhook': f'{self.api_url}/webhook/whatsapp'
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                # Guardar el QR code para mostrarlo
                qr_data = response.json()
                self.qr_code = qr_data.get('qrcode', {}).get('base64', '')
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'evolution.api',
                    'view_mode': 'form',
                    'res_id': self.id,
                    'views': [(False, 'form')],
                    'target': 'current',
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Create Instance',
                        'message': f'Error: {response.text}',
                        'type': 'danger',
                        'sticky': False,
                    }
                }
        except Exception as e:
            _logger.error(f"Error creating instance: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Create Instance',
                    'message': f'Error: {str(e)}',
                    'type': 'danger',
                    'sticky': False,
                }
            }
            
    def send_whatsapp_message(self, phone, message):
        self.ensure_one()
        try:
            url = f"{self.api_url}/message/sendText/{self.instance_id}"
            headers = {
                'apikey': self.api_key,
                'Content-Type': 'application/json'
            }
            data = {
                'number': phone,
                'text': message
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                _logger.info(f"Message sent to {phone}")
                return True
            else:
                _logger.error(f"Error sending message: {response.text}")
                return False
        except Exception as e:
            _logger.error(f"Error sending message: {str(e)}")
            return False
