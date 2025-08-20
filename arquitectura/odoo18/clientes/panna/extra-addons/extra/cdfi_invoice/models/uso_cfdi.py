from odoo import models, fields


class UsoCfdi(models.Model):
    _name = "catalogo.uso.cfdi"
    _rec_name = "description"

    code = fields.Char(string="Clave")
    description = fields.Char(string="Descripción")
