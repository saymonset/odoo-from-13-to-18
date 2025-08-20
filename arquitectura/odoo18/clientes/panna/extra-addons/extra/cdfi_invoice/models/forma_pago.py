from odoo import models, fields


class FormaPago(models.Model):
    _name = "catalogo.forma.pago"
    _description = "catalogo forma pago"
    _rec_name = "description"

    code = fields.Char(string="Clave")
    description = fields.Char(string="Descripción")
