# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ModelInfo_whats_app(models.Model):
    _name = 'model.info_whats_app'
    _description = 'ModelInfo_whats_app'
    _order = 'timestamp desc'

    conversation_ia = fields.Char('conversation_ia', help="AI conversation summary or response")
    host_phone = fields.Char('Host Phone', required=True, help="Phone number of the host")
    client_phone = fields.Char('Client Phone', required=True, help="Phone number of the client")
    message_type = fields.Char('Message Type', required=True, help="Type of message")
    instance = fields.Char('Instance', required=True, help="Instance identifier")
    apikey = fields.Char('API Key', required=True, help="API key for authentication")
    conversation = fields.Text('Conversation', help="Message content or conversation text")
    timestamp = fields.Datetime('Timestamp', default=fields.Datetime.now, 
                               help="Timestamp of the message")
    
    # Campo adicional solicitado
    thread_id = fields.Char('Thread ID', help="Unique identifier for the conversation thread")
    
    @api.depends('host_phone', 'client_phone', 'timestamp')
    def _compute_name(self):
        """Genera un nombre descriptivo para el registro"""
        for record in self:
            if record.host_phone and record.client_phone and record.timestamp:
                record.name = f"{record.host_phone}-{record.client_phone}-{record.timestamp.strftime('%Y%m%d_%H%M')}"
            else:
                record.name = "New WhatsApp Message"
    
    @api.model
    def create_from_dto(self, dto_data):
        """Método auxiliar para crear registros desde el DTO"""
        try:
            # Preparar datos con valores por defecto para evitar errores
            create_data = {
                'host_phone': dto_data.get('host_phone', ''),
                'client_phone': dto_data.get('client_phone', ''),
                'message_type': dto_data.get('message_type', ''),
                'instance': dto_data.get('instance', ''),
                'apikey': dto_data.get('apikey', ''),
                'conversation': dto_data.get('conversation', ''),
                'timestamp': dto_data.get('timestamp', fields.Datetime.now()),
                'thread_id': dto_data.get('thread_id', ''),
                'conversation_ia': dto_data.get('conversation_ia', ''),
            }
            
            _logger.info("Creating record with data: %s", create_data)
            record = self.create(create_data)
            _logger.info("Record created successfully: %s", record.id)
            return record
            
        except Exception as e:
            _logger.exception("Error creating record from DTO: %s", str(e))
            raise
    
    @api.model
    def get_last_record_info(self, client_phone):
        """
        Obtiene información del último registro para un client_phone específico.
        
        Args:
            client_phone (str): Número de teléfono del cliente a buscar.
        
        Returns:
            dict: Contiene:
                - 'thread_id' si han pasado más de 48 horas desde el último registro
                - 'conversation' si han pasado menos de 48 horas
                - None si no se encuentra ningún registro
        """
        if not client_phone:
            _logger.warning("No se proporcionó client_phone")
            return None
        
        # Buscar el último registro para el client_phone
        last_record = self.search([
            ('client_phone', '=', client_phone)
        ], order='timestamp desc', limit=1)
        
        if not last_record:
            _logger.info("No se encontraron registros para el client_phone: %s", client_phone)
            return None
        
        # Calcular la diferencia de tiempo
        now = datetime.now()
        record_time = fields.Datetime.from_string(last_record.timestamp)
        time_difference = now - record_time
        
        # Verificar si han pasado más de 48 horas
        if time_difference > timedelta(hours=48):
            _logger.info(
                "Han pasado más de 48 horas (%s) desde el último mensaje. Devolviendo thread_id: %s",
                time_difference, None
            )
            return None
        else:
            _logger.info(
                "Han pasado menos de 48 horas (%s) desde el último mensaje. Devolviendo thread_id: %s",
                 time_difference, last_record.thread_id
            )
            return last_record.thread_id
 
 
 