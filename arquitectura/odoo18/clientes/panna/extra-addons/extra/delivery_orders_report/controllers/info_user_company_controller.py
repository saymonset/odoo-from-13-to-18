from odoo import http
from ..services.info_user_company_service import user_company_service


class UserCompanyController(http.Controller):
    @http.route("/delivery_orders_report/user_company", type="json", auth="user")
    def user_company(self):
        return user_company_service(self)
