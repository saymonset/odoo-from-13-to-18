# -*- coding: utf-8 -*-

import logging
import locale
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time
from ..dto.get_info_whatsapp_dto import  InfoWhatsAppDto
from datetime import datetime

_logger = logging.getLogger(__name__)
try:
    locale.setlocale(locale.LC_TIME, 'es_VE.UTF-8')
except locale.Error:
    # Fallback a un locale más común
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') 

class GetDataUseCase(models.TransientModel):
    _name = 'get_data.use.case'
    _description = 'Get data Use Case'

    @api.model
    def execute(self, options)->dict:
        try:
            data = options.get('data')
            
            remote_jid = data.get('data', {}).get('key', {}).get('remoteJid')
            apikey = data.get('apikey')
            instance = data.get('instance')
            sender = data.get('sender')
            message_type = data.get('data', {}).get('messageType')
            # conversation = data.get('data', {}).get('message', {}).get('conversation')
            # base64 = data.get('data', {}).get('message', {}).get('base64')
            message = data.get('data', {}).get('message', {})
            conversation = message.get('conversation')
            base64_str = message.get('base64')
            audio_message = message.get("audioMessage", {})
            media_url = audio_message.get("url")
            client_phone = None
            # Validar client_phone
            client_phone = None
            if remote_jid and '@' in remote_jid:
                client_phone = remote_jid.split('@')[0]
            else:
                raise ValidationError("No se pudo extraer el client_phone de remoteJid")
            
            host_phone = None
            if sender and '@' in sender:
                host_phone = sender.split('@')[0]
            else:
                raise ValidationError("No se pudo extraer el host_phone de sender")
            

            # Validar que todos los campos requeridos estén presentes
            if not all([host_phone, client_phone, message_type, instance, apikey]):
                missing_fields = [field for field, value in [
                    ("host_phone", host_phone),
                    ("client_phone", client_phone),
                    ("message_type", message_type),
                    ("instance", instance),
                    ("apikey", apikey)
                ] if not value]
                raise ValidationError(f"Faltan campos requeridos: {', '.join(missing_fields)}")
          
            # Crear la instancia de InfoWhatsAppDto
            infoWhatsAppDto = InfoWhatsAppDto(
                host_phone=host_phone,
                client_phone=client_phone,
                message_type=message_type,
                conversation=conversation,
                instance=instance,
                apikey=apikey,
                base64 = base64_str,
                media_url = media_url,
                timestamp = datetime.now()
            )

            # Convertir la instancia de InfoWhatsAppDto a un diccionario para devolverla
            return infoWhatsAppDto.dict()
             

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}