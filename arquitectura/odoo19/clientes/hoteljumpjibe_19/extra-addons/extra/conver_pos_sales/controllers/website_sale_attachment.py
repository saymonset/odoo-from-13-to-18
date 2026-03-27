from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import base64
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleAttachment(WebsiteSale):

    @http.route(['/shop/upload_payment_proof'], type='http', methods=['POST'], auth='public', website=True, csrf=False)
    def upload_payment_proof(self, **post):
        file = request.httprequest.files.get('payment_proof_file')
        if not file or not file.filename:
            return request.make_response('ERROR', status=400)

        # Obtener la orden de venta actual desde la sesión
        sale_order_id = request.session.get('sale_order_id') or request.session.get('sale_last_order_id')
        order = None
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(int(sale_order_id)).exists()

        # Leer el archivo una sola vez
        file_data = file.read()
        file_base64 = base64.b64encode(file_data).decode('utf-8')
        filename = file.filename
        mimetype = getattr(file, 'content_type', 'application/octet-stream')

        if order:
            try:
                # Crear el attachment con la descripción específica (para copia a factura)
                request.env['ir.attachment'].sudo().create({
                    'name': filename,
                    'type': 'binary',
                    'datas': file_base64,
                    'res_model': 'sale.order',
                    'res_id': order.id,
                    'mimetype': mimetype,
                    'description': 'Comprobante de pago - Transferencia / Pago Móvil',
                })
                # Actualizar los campos binarios de la orden (para visualización)
                order.sudo().write({
                    'payment_proof': file_base64,
                    'payment_proof_filename': filename,
                })
                _logger.info(f"✅ Comprobante guardado en orden {order.name}")
                return request.make_response('OK')
            except Exception as e:
                _logger.error(f"Error guardando comprobante: {e}", exc_info=True)
                return request.make_response('ERROR', status=500)

        # Si no hay orden, guardar en sesión (fallback)
        request.session['payment_proof'] = {
            'data': file_base64,
            'filename': filename,
            'mimetype': mimetype,
        }
        _logger.info(f"📤 Comprobante guardado en sesión: {filename}")
        return request.make_response('OK')

    # Hook para métodos de pago personalizados (no usado por transferencia estándar)
    def _process_payment(self, **kwargs):
        _logger.info("🔄 Entrando en _process_payment (Payment Custom)")
        sale_order_id = request.session.get('sale_order_id') or request.session.get('sale_last_order_id')
        order = None
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(int(sale_order_id)).exists()

        if order and 'payment_proof' in request.session:
            proof = request.session.pop('payment_proof')
            try:
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': proof['filename'],
                    'type': 'binary',
                    'datas': proof['data'],
                    'res_model': 'sale.order',
                    'res_id': order.id,
                    'mimetype': proof.get('mimetype'),
                    'description': 'Comprobante de pago - Transferencia / Pago Móvil',
                })
                _logger.info(f"✅ Attachment creado en Sale Order {order.name}! Archivo: {proof['filename']}")
                order.sudo().write({
                    'payment_proof': proof['data'],
                    'payment_proof_filename': proof['filename'],
                })
            except Exception as e:
                _logger.error(f"Error creando attachment: {e}", exc_info=True)
        return super()._process_payment(**kwargs)