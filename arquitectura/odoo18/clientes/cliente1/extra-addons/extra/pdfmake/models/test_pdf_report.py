# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json

class TestPdfReport(models.Model):
    _name = 'test.pdf.report'
    _description = 'Modelo de prueba para reportes PDFMake'

    name = fields.Char("Nombre", default="Cliente de Prueba")
    amount = fields.Float("Importe", default=15899.50)
    active = fields.Boolean("Activo", default=True)
    partner_id = fields.Many2one('res.partner', string="Contacto")
    
    def action_generate_pdf(self):
        """Acción para generar PDF"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'pdfmake_download',  # Debe coincidir con el nombre del registro
            'params': {
                'name': self.name,
                'amount': self.amount,
                'active': self.active,
                'partner_name': self.partner_id.display_name if self.partner_id else 'Ninguno',
                'record_id': self.id
            }
        }

