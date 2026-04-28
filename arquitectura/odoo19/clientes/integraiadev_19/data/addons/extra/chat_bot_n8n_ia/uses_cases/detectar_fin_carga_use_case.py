# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api

_logger = logging.getLogger(__name__)

class DetectarFinCargaUseCase(models.TransientModel):
    _name = 'detectar.fin.carga.use.case'
    _description = 'Detecta si el usuario ha terminado de subir archivos/imágenes'

    @api.model
    def execute(self, options):
        """
        Determina si el mensaje del usuario indica que ya terminó de subir archivos.
        :param options: Diccionario con:
            - 'texto_usuario': el mensaje del usuario
            - 'openai_client': cliente OpenAI
            - 'model': modelo de IA
            - 'max_tokens': máx tokens
        :return: Diccionario con:
            - 'termino': bool
        """
        texto_usuario = options.get('texto_usuario', '')
        openai_client = options.get('openai_client')
        model = options.get('model', 'gpt-3.5-turbo')
        max_tokens = options.get('max_tokens', 100)

        if not texto_usuario:
            return {'termino': False}

        # 1. Búsqueda rápida por palabras clave comunes (ahorra llamadas a API)
        keywords = ['listo', 'ya', 'listo ya', 'ya termine', 'ya terminé', 'listo termine', 'suficiente', 'es suficiente', 'no mas', 'no más', 'ok', 'listo eso es todo', 'no', 'ninguna', 'no gracias']
        if texto_usuario.lower().strip() in keywords:
            return {'termino': True}

        # 2. Si no es obvio, consultar a la IA
        if openai_client:
            return self._detectar_con_ia(texto_usuario, openai_client, model, max_tokens)
        
        return {'termino': False}

    def _detectar_con_ia(self, texto_usuario, openai_client, model, max_tokens):
        system_content = """
Eres un clasificador de intención. Tu tarea es determinar si el usuario ha terminado de subir fotos o documentos en un chat.

Ejemplos de frases que indican que TERMINÓ:
- "listo"
- "ya los mandé"
- "eso es todo"
- "no tengo más"
- "continuar"
- "ya"
- "es suficiente"

Ejemplos de frases que indican que NO ha terminado:
- "espera"
- "mando otra"
- "falta una"
- "aquí va la otra"

Responde ÚNICAMENTE con un JSON en este formato: { "termino": true/false }
"""
        try:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": texto_usuario}
                ],
                max_tokens=max_tokens,
                temperature=0.0, # Queremos precisión máxima
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            return {'termino': data.get("termino", False)}
        except Exception as e:
            _logger.error(f"Error detectando fin de carga con IA: {e}")
            return {'termino': False}
