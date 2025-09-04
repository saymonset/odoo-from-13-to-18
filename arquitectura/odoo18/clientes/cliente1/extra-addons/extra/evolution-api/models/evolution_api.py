# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import base64
from odoo.http import request
_logger = logging.getLogger(__name__)


class Evolution_api(models.Model):
    _name = 'evolution_api'
    _description = 'Evolution_api'

    name = fields.Char(string='Name', required=True)
    api_url = fields.Char(string='API URL', required=True, default='https://evolution.jumpjibe.com')
    api_key = fields.Char(string='API Key', required=True)
    instance_id = fields.Char(string='Instance ID')
    status = fields.Selection([
        ('disconnected', 'Desconectado'),
        ('connected', 'Conectado'),
        ('pending', 'Pendiente'),
    ], string='Estado', default='disconnected', readonly=True)
    qr_code = fields.Binary(string='Código QR', attachment=True)
    
    @api.model
    def _get_base_url(self):
        return request.httprequest.host  # O usa config['web.base.url']
    
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
        url = f"{self.api_url}/instance/create"
        headers = {'apikey': self.api_key, 'Content-Type': 'application/json'}
        body = {
            'instanceName': self.name,
            'qrcode': True,
        }
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 201:
            data = response.json()
            self.instance_id = data.get('instance', {}).get('instanceName')
            self.status = 'pending'
            self.get_qr_code()
        else:
            raise UserError(_('Error al crear instancia: %s') % response.text)
    
    def get_qr_code(self):
        self.ensure_one()
        url = f"{self.api_url}/instance/connect/{self.name}"
        headers = {'apikey': self.api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            qr_base64 = data.get('base64')  # Asumiendo que devuelve {'base64': 'data:image/png;base64,...'}
            if qr_base64:
                if ',' in qr_base64:
                    qr_base64 = qr_base64.split(',')[1]
                self.qr_code = base64.b64decode(qr_base64)
        else:
            raise UserError(_('Error al obtener QR: %s') % response.text)     
        
    def test_connection(self):
        self.ensure_one()
        url = f"{self.api_url}/instance/fetchInstances/{self.name}"  # Asumiendo endpoint para estado
        headers = {'apikey': self.api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.status = data.get('status', 'disconnected')
        else:
            raise UserError(_('Error en conexión: %s') % response.text)   
        
    def set_webhook(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        webhook_url = f"{base_url}/whatsapp/webhook/{self.name}"
        url = f"{self.api_url}/webhook/{self.name}"
        headers = {'apikey': self.api_key, 'Content-Type': 'application/json'}
        body = {
            'url': webhook_url,
            'events': ['messages.upsert', 'connection.update'],  # Para mensajes recibidos y actualizaciones de conexión
            'enabled': True
        }
        response = requests.post(url, json=body, headers=headers)
        if not response.ok:
            raise UserError(_('Error al configurar webhook: %s') % response.text)
    
    def send_message(self, number, text):
        self.ensure_one()
        if self.status != 'connected':
            raise UserError(_('Instancia no conectada.'))
        url = f"{self.api_url}/message/sendText/{self.name}"
        headers = {'apikey': self.api_key, 'Content-Type': 'application/json'}
        body = {
            'number': number + '@c.us',  # Formato para números individuales
            'text': text
        }
        response = requests.post(url, json=body, headers=headers)
        if not response.ok:
            raise UserError(_('Error al enviar mensaje: %s') % response.text)
        return True
     
    def update_status(self, new_status):
        self.status = new_status
    
