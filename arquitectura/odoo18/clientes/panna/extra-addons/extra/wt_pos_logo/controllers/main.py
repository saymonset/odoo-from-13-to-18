# Copyright (C) Wisenetic Technologies.
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.binary import Binary


class Main(http.Controller):
    @http.route("/web/binary/pos_logo", type="http", auth="public")
    def pos_logo(self):
        config = request.env["pos.config"].sudo().search([], limit=1)
        if config.logo_option == "custom":
            return (
                request.env["ir.binary"]
                ._get_image_stream_from(
                    config,
                    field_name="custom_logo",
                )
                .get_response()
            )
        else:
            return Binary().company_logo()

    @http.route("/web/binary/pos_sceen_saver", type="http", auth="public")
    def pos_screen_saver(self):
        config = request.env["pos.config"].sudo().search([], limit=1)
        return (
            request.env["ir.binary"]
            ._get_image_stream_from(
                config,
                field_name="saver_background",
            )
            .get_response()
        )
