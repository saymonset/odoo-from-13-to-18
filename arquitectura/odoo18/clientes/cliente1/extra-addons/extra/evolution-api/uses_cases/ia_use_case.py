# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import models, api
from odoo.exceptions import ValidationError
from ..dto.get_info_whatsapp_dto import InfoWhatsAppDto

_logger = logging.getLogger(__name__)

class IaUseCase(models.TransientModel):
    _name = 'ia.use.case'
    _description = 'IA Case'

 

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
            

            return info_whatsapp_dto.dict()

        except ValidationError as ve:
            raise
        except Exception as e:
            _logger.error("Error processing request: %s", str(e), exc_info=True)
            return {"error": f"Processing error: {str(e)}"}
