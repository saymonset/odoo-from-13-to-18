# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class GenerarPreguntaIntegraiaUseCase(models.TransientModel):
    _name = 'generar_pregunta_integraia.use.case'
    _description = 'generar_pregunta_integraia_use_case - Genera preguntas amigables a partir de un campo'

    @api.model
    def execute(self, options):
        """
        Ejecuta el caso de uso para generar una pregunta amigable basada en el prompt.
        :param options: Diccionario con opciones, debe contener 'prompt' (ej: "Teléfono")
        :return: Diccionario con la pregunta generada y otros metadatos
        """
        prompt = options.get('prompt', '')
        openai_client = options.get('openai_client')
        max_tokens = options.get('max_tokens', 150)
        model = options.get('model', 'gpt-3.5-turbo')

        if not prompt:
            _logger.error("No se proporcionó un prompt (nombre_mostrar) para generar la pregunta")
            return {"error": "No se proporcionó un prompt"}
        if not openai_client:
            _logger.error("No se proporcionó el cliente de OpenAI")
            return {"error": "Configuración de OpenAI incorrecta"}

        try:
            system_content = """
            Eres un asistente que convierte nombres de campos (como "Teléfono", "Nombre completo", "Cédula") 
            en preguntas amigables y naturales en español para un formulario de chat o asistente virtual.
            Debes responder ÚNICAMENTE en formato JSON con la siguiente estructura:
            {
                "pregunta_amigable": "texto de la pregunta generada"
            }

            Reglas:
            - La pregunta debe ser cordial, clara y adecuada para el contexto de una conversación.
            - No incluyas información adicional fuera del JSON.
            - Si el prompt es "Teléfono", podrías generar: "¿Cuál es tu número de teléfono?"
            - Si es "Nombre completo": "¿Podrías indicarme tu nombre completo?"
            - Si es "Cédula": "¿Cuál es tu número de cédula?" o "¿Me compartes tu cédula?"
            - Si es "Fecha de nacimiento": "¿Cuál es tu fecha de nacimiento? (ejemplo: 15/05/1990)"
            - Sé empático y no uses lenguaje robótico.
            """

            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            response_content = response.choices[0].message.content

            try:
                json_resp = json.loads(response_content)
                generated_question = json_resp.get("pregunta_amigable", "")
                if not generated_question:
                    raise ValueError("No se encontró 'pregunta_amigable' en la respuesta")
            except (json.JSONDecodeError, ValueError) as e:
                _logger.error(f"Respuesta inválida de OpenAI: {response_content}")
                # Fallback: generar una pregunta por defecto
                generated_question = f"Por favor, ingresa tu {prompt.lower()}"

            return {
                "original_prompt": prompt,
                "generated_question": generated_question,
                "status": "success"
            }

        except Exception as e:
            _logger.error(f"Error al generar la pregunta: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}