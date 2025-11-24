# -*- coding: utf-8 -*-
from odoo import models, fields

class PDFPrinter(models.Model):
    _name = 'pdfmake.printer'
    _description = 'PDFMake Printer Service'

    name = fields.Char(string='Nombre', required=True, default='PDF Printer Service')
    use_local_fonts = fields.Boolean(
        string='Usar Fuentes Locales',
        default=True,
        help='Usar fuentes incluidas en el módulo'
    )