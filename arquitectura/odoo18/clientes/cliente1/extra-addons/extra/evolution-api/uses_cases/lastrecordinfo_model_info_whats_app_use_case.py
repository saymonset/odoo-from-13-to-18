# -*- coding: utf-8 -*-
import logging
from odoo import models, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SaveModelInfoWhatsAppUseCase(models.TransientModel):
    _name = 'lastrecordinfo_model_info_whats_app_use_case'
    _description = 'Last Record WhatsApp Data Use Case'



    @api.model
    def execute(self, options: dict) -> dict:
        """
        Processes WhatsApp data save and returns formatted response.
        
        Args:
            options (dict): Input data containing WhatsApp message details.
        
        Returns:
            dict: Processed data or error information.
        """
        try:
            info = options.get('data')
            # Forzar el commit de la transacción
            result = self.env['model.info_whats_app'].sudo().get_last_record_info(info.get('client_phone', ''))
            
            # Devolver un diccionario con la información relevante, por ejemplo el ID
            return result

        except ValidationError as ve:
            raise
        except Exception as e:
            _logger.error("Error processing request: %s", str(e), exc_info=True)
            return {"error": f"Processing error: {str(e)}"}
