# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time

_logger = logging.getLogger(__name__)

class TextToAudioUseCase(models.TransientModel):
    _name = 'text_to_audio.use.case'
    _description = 'Text to Audio Use Case'

    @api.model
    def execute(self, options):
        """
        Ejecuta el caso de uso de texto llevarlo a audio
        :param options: Diccionario con opciones, debe contener 'prompt'
        :return: Diccionario con resultados
        """
        prompt = options.get('prompt', '')
        openai_client = options.get('openai_client')
        model = options.get('model', 'gpt-3.5-turbo')  # Obtenemos el modelo de las opciones
        
        voices = {
            'nova': 'nova',
            'alloy': 'alloy',
            'echo': 'echo',
            'fable': 'fable',
            'onyx': 'onyx',
            'shimmer': 'shimmer',
        }

        selected_voice = voices.get(options.get('voice'), 'nova')
        
         # Carpeta donde se guardarán los audios
        folder_path = Path(__file__).parent.resolve() / '../generated/audios/'
        folder_path = folder_path.resolve()
        os.makedirs(folder_path, exist_ok=True)

        # Nombre único para el archivo
        speech_file = folder_path / f"{int(time.time() * 1000)}.mp3"
        
        if not prompt:
            _logger.error("No se proporcionó un prompt para la verificación ortográfica")
            return {"error": "No se proporcionó un prompt"}
        if not openai_client:
            _logger.error("No se proporcionó el cliente de OpenAI")
            return {"error": "Configuración de OpenAI incorrecta"}
        
        try:
            # Asegurarse de que el texto esté en español
            # Puedes añadir un prefijo para garantizar que se use español
            spanish_prompt = f"Texto en español: {prompt}"
            
            response = openai_client.audio.speech.create(
                model='tts-1',  # Usamos el modelo desde las opciones
                voice=selected_voice,
                input=spanish_prompt,
                response_format='mp3',
            )
            
            # Guardar el archivo MP3
            audio_bytes = response.content if hasattr(response, 'content') else response  # Ajusta según la versión de la librería
            with open(speech_file, 'wb') as f:
                f.write(audio_bytes)

            return str(speech_file)

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}