# chatter_voice_note/models/res_partner_inherit.py
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def web_save(self, ids, vals, **kwargs):
        """
        Método seguro para actualizar partners desde OWL/JS.
        Se espera args: [[id1, id2, ...], {field: value, ...}]
        Devuelve dict con status para evitar RPC exceptions.
        """
        try:
            # Validaciones simples
            if not isinstance(ids, (list, tuple)):
                _logger.warning("web_save: ids no es lista: %r", ids)
                return {"status": "error", "message": "ids debe ser una lista de IDs"}

            if not isinstance(vals, dict):
                _logger.warning("web_save: vals no es dict: %r", vals)
                return {"status": "error", "message": "vals debe ser un diccionario"}

            partners = self.browse(ids)
            if not partners:
                _logger.warning("web_save: no se encontraron partners para ids=%s", ids)
                return {"status": "error", "message": "Partners no encontrados"}

            # write con sudo si quieres evitar errores por permisos:
            partners.sudo().write(vals)

            _logger.info("web_save: actualizados partners %s con %s por usuario %s", partners.ids, vals, self.env.uid)
            return {"status": "ok", "updated_ids": partners.ids}
        except Exception as e:
            _logger.exception("Error en web_save: %s", e)
            # devolvemos un mensaje legible al frontend en vez de lanzar la excepción
            return {"status": "error", "message": str(e)}