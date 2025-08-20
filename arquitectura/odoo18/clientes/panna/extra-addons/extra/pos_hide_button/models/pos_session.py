from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    pos_hide_refund = fields.Boolean(string="Hide Refund Button", default=False)

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        loaded_data["pos_hide_refund"] = self.env.user.pos_hide_refund
