# -*- coding: utf-8 -*-
import json
import logging
from odoo import api, models, fields
from odoo.http import request

_logger = logging.getLogger(__name__)

class AudioToTextService(models.TransientModel):
    _name = 'audio_to_text.service'
    _description = 'Audio to Text Service Layer'

    # === CAMPOS DE INSTANCIA ===
    final_message = fields.Text(string="Mensaje Final", readonly=True)
    answer_ia = fields.Text(string="Respuesta IA", readonly=True)

    # === MÉTODO QUE CREA UNA INSTANCIA Y LLENA LOS CAMPOS ===
    @api.model
    def process_info(self, final_message=None, answer_ia=None):
        """
        Crea una instancia del servicio y procesa la información
        """
        # Crear una nueva instancia del servicio
        service_instance = self.create({
            'final_message': final_message or '',
            'answer_ia': answer_ia or '',
        })
        
        _logger.info(f"Instancia creada - ID: {service_instance.id}")
        _logger.info(f"final_message: {bool(service_instance.final_message)}")
        _logger.info(f"answer_ia: {bool(service_instance.answer_ia)}")
        
        return service_instance.get_processed_data()

    # === MÉTODO DE INSTANCIA ===
    def get_processed_data(self):
        """
        Devuelve final_message y answer_ia SOLO si ambos tienen datos válidos.
        """
        if not self.final_message or not self.final_message.strip():
            _logger.warning("final_message no está disponible o está vacío.")
            return {}

        if not self.answer_ia or not self.answer_ia.strip():
            _logger.warning("answer_ia no está disponible o está vacío.")
            return {}
        
        response = {
            'final_message': f"saymon dice -> {self.final_message.strip()}",
            'answer_ia': self.answer_ia.strip(),
        }
        return response