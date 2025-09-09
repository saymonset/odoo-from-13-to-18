# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo.http import request
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
        Processes call IA
        
        Args:
            options (dict): Input data containing WhatsApp message details.
        
        Returns:
            dict: Processed data or error information.
        """
        try:
            info = options.get('data', {})
            
            #LLamamos al modulo externo IA
            serviceIA = request.env['dixon.service']
            
            threadId = info.get('thread_id', '')
            
            if not threadId:
                id = serviceIA.createThread(None)
                threadId = id.get('id')
                info['thread_id'] = threadId
                _logger.info("Nuevo threadId creado: %s", str(threadId)) 
           
           
            question = info.get('conversation', '')
            
            serviceIA.createMessage(threadId,question)
            
            run = serviceIA.createRun(threadId)
            
            result = serviceIA.checkCompleteStatusRun(threadId,run.id)
            
            messages = serviceIA.getMessageList(threadId)
            
            respAssistentIA= messages[-1] if messages else {}
            
            messageIA = respAssistentIA.get('content', 'No response from AI')
            
            info['conversation_ia'] = messageIA
            

            return info

        except ValidationError as ve:
            raise
        except Exception as e:
            _logger.error("Error processing request: %s", str(e), exc_info=True)
            return {"error": f"Processing error: {str(e)}"}
