from odoo import models, fields


class UnidadMedida(models.Model):
    _name = "catalogo.unidad.medida"
    _rec_name = "descripcion"

    clave = fields.Char(string="Clave")
    descripcion = fields.Char(string="Descripción")
