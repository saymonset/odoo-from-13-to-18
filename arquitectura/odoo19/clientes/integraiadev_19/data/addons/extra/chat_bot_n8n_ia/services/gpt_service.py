# -*- coding: utf-8 -*-
import os
from pathlib import Path
import logging
import json
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

_logger = logging.getLogger(__name__)

class GptService(models.TransientModel):
    _name = 'gpt.service'
    _description = 'GPT Service Layer'
    
    @api.model
    def _get_openai_config(self):
        """Obtiene la configuración de OpenAI"""
        config = self.env['openai.config'].sudo().search([('active', '=', True)], limit=1)
        if not config:
            raise ValidationError(_('Configura la clave de API de OpenAI en Ajustes.'))
        return config
    
    @api.model
    def orthography_check(self, prompt, max_tokens=None):
        """Verificación ortográfica usando el caso de uso"""
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['orthography.use.case']
        options = {"prompt": prompt,
                   "max_tokens": max_tokens,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
         
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    
    @api.model
    def textToAudio(self, prompt, voice=None):
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['text_to_audio.use.case']
        options = {"prompt": prompt,
                   "voice": voice,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
         
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
    @api.model
    def getAudio(self, file_id):
        # Obtener la ruta base donde se guardan los audios
            folder_path = Path(__file__).parent.resolve() / '../generated/audios/'
            folder_path = folder_path.resolve()
            
            # Construir la ruta completa del archivo
            file_path = folder_path / f"{file_id}.mp3"
            if not file_path.exists():
                raise ValidationError(_('El archivo de audio no existe.'))
            return str(file_path)
        
        
    @api.model
    def audioToText(self, file_path, prompt=''):
            config = self._get_openai_config()
            openai_client = OpenAI(api_key=config.api_key)
            use_case = self.env['audio_to_text.use.case']
            options = {"prompt": prompt,
                    "file_path": file_path,
                    "openai_client": openai_client
                    }
            
            # Implementa aquí la lógica real de verificación ortográfica
            # Por ahora devolvemos un ejemplo básaico
            return use_case.execute(options)

    
    @api.model
    def GenerarPreguntaIntegraia(self, prompt, max_tokens=None):
        """Verificación ortográfica usando el caso de uso"""
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['generar_pregunta_integraia.use.case']
        options = {"prompt": prompt,
                   "max_tokens": max_tokens,
                   "openai_client": openai_client,
                   "model": config.default_model,  # Pasamos el modelo desde la configuración
                   }
         
        # Implementa aquí la lógica real de verificación ortográfica
        # Por ahora devolvemos un ejemplo básaico
        return use_case.execute(options)
            
    @api.model
    def validar_valor_amigable(self, valor, tipo_dato, paso=None, nombre_mostrar=None, max_tokens=None):
        """
        Valida un valor según tipo de dato y paso, y si falla, genera un mensaje de error amigable usando IA.
        :param valor: valor a validar (ej: "04121234567")
        :param tipo_dato: tipo de dato esperado (text, integer, float, date, datetime, boolean, image, selection)
        :param paso: (opcional) identificador del paso (ej: 'solicitar_phone') para validaciones especiales
        :param nombre_mostrar: (opcional) nombre amigable del campo (ej: "Teléfono", "Fecha de nacimiento")
        :param max_tokens: (opcional) máx tokens para la generación del mensaje de error
        :return: Diccionario con 'success', 'valor_transformado', 'mensaje', 'usando_ia'
        """
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['validacion.amigable.use.case']
        options = {
            "valor": valor,
            "tipo_dato": tipo_dato,
            "paso": paso,
            "nombre_mostrar": nombre_mostrar,
            "openai_client": openai_client,
            "model": config.default_model,
            "max_tokens": max_tokens or 150,
        }
        return use_case.execute(options)

    @api.model
    def detectar_intencion_salida(self, texto_usuario, max_tokens=None):
        """
        Detecta si el usuario quiere salir del flujo actual.
        :param texto_usuario: string con el mensaje del usuario
        :param max_tokens: opcional
        :return: dict con 'es_salida' (bool) y 'mensaje' (despedida si aplica)
        """
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['detectar.intencion.salida.use.case']
        options = {
            "texto_usuario": texto_usuario,
            "openai_client": openai_client,
            "model": config.default_model,
            "max_tokens": max_tokens or 100,
        }
        return use_case.execute(options)

    @api.model
    def generar_mensaje_finalizacion(self, datos_paciente, max_tokens=None):
        """
        Genera un mensaje de éxito amigable al completar el flujo.
        :param datos_paciente: dict con los datos recolectados (ej. solicitar_name, etc.)
        :param max_tokens: opcional
        :return: dict con 'mensaje_final' (string)
        """
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['generar.mensaje.finalizacion.use.case']
        options = {
            "datos_paciente": datos_paciente,
            "openai_client": openai_client,
            "model": config.default_model,
            "max_tokens": max_tokens or 150,
        }
        return use_case.execute(options)


    @api.model
    def generar_mensaje_personalizado(self, contexto, texto_usuario=None, max_tokens=None):
        """
        Genera un mensaje amigable según el contexto (sin_sesion, expirado, sin_pasos).
        :param contexto: string, uno de 'sin_sesion', 'expirado', 'sin_pasos'
        :param texto_usuario: (opcional) último mensaje del usuario
        :param max_tokens: opcional
        :return: dict con 'mensaje' (string)
        """
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['generar.mensaje.contexto.use.case']
        options = {
            "contexto": contexto,
            "texto_usuario": texto_usuario or "",
            "openai_client": openai_client,
            "model": config.default_model,
            "max_tokens": max_tokens or 150,
        }
        return use_case.execute(options)

    @api.model
    def detectar_intencion_finalizar_carga(self, texto_usuario, max_tokens=None):
        """
        Detecta si el usuario terminó de subir imágenes/archivos.
        :param texto_usuario: string
        :param max_tokens: opcional
        :return: dict con 'termino' (bool)
        """
        config = self._get_openai_config()
        openai_client = OpenAI(api_key=config.api_key)
        use_case = self.env['detectar.fin.carga.use.case']
        options = {
            "texto_usuario": texto_usuario,
            "openai_client": openai_client,
            "model": config.default_model,
            "max_tokens": max_tokens or 100,
        }
        return use_case.execute(options)