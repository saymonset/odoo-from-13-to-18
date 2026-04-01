from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang

import logging

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _round_base_lines_tax_details(self, base_lines, company_id, tax_lines=None):
        """
        Sobrescritura para asegurar que las monedas sean singletons antes de redondear.
        Odoo 19: ahora acepta el parámetro tax_lines.
        """
        for line in base_lines:
            currency = line.get('currency_id')
            if currency:
                if len(currency) > 1:
                    line['currency_id'] = currency[0]
                elif not currency:
                    line['currency_id'] = company_id.currency_id
        
        # También validar tax_lines si se proporcionan
        if tax_lines:
            for line in tax_lines:
                currency = line.get('currency_id')
                if currency:
                    if len(currency) > 1:
                        line['currency_id'] = currency[0]
                    elif not currency:
                        line['currency_id'] = company_id.currency_id
        
        # Llamar al método padre con los parámetros correctos
        if tax_lines is not None:
            return super()._round_base_lines_tax_details(base_lines, company_id, tax_lines=tax_lines)
        else:
            return super()._round_base_lines_tax_details(base_lines, company_id)

    @api.model
    def _get_tax_totals_summary(
        self, base_lines, currency, company, cash_rounding=None
    ):
        
        # Validar que currency sea singleton
        if currency and len(currency) > 1:
            currency = currency[0]
        elif not currency:
            currency = company.currency_id
        
        ## Base currency
        res = super()._get_tax_totals_summary(
            base_lines, currency, company, cash_rounding
        )

        # Obtener VES currency de forma segura
        try:
            ves_currency = self.env.ref('base.VEF', raise_if_not_found=False)
            if not ves_currency:
                ves_currency = self.env.ref('base.VES', raise_if_not_found=False)
            if not ves_currency:
                ves_currency = self.env.company.currency_id
                _logger.warning("No se encontró moneda VEF/VES, usando moneda de la compañía")
        except Exception as e:
            ves_currency = self.env.company.currency_id
            _logger.warning("Error obteniendo moneda VEF/VES: %s", e)
        
        if ves_currency and len(ves_currency) > 1:
            ves_currency = ves_currency[0]
        
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        
        record = False
        if active_model and active_id:
            if isinstance(active_id, api.NewId):
                active_id = active_id.origin
            if active_id:
                record = self.env[active_model].browse(active_id)

        if not record and base_lines:
            try:
                first_line = base_lines[0].get('record')
                if first_line and isinstance(first_line, models.Model):
                    if hasattr(first_line, 'move_id'):
                        record = first_line.move_id
                    elif hasattr(first_line, 'order_id'):
                        record = first_line.order_id
                    else:
                        record = first_line
            except Exception as e:
                _logger.warning("Error deduciendo el record al generar summary tax base %s", e)

        if not record:
            return res
        
        # Obtener monedas de forma segura
        currency_id = self.env.company.currency_id
        foreign_currency_id = self.env.company.foreign_currency_id if hasattr(self.env.company, 'foreign_currency_id') else None
        
        if not foreign_currency_id:
            foreign_currency_id = currency_id
        
        company_rate = 1.0
        has_discount = False
        
        if active_model == "account.move" and record.move_type in ("out_invoice", "in_invoice", "out_refund", "in_refund"):
            company_rate = record.company_currency_rate if hasattr(record, 'company_currency_rate') else 1.0
            currency_id = record.currency_id
            foreign_currency_id = record.foreign_currency_id if hasattr(record, 'foreign_currency_id') else currency_id
            has_discount = any(
                line.discount > 0
                for line in record.invoice_line_ids
            )
        else: 
            if hasattr(record, 'company_id'): 
                currency_id = record.company_id.currency_id
            else:
                currency_id = self.env.company.currency_id
            foreign_currency_id = self.env.company.foreign_currency_id if hasattr(self.env.company, 'foreign_currency_id') else currency_id
        
        # Asegurar que todas las monedas son singletons
        if currency_id and len(currency_id) > 1:
            currency_id = currency_id[0]
        if foreign_currency_id and len(foreign_currency_id) > 1:
            foreign_currency_id = foreign_currency_id[0]
        
        res_without_discount = res.copy()
        
        formatted_total_discount = 0.0
        formatted_total_discount_ves = 0.0
        if has_discount:
            exchange_rate = company_rate
            total_discount_amount = sum([
                (line.get("price_unit", 0.0) * line.get("quantity", 0.0) * line.get("discount", 0.0) / 100)
                for line in base_lines
            ])
            total_discount_amount_ves = total_discount_amount * exchange_rate
            
            from odoo.tools.float_utils import float_round
            formatted_total_discount = float_round(total_discount_amount, precision_digits=2)
            formatted_total_discount_ves = float_round(total_discount_amount_ves, precision_digits=2)
        
        foreign_lines = []
        
        if record._name == 'account.move':
            foreign_lines, _foreign_tax_lines = record._get_rounded_foreign_base_and_tax_lines()
        elif record._name in ('sale.order','purchase.order'):
            company_id = (self.company_id or self.env.company)
            foreign_lines = [line._prepare_foreign_base_line_for_taxes_computation() for line in record.order_line]
            
            self._add_tax_details_in_base_lines(foreign_lines, company_id)
            # Llamar a nuestro método sobrescrito en lugar del original
            self._round_base_lines_tax_details(foreign_lines, company_id)
        
        # Asegurar que foreign_currency_id sea singleton
        if foreign_currency_id and len(foreign_currency_id) > 1:
            foreign_currency_id = foreign_currency_id[0]
        
        foreign_res = super()._get_tax_totals_summary(
            foreign_lines,
            foreign_currency_id,
            company,
            cash_rounding
        )
        
        def safe_format(value, currency_obj):
            if not currency_obj:
                return value
            try:
                if len(currency_obj) > 1:
                    currency_obj = currency_obj[0]
                return formatLang(
                    env=self.env,
                    value=value,
                    currency_obj=currency_obj
                )
            except Exception:
                return value
        
        # amounts in foreign currency
        res['foreign_currency_id'] = foreign_res.get('currency_id', False)
        if res['foreign_currency_id'] and len(res['foreign_currency_id']) > 1:
            res['foreign_currency_id'] = res['foreign_currency_id'][0].id if hasattr(res['foreign_currency_id'][0], 'id') else False
        
        res['ves_currency_id'] = ves_currency.id if ves_currency else False
        res['base_amount_foreign_currency'] = foreign_res.get('base_amount_currency', 0.0)
        res['tax_amount_foreign_currency'] = foreign_res.get('tax_amount_currency', 0.0)
        res['total_amount_foreign_currency'] = foreign_res.get('total_amount_currency', 0.0)
        res['formatted_total_discount'] = formatted_total_discount
        res['formatted_total_discount_ves'] = formatted_total_discount_ves
        
        # Moneda Base
        res['formatted_base_amount_currency'] = safe_format(
            res.get('base_amount_currency', 0.0),
            currency_id
        )
        res['formatted_tax_amount_currency'] = safe_format(
            res.get('tax_amount_currency', 0.0),
            currency_id
        )
        res['formatted_total_amount_currency'] = safe_format(
            res.get('total_amount_currency', 0.0),
            currency_id
        )
        
        # only VES amounts
        res['formatted_base_amount_currency_ves'] = safe_format(
            res.get('base_amount', 0.0),
            ves_currency
        )
        res['formatted_tax_amount_currency_ves'] = safe_format(
            res.get('tax_amount', 0.0),
            ves_currency
        )
        res['formatted_total_amount_currency_ves'] = safe_format(
            res.get('total_amount', 0.0),
            ves_currency
        )
        
        # Foraneos
        res['formatted_base_amount_foreign_currency'] = safe_format(
            res.get('base_amount_foreign_currency', 0.0),
            foreign_currency_id
        )
        res['formatted_tax_amount_foreign_currency'] = safe_format(
            res.get('tax_amount_foreign_currency', 0.0),
            foreign_currency_id
        )
        res['formatted_total_amount_foreign_currency'] = safe_format(
            res.get('total_amount_foreign_currency', 0.0),
            foreign_currency_id
        )
        
        # Procesar subtotales y grupos de impuestos
        for res_subtotal, foreign_subtotal in zip(res.get("subtotals", []), foreign_res.get("subtotals", [])):
            res_subtotal["tax_amount_foreign_currency"] = foreign_subtotal.get("tax_amount_currency", 0.0)
            res_subtotal["base_amount_foreign_currency"] = foreign_subtotal.get("base_amount_currency", 0.0)
            res_subtotal["total_amount_foreign_currency"] = foreign_subtotal.get("total_amount_currency", 0.0)
            
            res_subtotal['formatted_base_amount_foreign_currency'] = safe_format(
                res_subtotal.get('base_amount_foreign_currency', 0.0),
                foreign_currency_id
            )
            res_subtotal['formatted_tax_amount_foreign_currency'] = safe_format(
                res_subtotal.get('tax_amount_foreign_currency', 0.0),
                foreign_currency_id
            )
            res_subtotal['formatted_total_amount_foreign_currency'] = safe_format(
                res_subtotal.get('total_amount_foreign_currency', 0.0),
                foreign_currency_id
            )
            res_subtotal['formatted_base_amount_currency_ves'] = safe_format(
                res_subtotal.get('base_amount', 0.0),
                ves_currency
            )
            res_subtotal['formatted_tax_amount_currency_ves'] = safe_format(
                res_subtotal.get('tax_amount', 0.0),
                ves_currency
            )
            res_subtotal['formatted_total_amount_currency_ves'] = safe_format(
                res_subtotal.get('total_amount', 0.0),
                ves_currency
            )
            res_subtotal['formatted_base_amount_currency'] = safe_format(
                res_subtotal.get('base_amount_currency', 0.0),
                currency_id
            )
            res_subtotal['formatted_tax_amount_currency'] = safe_format(
                res_subtotal.get('tax_amount_currency', 0.0),
                currency_id
            )
            res_subtotal['formatted_total_amount_currency'] = safe_format(
                res_subtotal.get('total_amount_currency', 0.0),
                currency_id
            )
            
            for res_tax_group, foreign_tax_group in zip(res_subtotal.get("tax_groups", []), foreign_subtotal.get("tax_groups", [])):
                res_tax_group["tax_amount_foreign_currency"] = foreign_tax_group.get("tax_amount_currency", 0.0)
                res_tax_group["base_amount_foreign_currency"] = foreign_tax_group.get("base_amount_currency", 0.0)
                res_tax_group["display_base_amount_foreign_currency"] = foreign_tax_group.get("display_base_amount_currency", 0.0)
                
                res_tax_group['formatted_base_amount_currency'] = safe_format(
                    res_tax_group.get('base_amount_currency', 0.0),
                    currency_id
                )
                res_tax_group['formatted_tax_amount_currency'] = safe_format(
                    res_tax_group.get('tax_amount_currency', 0.0),
                    currency_id
                )
                res_tax_group['formatted_display_base_amount_currency'] = safe_format(
                    res_tax_group.get('display_base_amount_currency', 0.0),
                    currency_id
                )
                res_tax_group['formatted_base_amount_currency_ves'] = safe_format(
                    res_tax_group.get('base_amount', 0.0),
                    ves_currency
                )
                res_tax_group['formatted_tax_amount_currency_ves'] = safe_format(
                    res_tax_group.get('tax_amount', 0.0),
                    ves_currency
                )
                res_tax_group['formatted_total_amount_currency_ves'] = safe_format(
                    res_tax_group.get('total_amount', 0.0),
                    ves_currency
                )
                res_tax_group['formatted_base_amount_foreign_currency'] = safe_format(
                    res_tax_group.get('base_amount_foreign_currency', 0.0),
                    foreign_currency_id
                )
                res_tax_group['formatted_tax_amount_foreign_currency'] = safe_format(
                    res_tax_group.get('tax_amount_foreign_currency', 0.0),
                    foreign_currency_id
                )
                res_tax_group['formatted_display_base_amount_foreign_currency'] = safe_format(
                    res_tax_group.get('display_base_amount_foreign_currency', 0.0),
                    foreign_currency_id
                )
        
        return res
    
    @api.model
    def _prepare_foreign_base_line_for_taxes_computation(self, record, **kwargs):
        """ Convert any representation of a business object into a base line
        with validated currency.
        """
        def load(field, fallback, from_base_line=False):
            return self._get_base_line_field_value_from_record(record, field, kwargs, fallback, from_base_line=from_base_line)

        currency = (
            load('foreign_currency_id', None)
            or self.env.company.foreign_currency_id
            or self.env.company.currency_id
        )
        
        # Asegurar que currency sea singleton
        if currency and len(currency) > 1:
            currency = currency[0]
        
        base_line = {
            **kwargs,
            'record': record,
            'id': load('id', 0),

            # Basic fields:
            'product_id': load('product_id', self.env['product.product']),
            'product_uom_id': load('product_uom_id', self.env['uom.uom']),
            'tax_ids': load('tax_ids', self.env['account.tax']),
            'price_unit': load('price_unit', 0.0),
            'quantity': load('quantity', 0.0),
            'discount': load('discount', 0.0),
            'currency_id': currency,
            'deferred_start_date': self._get_base_line_field_value_from_record(record, 'deferred_start_date', kwargs, False),
            'deferred_end_date': self._get_base_line_field_value_from_record(record, 'deferred_end_date', kwargs, False),

            # The special_mode for the taxes computation:
            'special_mode': load('special_mode', False, from_base_line=True),

            # A special typing of base line for some custom behavior:
            'special_type': load('special_type', False, from_base_line=True),

            # All computation are managing the foreign currency and the local one.
            'rate': load('rate', 1.0),

            # For all computation that are inferring a base amount in order to reach a total you know in advance, you have to force some
            # base/tax amounts for the computation (E.g. down payment, combo products, global discounts etc).
            'manual_tax_amounts': load('manual_tax_amounts', None, from_base_line=True),
            'manual_total_excluded_currency': load('manual_total_excluded_currency', None, from_base_line=True),
            # Add a function allowing to filter out some taxes during the evaluation. Those taxes can't be removed from the base_line
            'filter_tax_function': load('filter_tax_function', None, from_base_line=True),
            'manual_total_excluded': load('manual_total_excluded', None, from_base_line=True),
            # ===== Accounting stuff =====
            'sign': load('sign', 1.0),
            'is_refund': load('is_refund', False),
            'tax_tag_invert': load('tax_tag_invert', False),
            'partner_id': load('partner_id', self.env['res.partner']),
            'account_id': load('account_id', self.env['account.account']),
            'analytic_distribution': load('analytic_distribution', None),
        }

        extra_tax_data = self._import_base_line_extra_tax_data(base_line, load('extra_tax_data', {}) or {})
        base_line.update({
            'computation_key': load('computation_key', extra_tax_data.get('computation_key'), from_base_line=True),
            'manual_tax_amounts': load('manual_tax_amounts', extra_tax_data.get('manual_tax_amounts'), from_base_line=True),
        })
        if 'price_unit' in extra_tax_data:
            base_line['price_unit'] = extra_tax_data['price_unit']

        if record and isinstance(record, dict):
            for k, v in record.items():
                if k.startswith('_') and k not in base_line:
                    base_line[k] = v

        manual_fields = (
            'manual_total_excluded',
            'manual_total_excluded_currency',
            'manual_total_included',
            'manual_total_included_currency',
        )
        for field in manual_fields:
            base_line.setdefault(field, None)
        return base_line