# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
 
_logger = logging.getLogger(__name__)


class MiContacto(models.Model):
    _name = 'reactodoo.micontacto'
    _description = 'Mi Modelo de Contacto Personalizado'
    # Añadimos un campo extra, por ejemplo, un campo booleano
    es_preferido = fields.Boolean(string='Contacto Preferido')
    descripcion_ai = fields.Text(string='Descripción Generada por AI')
    
    def generar_descripcion_ai(self):
        service = self.env['openai.service']
        for record in self:
            prompt = f"Genera una breve descripción de venezuela"
            record.descripcion_ai = service.generate_text(prompt)
     