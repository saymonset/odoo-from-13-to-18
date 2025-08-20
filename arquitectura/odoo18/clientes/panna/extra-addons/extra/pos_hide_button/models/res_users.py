import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    pos_hide_refund = fields.Boolean(
        string="Hide Refund Button", default=False, help="Hide Refund Button in POS"
    )
    pos_hide_general_note = fields.Boolean(
        string="Hide General Note", default=False, help="Hide General Note in POS"
    )
    pos_hide_customer_note = fields.Boolean(
        string="Hide Customer Note", default=False, help="Hide Custom Note in POS"
    )
    pos_hide_pricelist = fields.Boolean(
        string="Hide Pricelist Button",
        default=False,
        help="Hide Pricelist Button in POS",
    )
    pos_hide_cancel_order = fields.Boolean(
        string="Hide Cancel Order Button",
        default=False,
        help="Hide Cancel Order Button in POS",
    )
    pos_hide_quotations_order = fields.Boolean(
        string="Hide Quotations Order Button",
        default=False,
        help="Hide Quotations Order Button in POS",
    )
    pos_hide_actions = fields.Boolean(
        string="Hide Actions Button", default=False, help="Hide Actions Button in POS"
    )
