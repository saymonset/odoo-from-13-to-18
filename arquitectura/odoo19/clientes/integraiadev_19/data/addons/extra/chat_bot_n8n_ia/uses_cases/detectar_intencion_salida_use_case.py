# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api

_logger = logging.getLogger(__name__)

class DetectarIntencionSalidaUseCase(models.TransientModel):
    _name = 'detectar.intencion.salida.use.case'
    _description = 'Detecta si un mensaje del usuario expresa intención de salir/cancelar'

    @api.model
    def execute(self, options):
        """
        Evalúa si el texto del usuario indica que quiere salir del flujo actual.
        :param options: dict con:
            - 'texto_usuario': string
            - 'openai_client': cliente OpenAI
            - 'model': modelo a usar (ej. 'gpt-3.5-turbo')
            - 'max_tokens': opcional, default 100
        :return: dict con 'es_salida' (bool) y 'mensaje' (string de despedida si es salida)
        """
        texto = options.get('texto_usuario', '')
        openai_client = options.get('openai_client')
        model = options.get('model', 'gpt-3.5-turbo')
        max_tokens = options.get('max_tokens', 100)

        if not texto:
            _logger.error("No se proporcionó texto para evaluar intención de salida")
            return {"es_salida": False, "mensaje": ""}
        if not openai_client:
            _logger.error("No se proporcionó cliente de OpenAI")
            return {"es_salida": False, "mensaje": ""}

        try:
            system_content = """
            Eres un asistente experto en detectar intenciones de cancelación o salida.
            Analiza el mensaje del usuario y determina si quiere ABANDONAR o CANCELAR el proceso actual por completo.
            Palabras clave que indican salida: salir, cancelar, volver al menú, no quiero continuar, abandonar, déjalo, después lo hago, etc.
            
            IMPORTANTE: 
            - Si el usuario dice que ha TERMINADO o FINALIZADO de realizar una acción (ej: "ya está", "listo", "ya terminé de subir las fotos", "es suficiente"), eso NO es una intención de salida. Es solo la confirmación de que terminó su tarea y desea continuar con el siguiente paso.
            - Solo marca "es_salida": true si el usuario explícitamente quiere detener el chatbot o irse.
            
            Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
            {"es_salida": true/false, "mensaje": "mensaje de despedida amigable si es salida, si no, cadena vacía"}
            
            Si es salida, genera un mensaje de despedida corto y amable, que incluya la opción de retomar después.
            """

            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": texto}
                ],
                max_tokens=max_tokens,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            data = json.loads(content)
            return {
                "es_salida": data.get("es_salida", False),
                "mensaje": data.get("mensaje", "")
            }

        except Exception as e:
            _logger.error(f"Error detectando intención de salida: {str(e)}")
            # Fallback simple basado en palabras clave
            texto_lower = texto.lower()
            palabras_salida = ['salir', 'cancelar', 'terminar', 'menu', 'menú', 'volver', 'atrás', 'abortar', 'no']
            es_salida = any(p in texto_lower for p in palabras_salida)
            mensaje = "Entendido. Si deseas continuar más tarde, aquí estaremos. ¡Hasta pronto!" if es_salida else ""
            return {"es_salida": es_salida, "mensaje": mensaje}