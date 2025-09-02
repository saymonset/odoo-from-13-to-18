import json
import tempfile
import os
from odoo import http
from odoo.http import request, Response
import logging
from ..dto.orthography_dto import OrthographyDto
from ..dto.text_to_audio_dto import  TextToAudioDto

from pydantic import ValidationError
_logger = logging.getLogger(__name__)

class GptController(http.Controller):

    @http.route('/gpt/ortografia',type='json', auth='public',csrf=False)
    def ortografia(self, **kw):
        try:
            # Validar y parsear los datos de entrada con el DTO
            try:
                dto = OrthographyDto(**kw)
            except ValidationError as e:
                return {'error': f'Datos inválidos: {e.errors()}'}
            
            prompt = kw.get('prompt', '')
            if not prompt:
                return {'error': 'No prompt provided'}
            max_tokens = kw.get('max_tokens')
            
            service = http.request.env['gpt.service']
            result = service.orthography_check(prompt, max_tokens)
            return result
        except Exception as e:
            return {'error': str(e)}
   
    @http.route('/gpt/text-to-audio',type='http', auth='public',csrf=False)
    def text_to_audio(self, **kw):
        try:
           # Validar y parsear los datos de entrada con el DTO
            try:
                dto = TextToAudioDto(**kw)
            except ValidationError as e:
                return {'error': f'Datos inválidos: {e.errors()}'}
            
            prompt = kw.get('prompt', '')
            if not prompt:
                return {'error': 'No prompt provided'}
            voice = kw.get('voice')
            
            service = http.request.env['gpt.service']
            file_path = service.textToAudio(prompt, voice)
            # Preparar respuesta con el archivo de audio
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            response = Response(
                audio_data,
                status=200,
                mimetype='audio/mp3'
            )
            response.headers.set('Content-Disposition', 'attachment; filename=audio.mp3')
            
            # Limpiar archivo temporal si lo deseas
            #os.unlink(file_path)
            
            return response
        except Exception as e:
            _logger.error(f"Error en text_to_audio: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                mimetype='application/json'
            )
                
    @http.route('/gpt/getaudio',type='http', auth='public',csrf=False)
    def getaudio(self, **kw):
        try:
            fileId = kw.get('fileId', '')
            if not fileId:
                return {'error': 'No fileId provided'}
            
            service = http.request.env['gpt.service']
            file_path = service.getAudio(fileId)
            # Preparar respuesta con el archivo de audio
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            response = Response(
                audio_data,
                status=200,
                mimetype='audio/mp3'
            )
            response.headers.set('Content-Disposition', 'attachment; filename=audio.mp3')
            
            # Limpiar archivo temporal si lo deseas
            #os.unlink(file_path)
            
            return response
        except Exception as e:
            _logger.error(f"Error en text_to_audio: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                mimetype='application/json'
            )