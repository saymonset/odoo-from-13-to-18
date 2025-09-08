# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from odoo import models, api
from odoo.exceptions import ValidationError
from ..dto.get_info_whatsapp_dto import InfoWhatsAppDto

_logger = logging.getLogger(__name__)

class GetDataUseCase(models.TransientModel):
    _name = 'get_data.use.case'
    _description = 'Get WhatsApp Data Use Case'

    @staticmethod
    def _extract_phone(phone_str: str, field_name: str) -> str:
        """Extracts and validates phone number from a string."""
        if not phone_str or '@' not in phone_str:
            raise ValidationError(f"Invalid format in {field_name}")
        return phone_str.split('@', 1)[0]

    @api.model
    def execute(self, options: dict) -> dict:
        """
        Processes WhatsApp data and returns formatted response.
        
        Args:
            options (dict): Input data containing WhatsApp message details.
        
        Returns:
            dict: Processed data or error information.
        """
        try:
            data = options.get('data', {})
            
            # Define required fields mapping
            required_fields = {
                'remoteJid': 'client_phone',
                'sender': 'host_phone',
                'messageType': 'message_type',
                'instance': 'instance',
                'apikey': 'apikey'
            }

            # Extract and validate fields in a single pass
            extracted = {}
            missing_fields = []
            for field, key in required_fields.items():
                value = data.get(field)
                if not value:
                    missing_fields.append(field)
                    continue
                
                extracted[key] = (
                    self._extract_phone(value, field)
                    if field in ('remoteJid', 'sender')
                    else value
                )

            # Check for missing fields
            if missing_fields:
                raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

            # Create DTO with validated data
            info_whatsapp_dto = InfoWhatsAppDto(
                conversation=data.get('conversation', ''),
                timestamp=datetime.now(),
                **extracted
            )

            return info_whatsapp_dto.dict()

        except ValidationError as ve:
            raise
        except Exception as e:
            _logger.error("Error processing request: %s", str(e), exc_info=True)
            return {"error": f"Processing error: {str(e)}"}
