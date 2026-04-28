# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api

_logger = logging.getLogger(__name__)

class GenerarMensajeFinalizacionUseCase(models.TransientModel):
    _name = 'generar.mensaje.finalizacion.use.case'
    _description = 'Genera un mensaje amigable de éxito al completar un flujo'

    @api.model
    def execute(self, options):
        """
        Genera un mensaje de felicitación y confirmación cuando el usuario termina el formulario.
        :param options: dict con:
            - 'datos_paciente': dict con los datos recolectados (al menos 'solicitar_name')
            - 'openai_client': cliente OpenAI
            - 'model': modelo a usar
            - 'max_tokens': opcional, default 150
        :return: dict con 'mensaje_final' (string)
        """
        datos = options.get('datos_paciente', {})
        openai_client = options.get('openai_client')
        model = options.get('model', 'gpt-3.5-turbo')
        max_tokens = options.get('max_tokens', 150)

        if not openai_client:
            _logger.error("No se proporcionó cliente de OpenAI")
            return {"mensaje_final": "¡Gracias por completar el formulario! Nos pondremos en contacto contigo pronto."}

        try:
            system_content = """
            Eres un asistente amable de un sistema de salud. El usuario acaba de completar exitosamente un formulario de agendamiento.
            Con los datos proporcionados (pueden estar parcialmente completos), genera un mensaje de agradecimiento y confirmación.
            El mensaje debe ser breve, cálido, y si el nombre está presente, úsalo. 
            No incluyas tecnicismos. Responde ÚNICAMENTE con el texto del mensaje, sin formato JSON.
            Ejemplo: "¡Gracias, Juan! Hemos recibido tu información. En breve uno de nuestros asesores se contactará contigo. ¡Que tengas un excelente día!"
            """

            nombre = datos.get('solicitar_name', '')
            prompt = f"Nombre: {nombre} - Datos adicionales: {json.dumps(datos)}"

            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.5,
            )

            mensaje = response.choices[0].message.content.strip()
            # Limpiar posibles comillas o escapes
            mensaje = mensaje.strip('"').strip("'")
            return {"mensaje_final": mensaje}

        except Exception as e:
            _logger.error(f"Error generando mensaje de finalización: {str(e)}")
            fallback = "¡Gracias por completar el formulario! Nos pondremos en contacto contigo a la brevedad. ¡Que tengas un excelente día!"
            return {"mensaje_final": fallback}