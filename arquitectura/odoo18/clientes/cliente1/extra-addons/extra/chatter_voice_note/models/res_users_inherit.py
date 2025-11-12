# chatter_voice_note/models/res_users_inherit.py
from odoo import api, models

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def get_current_user_info(self):
        """Retorna información básica del usuario actual"""
        user = self.env.user
        return {
            "userId": user.id,
            "name": user.name or "",
            "login": user.login or "",
            "email": user.email or "",
            "partner_id": user.partner_id.id if user.partner_id else False,
        }
