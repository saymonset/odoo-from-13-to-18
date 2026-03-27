from odoo import models, fields, api
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_proof = fields.Binary('Comprobante de pago', attachment=True)
    payment_proof_filename = fields.Char('Nombre del archivo')

    currency_aux = fields.Many2one(
        'res.currency',
        string='Moneda Auxiliar USD',
        compute='_compute_currency_aux',
        store=True
    )

    amount_total_usd = fields.Monetary(
        string='Total USD (BCV)',
        currency_field='currency_aux',
        compute='_compute_amount_total_usd',
        store=True
    )

    @api.depends('order_line.price_subtotal_usd_bcv')
    def _compute_amount_total_usd(self):
        for order in self:
            order.amount_total_usd = sum(line.price_subtotal_usd_bcv for line in order.order_line)

    @api.depends('currency_id')
    def _compute_currency_aux(self):
        usd = self.env.ref('base.USD', raise_if_not_found=False)
        for order in self:
            order.currency_aux = usd

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Copia automáticamente el comprobante de pago de la orden de venta a la factura"""
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)

        for order in self:
            attachments = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', order.id),
                ('description', '=', 'Comprobante de pago - Transferencia / Pago Móvil'),
            ])

            for invoice in invoices:
                for att in attachments:
                    self.env['ir.attachment'].sudo().create({
                        'name': att.name,
                        'type': att.type,
                        'datas': att.datas,
                        'mimetype': att.mimetype,
                        'res_model': 'account.move',
                        'res_id': invoice.id,
                        'description': 'Comprobante de pago - Transferencia / Pago Móvil',
                    })
                    _logger.info(f"Comprobante copiado a factura {invoice.name} desde orden {order.name}")

        return invoices

    def action_confirm(self):
        """Intentar crear el attachment si viene del website (por si no se creó antes)"""
        res = super().action_confirm()

        try:
            if request and hasattr(request, 'session') and 'payment_proof' in request.session:
                proof = request.session.pop('payment_proof')
                order = self

                self.env['ir.attachment'].sudo().create({
                    'name': proof['filename'],
                    'type': 'binary',
                    'datas': proof['data'],
                    'res_model': 'sale.order',
                    'res_id': order.id,
                    'mimetype': proof.get('mimetype'),
                    'description': 'Comprobante de pago - Transferencia / Pago Móvil',
                })
                _logger.info(f"✅ Attachment creado en action_confirm para orden {order.name}")

                order.sudo().write({
                    'payment_proof': proof['data'],
                    'payment_proof_filename': proof['filename'],
                })
        except Exception:
            pass  # Ignorar si no hay request (caso backend)

        return res