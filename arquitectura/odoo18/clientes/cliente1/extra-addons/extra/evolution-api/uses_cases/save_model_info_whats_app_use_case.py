# -*- coding: utf-8 -*-
import logging
from odoo import models, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SaveModelInfoWhatsAppUseCase(models.TransientModel):
    _name = 'save_model_info_whats_app.use.case'
    _description = 'Save WhatsApp Data Use Case'



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
            whatsapp_record = self.env['model.info_whats_app'].sudo().create_from_dto(info)
           # Forzar el commit de la transacción
            self.env.cr.commit()  # Esto es necesario para persistir los datos
            
            _logger.info("Record created successfully with ID: %s", whatsapp_record.id)
            
            # Verificar que el registro existe realmente
            record_exists = self.env['model.info_whats_app'].sudo().search([('id', '=', whatsapp_record.id)])
            _logger.info("Record verification - exists: %s", bool(record_exists))
             
     
            # Devolver un diccionario con la información relevante, por ejemplo el ID
            return {
                'id': whatsapp_record.id,
                'host_phone': whatsapp_record.host_phone,
                'client_phone': whatsapp_record.client_phone,
                'message_type': whatsapp_record.message_type,
                'instance': whatsapp_record.instance,
                'apikey': whatsapp_record.apikey,
                'conversation': whatsapp_record.conversation,
                'timestamp': whatsapp_record.timestamp,
                'thread_id': whatsapp_record.thread_id,
            }

        except ValidationError as ve:
            raise
        except Exception as e:
            _logger.error("Error processing request: %s", str(e), exc_info=True)
            return {"error": f"Processing error: {str(e)}"}
