# -*- coding: utf-8 -*-

import logging
import json
from datetime import datetime
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class ValidacionAmigableUseCase(models.TransientModel):
    _name = 'validacion.amigable.use.case'
    _description = 'Validación de valores con mensajes de error humanos generados por IA'

    @api.model
    def execute(self, options):
        """
        Valida un valor según tipo de dato y paso, y si falla, genera un mensaje de error amigable con IA.
        :param options: Diccionario con:
            - 'valor': el valor a validar
            - 'tipo_dato': text, integer, float, date, datetime, boolean, image, selection
            - 'paso': (opcional) identificador como 'solicitar_phone' para reglas especiales
            - 'nombre_mostrar': (opcional) nombre amigable del campo, ej. "Teléfono"
            - 'openai_client': cliente OpenAI
            - 'model': modelo de IA (ej. 'gpt-3.5-turbo')
            - 'max_tokens': (opcional, default 150)
        :return: Diccionario con:
            - 'success': bool
            - 'valor_transformado': valor convertido (si success True)
            - 'mensaje': mensaje de error amigable (si success False)
            - 'usando_ia': bool (si se usó IA para generar el mensaje)
        """
        valor = options.get('valor')
        tipo_dato = options.get('tipo_dato')
        paso = options.get('paso')
        nombre_mostrar = options.get('nombre_mostrar', paso or tipo_dato)
        openai_client = options.get('openai_client')
        model = options.get('model', 'gpt-3.5-turbo')
        max_tokens = options.get('max_tokens', 150)

        # 1. Validación tradicional (rígida pero precisa)
        es_valido, resultado = self._validacion_tradicional(valor, tipo_dato, paso)

        if es_valido:
            return {
                'success': True,
                'valor_transformado': resultado,
                'mensaje': '',
                'usando_ia': False
            }

        # 2. Si falló y tenemos IA, generar mensaje amigable
        if openai_client:
            mensaje_personalizado = self._generar_mensaje_error_con_ia(
                valor, tipo_dato, paso, nombre_mostrar, resultado,
                openai_client, model, max_tokens
            )
            return {
                'success': False,
                'valor_transformado': None,
                'mensaje': mensaje_personalizado,
                'usando_ia': True
            }
        else:
            # Fallback sin IA (mensaje original robótico)
            return {
                'success': False,
                'valor_transformado': None,
                'mensaje': resultado,  # mensaje de error tradicional
                'usando_ia': False
            }

    # ------------------------------------------------------------
    # Validación tradicional (copia exacta de tu lógica actual)
    # ------------------------------------------------------------
    @staticmethod
    def _validacion_tradicional(valor, tipo_dato, paso=None):
        """Devuelve (bool, valor_transformado_o_mensaje_error)"""
        # Validaciones especiales por paso
        if paso == 'solicitar_phone':
            if not valor:
                return False, "El teléfono no puede estar vacío"
            valor_str = str(valor).strip()
            digits = ''.join(filter(str.isdigit, valor_str))
            if not digits:
                return False, "El teléfono debe contener al menos un dígito"
            if len(digits) < 7:
                return False, "El teléfono debe tener al menos 7 dígitos (incluyendo código de área)"
            return True, valor_str

        # Si no hay paso especial, validar según tipo_dato
        if tipo_dato == 'text':
            return True, valor
        elif tipo_dato == 'integer':
            try:
                return True, int(valor)
            except:
                return False, "Debe ser un número entero"
        elif tipo_dato == 'float':
            try:
                return True, float(valor)
            except:
                return False, "Debe ser un número decimal"
        elif tipo_dato == 'date':
            formatos = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%d.%m.%Y',
                '%m/%d/%Y',
            ]
            valor_str = str(valor).strip()
            for fmt in formatos:
                try:
                    fecha = datetime.strptime(valor_str, fmt).date()
                    return True, fecha.isoformat()
                except ValueError:
                    continue
            return False, "Fecha inválida. Use formato DD/MM/YYYY o YYYY-MM-DD"
        elif tipo_dato == 'datetime':
            try:
                dt = fields.Datetime.from_string(valor)
                return True, dt.isoformat()
            except:
                return False, "Fecha y hora inválida"
        elif tipo_dato == 'boolean':
            if isinstance(valor, bool):
                return True, valor
            if isinstance(valor, str):
                v = valor.lower()
                if v in ['true', '1', 'yes', 'sí']:
                    return True, True
                elif v in ['false', '0', 'no']:
                    return True, False
            return False, "Debe ser un booleano (true/false)"
        elif tipo_dato == 'image':
            if not valor:
                return False, "No se recibió ninguna imagen"
            import re
            valor_str = str(valor).strip()
            # Validación básica de URL
            if not re.match(r'^https?://', valor_str):
                return False, "El valor proporcionado no parece ser un enlace de imagen válido. Por favor, envía la imagen directamente o asegúrate de que sea un enlace (URL) que comience con http o https."
            return True, valor_str
        elif tipo_dato == 'selection':
            return True, valor
        else:
            return False, f"Tipo de dato no soportado: {tipo_dato}"

    # ------------------------------------------------------------
    # Generación de mensaje amigable con IA
    # ------------------------------------------------------------
    def _generar_mensaje_error_con_ia(self, valor, tipo_dato, paso, nombre_mostrar,
                                      error_tradicional, openai_client, model, max_tokens):
        """Usa OpenAI para crear un mensaje de error empático y claro."""
        system_content = f"""
Eres un asistente experto en atención al cliente. Tu tarea es convertir mensajes de error técnicos y fríos en explicaciones amigables, empáticas y útiles para un usuario final en un chat.

El usuario intentó ingresar un valor para el campo "{nombre_mostrar}" (tipo de dato: {tipo_dato}).
- Valor ingresado: "{valor}"
- Razón del error técnico: "{error_tradicional}"

Debes generar un único mensaje de error que:
- Sea cordial y no culpabilice al usuario.
- Explique brevemente qué salió mal y cómo solucionarlo.
- Use un tono cercano, como si fuera un asistente humano.
- No incluya tecnicismos como "formato inválido" a menos que sea muy necesario.
- Sea corto (máximo 2 frases).

Ejemplos:
- Para un teléfono muy corto: "El número que ingresaste parece muy corto 😅. Por favor, escríbelo completo con el código de área, por ejemplo 0412 1234567."
- Para una fecha con formato equivocado: "No pude reconocer la fecha. ¿Podrías escribirla como día/mes/año? Por ejemplo: 15/05/1990."
- Para un error de imagen (no es URL o no carga): "¡Ups! No pude abrir la imagen que enviaste 🖼️. ¿Podrías intentar enviarla de nuevo o asegurarte de que sea un enlace válido?"

Responde ÚNICAMENTE con un JSON en este formato: {{ "mensaje_amigable": "texto del mensaje" }}
"""
        try:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": f"Error al validar '{valor}' para {nombre_mostrar}"}
                ],
                max_tokens=max_tokens,
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            return data.get("mensaje_amigable", error_tradicional)
        except Exception as e:
            _logger.error(f"Error generando mensaje amigable con IA: {e}")
            return error_tradicional