# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

# import datetime
from odoo import fields, models, api
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from collections import Counter
import ast
import json
import base64
import pytz

from datetime import datetime
# import pytz


class ResCompany(models.Model):
    _inherit = "res.company"

    res_display_product_wise_detail = fields.Boolean(
        string="Allow To Display Product Wise Detail"
    )
    res_display_payment_detail = fields.Boolean(
        string="Allow To Display Payment Detail"
    )
    res_category_wise_detail = fields.Boolean(
        string="Allow To Display Category Wise Detail"
    )
    res_customer_wise_detail = fields.Boolean(
        string="Allow To Display Customer Wise Detail"
    )
    res_pricelist_wise_detail = fields.Boolean(
        string="Allow To Display Pricelist Wise Detail"
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super(ResCompany, self)._load_pos_data_fields(config_id)
        result.extend(["street", "street2", "city"])
        return result


class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_session_report = fields.Boolean(string="Enable Session  Report")
    allow_posted_session_report = fields.Boolean(string="Allow Posted Session Report")
    z_report_selection = fields.Selection(
        [("pdf", "PDF"), ("receipt", "Receipt"), ("both", "Both")],
        string="Report Type",
        default="pdf",
    )

    display_product_wise_detail = fields.Boolean(
        related="company_id.res_display_product_wise_detail", readonly=False
    )
    display_payment_detail = fields.Boolean(
        related="company_id.res_display_payment_detail", readonly=False
    )
    category_wise_detail = fields.Boolean(
        related="company_id.res_category_wise_detail", readonly=False
    )
    customer_wise_detail = fields.Boolean(
        related="company_id.res_customer_wise_detail", readonly=False
    )
    pricelist_wise_detail = fields.Boolean(
        related="company_id.res_pricelist_wise_detail", readonly=False
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_enable_session_report = fields.Boolean(
        related="pos_config_id.enable_session_report", readonly=False
    )
    pos_allow_posted_session_report = fields.Boolean(
        related="pos_config_id.allow_posted_session_report", readonly=False
    )
    pos_z_report_selection = fields.Selection(
        related="pos_config_id.z_report_selection", readonly=False
    )
    pos1_display_product_wise_detail = fields.Boolean(
        related="pos_config_id.display_product_wise_detail", readonly=False
    )
    pos1_display_payment_detail = fields.Boolean(
        related="pos_config_id.display_payment_detail", readonly=False
    )
    pos1_category_wise_detail = fields.Boolean(
        related="pos_config_id.category_wise_detail", readonly=False
    )
    pos1_customer_wise_detail = fields.Boolean(
        related="pos_config_id.customer_wise_detail", readonly=False
    )
    pos1_pricelist_wise_detail = fields.Boolean(
        related="pos_config_id.pricelist_wise_detail", readonly=False
    )


class PosSession(models.Model):
    _inherit = "pos.session"

    pos_display_product_wise_detail = fields.Boolean(
        related="company_id.res_display_product_wise_detail", readonly=False
    )
    pos_display_payment_detail = fields.Boolean(
        related="company_id.res_display_payment_detail", readonly=False
    )
    pos_category_wise_detail = fields.Boolean(
        related="company_id.res_category_wise_detail", readonly=False
    )
    pos_customer_wise_detail = fields.Boolean(
        related="company_id.res_customer_wise_detail", readonly=False
    )
    pos_pricelist_wise_detail = fields.Boolean(
        related="company_id.res_pricelist_wise_detail", readonly=False
    )

    def view_session_report(self):
        return self.env.ref(
            "bi_pos_closed_session_reports.action_report_session_z"
        ).report_action(self)

    def get_current_datetime(self):
        timezone = self.env.user.tz
        print(type(datetime.now()))
        current_time = datetime.now(pytz.timezone(timezone))
        return current_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_opened_date(self):
        timezone = self.env.user.tz
        deadline = pytz.utc.localize(self.start_at)
        start_date = deadline.astimezone(pytz.timezone(timezone))
        return start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_closed_date(self):
        if self.stop_at:
            timezone = self.env.user.tz
            deadline = pytz.utc.localize(self.stop_at)
            closed_date = deadline.astimezone(pytz.timezone(timezone))
            return closed_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_session_amount_data(self):
        pos_order_ids = self.env["pos.order"].search([("session_id", "=", self.id)])
        discount_amount = 0.0
        taxes_amount = 0.0
        total_sale_amount = 0.0
        total_gross_amount = 0.0
        sold_product = {}
        partner_data = []
        product_data = []
        customer_wise_total_amount = 0
        product_wise_total_amount = 0
        for pos_order in pos_order_ids:
            # for customer details
            if pos_order.partner_id:
                dict1 = {
                    "partner_id": pos_order.partner_id.id,
                    "partner_name": pos_order.partner_id.name,
                    "amount": pos_order.amount_total,
                }
                partner_data.append(dict1)
                customer_wise_total_amount += pos_order.amount_total
            else:
                dict1 = {
                    "partner_id": 00,
                    "partner_name": "Unknown",
                    "amount": pos_order.amount_total,
                }
                partner_data.append(dict1)
                customer_wise_total_amount += pos_order.amount_total

            currency = pos_order.session_id.currency_id
            total_gross_amount += pos_order.amount_total
            for line in pos_order.lines:
                # for product details
                product_dict = {
                    "product_id": line.product_id.id,
                    "product_name": line.full_product_name,
                    "product_qty": line.qty,
                    "product_price": line.price_unit,
                }
                product_data.append(product_dict)

                for categ in line.product_id.pos_categ_ids:
                    if categ.name:
                        if categ.name in sold_product:
                            sold_product[categ.name] += line.qty
                        else:
                            sold_product.update({categ.name: line.qty})
                    else:
                        if "undefine" in sold_product:
                            sold_product["undefine"] += line.qty
                        else:
                            sold_product.update({"undefine": line.qty})
                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(
                        line.price_unit * (1 - (line.discount or 0.0) / 100.0),
                        currency,
                        line.qty,
                        product=line.product_id,
                        partner=line.order_id.partner_id or False,
                    )
                    for tax in line_taxes["taxes"]:
                        taxes_amount += tax.get("amount", 0)
                if line.discount > 0:
                    discount_amount += (
                        (line.price_unit * line.qty) * line.discount
                    ) / 100
                if line.qty > 0:
                    total_sale_amount += line.price_unit * line.qty

        # for customer details
        merged_data_customer = []
        if len(partner_data) > 0:
            partner_data.sort(key=lambda x: x["partner_id"])
            current_partner = None
            for entry in partner_data:
                if entry["partner_id"] != current_partner:
                    if current_partner is not None:
                        merged_data_customer.append(
                            {"partner_name": partner_name, "amount": total_amount}
                        )
                    current_partner = entry["partner_id"]
                    partner_name = entry["partner_name"]
                    total_amount = 0
                total_amount += entry["amount"]
            merged_data_customer.append(
                {"partner_name": partner_name, "amount": total_amount}
            )

        # for product details
        merged_data = {}
        if len(product_data) > 0:
            for entry in product_data:
                product_id = entry["product_id"]
                product_price = entry["product_price"]
                product_qty = entry["product_qty"]
                key = (product_id, product_price)
                if key in merged_data:
                    merged_data[key]["product_qty"] += product_qty
                else:
                    merged_data[key] = {
                        "product_id": product_id,
                        "product_name": entry["product_name"],
                        "product_qty": product_qty,
                        "product_price": product_price,
                    }
            merged_data_product = list(merged_data.values())
            for count_total in merged_data_product:
                qty_wise_price = (
                    count_total["product_price"] * count_total["product_qty"]
                )
                product_wise_total_amount += qty_wise_price
        else:
            merged_data_product = []

        return {
            "total_sale": total_gross_amount,
            "customer_data": merged_data_customer,
            "customer_wise_total_amount": customer_wise_total_amount,
            "product_detail_data": merged_data_product,
            "product_wise_total_amount": product_wise_total_amount,
            "discount": discount_amount,
            "tax": taxes_amount,
            "products_sold": sold_product,
            "total_gross": total_gross_amount - taxes_amount - discount_amount,
            "final_total": (total_gross_amount - discount_amount),
        }

    def get_taxes_data(self):
        order_ids = self.env["pos.order"].search([("session_id", "=", self.id)])
        taxes = {}
        for order in order_ids:
            currency = order.pricelist_id.currency_id
            for line in order.lines:
                if line.tax_ids_after_fiscal_position:
                    for tax in line.tax_ids_after_fiscal_position:
                        discount_amount = 0
                        if line.discount > 0:
                            discount_amount = (
                                (line.qty * line.price_unit) * line.discount
                            ) / 100
                        untaxed_amount = (line.qty * line.price_unit) - discount_amount
                        tax_percentage = 0
                        if tax.amount_type == "group":
                            for child_tax in tax.children_tax_ids:
                                tax_percentage += child_tax.amount
                        else:
                            tax_percentage += tax.amount

                        tax_amount = (untaxed_amount * tax_percentage) / 100
                        if tax.name:
                            if tax.name in taxes:
                                taxes[tax.name] += tax_amount
                            else:
                                taxes.update({tax.name: tax_amount})
                        else:
                            if "undefine" in taxes:
                                taxes["undefine"] += tax_amount
                            else:
                                taxes.update({"undefine": tax_amount})
        return taxes

    def get_pricelist(self):
        pos_order_ids = self.env["pos.order"].search([("session_id", "=", self.id)])
        pricelist = {}
        for pos_order in pos_order_ids:
            if pos_order.pricelist_id.name:
                if pos_order.pricelist_id.name in pricelist:
                    pricelist[pos_order.pricelist_id.name] += pos_order.amount_total
                else:
                    pricelist.update(
                        {pos_order.pricelist_id.name: pos_order.amount_total}
                    )
            else:
                if "undefine" in pricelist:
                    pricelist["undefine"] += pos_order.amount_total
                else:
                    pricelist.update({"undefine": pos_order.amount_total})
        return pricelist

    def get_pricelist_qty(self, pricelist):
        if pricelist:
            qty_pricelist = 0
            pricelist_obj = self.env["product.pricelist"].search(
                [("name", "=", str(pricelist))]
            )
            if pricelist_obj:
                pos_order_ids = self.env["pos.order"].search(
                    [
                        ("session_id", "=", self.id),
                        ("pricelist_id.id", "=", pricelist_obj.id),
                    ]
                )
                qty_pricelist = len(pos_order_ids)
            else:
                if pricelist == "undefine":
                    pos_order_ids = self.env["pos.order"].search(
                        [("session_id", "=", self.id), ("pricelist_id", "=", False)]
                    )
                    qty_pricelist = len(pos_order_ids)
            return int(qty_pricelist)

    def get_payment_data(self):
        pos_order_ids = self.env["pos.order"].search([("session_id", "=", self.id)])
        bank_statement_line_ids = (
            self.env["account.bank.statement.line"]
            .search([("statement_id", "in", pos_order_ids.ids)])
            .ids
        )

        st_line_ids = (
            self.env["pos.payment"]
            .search([("pos_order_id", "in", pos_order_ids.ids)])
            .ids
        )
        if st_line_ids:
            self.env.cr.execute(
                """
                SELECT COALESCE(ppm.name->>%s, ppm.name->>'en_US') p_name, sum(amount) total
                FROM pos_payment AS pp,
                    pos_payment_method AS ppm
                WHERE  pp.payment_method_id = ppm.id
                    AND pp.id IN %s
                GROUP BY ppm.name
            """,
                (
                    self.env.lang,
                    tuple(st_line_ids),
                ),
            )
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        return payments

    def get_payment_qty(self, payment_method):
        qty_payment_method = 0
        if payment_method:
            orders = self.env["pos.order"].search([("session_id", "=", self.id)])
            st_line_obj = self.env["account.bank.statement.line"].search(
                [("statement_id", "in", orders.ids)]
            )
            if len(st_line_obj) > 0:
                res = []
                for line in st_line_obj:
                    res.append(line.journal_id.name)
                res_dict = ast.literal_eval(json.dumps(dict(Counter(res))))
                if payment_method in res_dict:
                    qty_payment_method = res_dict[payment_method]
        return int(qty_payment_method)

    # my code start

    def pos_side_get_session_amount_data(self, session_id):
        print("\n\n pos_side_get_session_amount_data called", session_id)
        pos_order_ids = self.env["pos.order"].search([("session_id", "=", session_id)])
        discount_amount = 0.0
        taxes_amount = 0.0
        total_sale_amount = 0.0
        total_gross_amount = 0.0
        sold_product = {}
        partner_data = []
        product_data = []
        customer_wise_total_amount = 0
        product_wise_total_amount = 0
        for pos_order in pos_order_ids:
            # for customer details
            if pos_order.partner_id:
                dict1 = {
                    "partner_id": pos_order.partner_id.id,
                    "partner_name": pos_order.partner_id.name,
                    "amount": pos_order.amount_total,
                }
                partner_data.append(dict1)
                customer_wise_total_amount += pos_order.amount_total
            else:
                dict1 = {
                    "partner_id": 00,
                    "partner_name": "Unknown",
                    "amount": pos_order.amount_total,
                }
                partner_data.append(dict1)
                customer_wise_total_amount += pos_order.amount_total

            currency = pos_order.session_id.currency_id
            total_gross_amount += pos_order.amount_total
            for line in pos_order.lines:
                # for product details
                product_dict = {
                    "product_id": line.product_id.id,
                    "product_name": line.full_product_name,
                    "product_qty": line.qty,
                    "product_price": line.price_unit,
                }
                product_data.append(product_dict)

                for categ in line.product_id.pos_categ_ids:
                    if categ.name:
                        if categ.name in sold_product:
                            sold_product[categ.name] += line.qty
                        else:
                            sold_product.update({categ.name: line.qty})
                    else:
                        if "undefine" in sold_product:
                            sold_product["undefine"] += line.qty
                        else:
                            sold_product.update({"undefine": line.qty})

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(
                        line.price_unit * (1 - (line.discount or 0.0) / 100.0),
                        currency,
                        line.qty,
                        product=line.product_id,
                        partner=line.order_id.partner_id or False,
                    )
                    for tax in line_taxes["taxes"]:
                        taxes_amount += tax.get("amount", 0)
                if line.discount > 0:
                    discount_amount += (
                        (line.price_unit * line.qty) * line.discount
                    ) / 100
                if line.qty > 0:
                    total_sale_amount += line.price_unit * line.qty

        # for customer details
        merged_data_customer = []
        if len(partner_data) > 0:
            partner_data.sort(key=lambda x: x["partner_id"])
            current_partner = None
            for entry in partner_data:
                if entry["partner_id"] != current_partner:
                    if current_partner is not None:
                        merged_data_customer.append(
                            {"partner_name": partner_name, "amount": total_amount}
                        )
                    current_partner = entry["partner_id"]
                    partner_name = entry["partner_name"]
                    total_amount = 0
                total_amount += entry["amount"]
            merged_data_customer.append(
                {"partner_name": partner_name, "amount": total_amount}
            )

        # for product details
        merged_data = {}
        if len(product_data) > 0:
            for entry in product_data:
                product_id = entry["product_id"]
                product_price = entry["product_price"]
                product_qty = entry["product_qty"]
                key = (product_id, product_price)
                if key in merged_data:
                    merged_data[key]["product_qty"] += product_qty
                else:
                    merged_data[key] = {
                        "product_id": product_id,
                        "product_name": entry["product_name"],
                        "product_qty": product_qty,
                        "product_price": product_price,
                    }
            merged_data_product = list(merged_data.values())
            for count_total in merged_data_product:
                qty_wise_price = (
                    count_total["product_price"] * count_total["product_qty"]
                )
                product_wise_total_amount += qty_wise_price
        else:
            merged_data_product = []

        return {
            "total_sale": total_gross_amount,
            "customer_data": merged_data_customer,
            "customer_wise_total_amount": customer_wise_total_amount,
            "product_detail_data": merged_data_product,
            "product_wise_total_amount": product_wise_total_amount,
            "discount": discount_amount,
            "tax": taxes_amount,
            "products_sold": sold_product,
            "total_gross": total_gross_amount - taxes_amount - discount_amount,
            "final_total": (total_gross_amount - discount_amount),
        }

    def pos_side_get_pricelist(self, session_id):
        pos_order_ids = self.env["pos.order"].search([("session_id", "=", session_id)])
        pricelist = {}
        pricelist1 = []
        for pos_order in pos_order_ids:
            if pos_order.pricelist_id.name:
                if pos_order.pricelist_id.name in pricelist:
                    pricelist[pos_order.pricelist_id.name] += [pos_order.amount_total]
                else:
                    pricelist.update(
                        {pos_order.pricelist_id.name: [pos_order.amount_total]}
                    )
            else:
                if "undefine" in pricelist:
                    pricelist["undefine"] += [pos_order.amount_total]
                else:
                    pricelist.update({"undefine": [pos_order.amount_total]})
        for data in pricelist:
            pricelist_dict = {
                data: [{"ord": len(pricelist[data]), "total": sum(pricelist[data])}]
            }
            pricelist1.append(pricelist_dict)
        return pricelist1

    def pos_side_get_payment_data(self, session_id):
        pos_order_ids = self.env["pos.order"].search([("session_id", "=", session_id)])
        st_line_ids = (
            self.env["pos.payment"]
            .search([("pos_order_id", "in", pos_order_ids.ids)])
            .ids
        )
        if st_line_ids:
            self.env.cr.execute(
                """
                SELECT ppm.name, sum(amount) total
                FROM pos_payment AS pp,
                    pos_payment_method AS ppm
                WHERE  pp.payment_method_id = ppm.id
                    AND pp.id IN %s
                GROUP BY ppm.name
            """,
                (tuple(st_line_ids),),
            )
            payments = self.env.cr.dictfetchall()
        else:
            payments = []
        return payments

    def send_session_receipt_email(self, email_address, session_id):
        if email_address:
            email_values = {"email_to": email_address}
            pos_session = (
                self.env["pos.session"].sudo().search([("id", "=", session_id)])
            )
            mail_template = self.env.ref(
                "bi_pos_closed_session_reports.pos_receipt_email_template",
                raise_if_not_found=False,
            )
            report = self.env["ir.actions.report"]._render_qweb_pdf(
                "bi_pos_closed_session_reports.action_report_session_z", pos_session.id
            )
            filename = "Session Receipt Report"
            attachment_data = {
                "name": "%s.pdf" % filename,
                "datas": base64.b64encode(report[0]),
                "res_model": "pos.order",
                "res_id": pos_session.id,
                "mimetype": "application/x-pdf",
                "type": "binary",
            }
            pos_attachment = self.env["ir.attachment"].sudo().create(attachment_data)
            mail_template.attachment_ids = [(6, 0, [pos_attachment.id])]
            mail_template.send_mail(
                pos_session.id, email_values=email_values, force_send=True
            )

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super(PosSession, self)._load_pos_data_fields(config_id)
        result.extend(["cash_register_balance_end_real", "cash_register_difference"])
        return result
