import json
import tempfile
import os
from odoo import http
import time
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
            
            
            
    @http.route('/gpt/audio-to-text', type='http', auth='public', csrf=False)
    def audio_to_text(self, **kw):
        # Acceder al archivo enviado
        file_storage = http.request.httprequest.files.get('file')
        if not file_storage:
            return http.Response('No file uploaded', status=400)

        # Validar tipo de archivo (ejemplo: audio)
        if not file_storage.mimetype.startswith('audio/'):
            return http.Response('Invalid file type', status=400)

        # Validar tamaño (ejemplo: 5 MB)
        file_storage.seek(0, os.SEEK_END)
        file_size = file_storage.tell()
        file_storage.seek(0)
        if file_size > 5 * 1024 * 1024:
            return http.Response('File is bigger than 5 MB', status=400)

        # Guardar el archivo con nombre único
        ext = file_storage.filename.split('.')[-1]
        filename = f"{int(time.time())}.{ext}"
        
        # Ruta absoluta del directorio donde está este archivo Python
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Subir una carpeta y luego ir a generated/upload
        upload_dir = os.path.abspath(os.path.join(current_dir, '..', 'generated', 'upload'))

        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            file_storage.save(f)

        service = http.request.env['gpt.service']
        prompt = kw.get('prompt', '')
        response = service.audioToText(file_path,prompt)
        

        return http.Response(f'File uploaded as {response}', status=200)