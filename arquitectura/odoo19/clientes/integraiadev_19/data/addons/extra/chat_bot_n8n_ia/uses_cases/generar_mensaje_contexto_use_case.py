 # -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api

_logger = logging.getLogger(__name__)

class GenerarMensajeContextoUseCase(models.TransientModel):
    _name = 'generar.mensaje.contexto.use.case'
    _description = 'Genera mensajes amigables según el contexto (sin sesión, expirado, sin pasos)'

    @api.model
    def execute(self, options):
        """
        Genera un mensaje personalizado para un contexto específico.
        :param options: dict con:
            - 'contexto': string, puede ser 'sin_sesion', 'expirado', 'sin_pasos'
            - 'texto_usuario': (opcional) el último mensaje del usuario
            - 'openai_client': cliente OpenAI
            - 'model': modelo a usar (ej. 'gpt-3.5-turbo')
            - 'max_tokens': opcional, default 150
        :return: dict con 'mensaje' (string)
        """
        contexto = options.get('contexto')
        texto_usuario = options.get('texto_usuario', '')
        openai_client = options.get('openai_client')
        model = options.get('model', 'gpt-3.5-turbo')
        max_tokens = options.get('max_tokens', 150)

        if not contexto:
            _logger.error("No se proporcionó contexto para generar mensaje")
            return {"mensaje": ""}
        if not openai_client:
            _logger.error("No se proporcionó cliente de OpenAI")
            return {"mensaje": "Lo siento, no puedo responder en este momento."}

        # Descripción del contexto para la IA
        descripcion_contexto = {
            'sin_sesion': 'El usuario envió un mensaje pero no hay una conversación activa (no existe sesión).',
            'expirado': 'La sesión del usuario expiró por inactividad (10 minutos sin actividad).',
            'sin_pasos': 'El usuario ya completó un flujo anteriormente y no hay pasos pendientes, pero la sesión aún existe.'
        }.get(contexto, f'Contexto desconocido: {contexto}')

        system_content = f"""
Eres un asistente amable de un sistema de salud. Tu objetivo es generar un mensaje breve, cálido y claro para el usuario, según la situación que se describe a continuación.

Situación: {descripcion_contexto}
El usuario acaba de escribir: "{texto_usuario}" (si está vacío, ignóralo).

Debes:
- Explicar brevemente qué ocurrió (sin tecnicismos).
- Invitar al usuario a comenzar un nuevo proceso o acción.
- Mantener un tono empático y humano.
- Máximo 2 frases.

Responde ÚNICAMENTE con un JSON en este formato: {{ "mensaje": "texto del mensaje" }}
"""

        try:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": f"Contexto: {contexto}"}
                ],
                max_tokens=max_tokens,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            mensaje = data.get("mensaje", "")
            if not mensaje:
                raise ValueError("No se encontró mensaje en la respuesta")
            return {"mensaje": mensaje}
        except Exception as e:
            _logger.error(f"Error generando mensaje de contexto '{contexto}': {e}")
            # Fallbacks claros
            fallbacks = {
                'sin_sesion': "No tengo una conversación activa. ¿Te gustaría comenzar de nuevo?",
                'expirado': "Tu sesión ha expirado por inactividad. Por favor, inicia un nuevo proceso.",
                'sin_pasos': "Ya habías completado el proceso anterior. ¿Necesitas algo más?"
            }
            return {"mensaje": fallbacks.get(contexto, "Lo siento, hubo un error. Por favor, intenta de nuevo.")}