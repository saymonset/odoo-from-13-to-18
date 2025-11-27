import json
import tempfile
import os
from odoo import http
import time
from odoo.http import request, Response
import logging
from ..dto.question_dto import  QuestionDto

from pydantic import ValidationError
_logger = logging.getLogger(__name__)

class DixonGptController(http.Controller):

    @http.route('/dixon/create-thread',type='json', auth='public',csrf=False)
    def createThread(self, **kw):
        try:
            # Validar y parsear los datos de entrada con el DTO
            try:
                dto = QuestionDto(**kw)
            except ValidationError as e:
                return {'error': f'Datos inválidos: {e.errors()}'}
            
            threadId = kw.get('threadId', '')
            if not threadId:
                return {'error': 'No threadId provided'}
            
            service = http.request.env['dixon.service']
            service.createThread(threadId)
        
            # Retornar solo el id en un diccionario
            return service.createThread(threadId)
        except Exception as e:
            return {'error': str(e)}
        
    @http.route('/dixon/user-question',type='json', auth='public',csrf=False)
    def userQuestion(self, **kw):
        try:
            # Validar y parsear los datos de entrada con el DTO
            try:
                dto = QuestionDto(**kw)
            except ValidationError as e:
                return {'error': f'Datos inválidos: {e.errors()}'}
            
            threadId = kw.get('threadId', '')
            if not threadId:
                return {'error': 'No threadId provided'}
            
            question = kw.get('question', '')
            if not question:
                return {'error': 'No question provided'}
             
            
            service = http.request.env['dixon.service']
            
            message = service.createMessage(threadId,question)
            
            run = service.createRun(threadId)
            
            result = service.checkCompleteStatusRun(threadId,run.id)
            
            messages = service.getMessageList(threadId)
            
            return messages
        
        except Exception as e:
            return {'error': str(e)}
        
    # @http.route('/dixon/user-run',type='json', auth='public',csrf=False)
    # def userRun(self, **kw):
    #     try:
    #         # Validar y parsear los datos de entrada con el DTO
    #         try:
    #             dto = QuestionDto(**kw)
    #         except ValidationError as e:
    #             return {'error': f'Datos inválidos: {e.errors()}'}
            
    #         threadId = kw.get('threadId', '')
    #         if not threadId:
    #             return {'error': 'No threadId provided'}
            
    #         service = http.request.env['dixon.service']
    #         result = service.createRun(threadId)
    #         return result
    #     except Exception as e:
    #         return {'error': str(e)}
   
    