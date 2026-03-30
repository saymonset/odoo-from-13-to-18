from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import base64
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleAttachment(WebsiteSale):

    # -------------------------------------------------------------------------
    # Endpoint JSON: obtener total de orden + tasa BCV + equivalente USD
    # -------------------------------------------------------------------------
    @http.route('/payment_proof/get_order_total_and_rate', type='json', auth='public', csrf=False)
    def get_order_total_and_rate(self):
        """Devuelve el total de la orden actual en VES, la tasa BCV y el equivalente en USD"""
        _logger.info("=== get_order_total_and_rate called ===")
        try:
            # Obtener la orden desde la sesión
            sale_order_id = request.session.get('sale_order_id') or request.session.get('sale_last_order_id')
            if not sale_order_id:
                _logger.warning("No hay sale_order_id en sesión")
                return {'error': 'No hay orden activa'}

            order = request.env['sale.order'].sudo().browse(int(sale_order_id)).exists()
            if not order:
                _logger.warning(f"No se encontró la orden con ID {sale_order_id}")
                return {'error': 'No se encontró la orden'}

            amount_vef = order.amount_total
            _logger.info(f"Monto en VES: {amount_vef}")

            # Consultar directamente la tasa BCV
            Rate = request.env['res.currency.rate']
            rate_record = Rate.sudo().search([
                ('currency_id.name', '=', 'VES'),
                ('is_bcv_rate', '=', True),
                ('company_id', '=', request.env.company.id),
            ], order='name desc', limit=1)

            if rate_record and rate_record.bcv_rate_value and rate_record.bcv_rate_value > 0:
                exchange_rate = rate_record.bcv_rate_value
                # Formatear fecha
                fecha = rate_record.name
                fecha_formateada = fecha.strftime('%d/%m/%Y') if fecha else ''
                amount_usd = amount_vef / exchange_rate
                _logger.info(f"Tasa encontrada: {exchange_rate}, USD: {amount_usd}")
                return {
                    'amount_vef': amount_vef,
                    'exchange_rate': exchange_rate,
                    'rate_date': fecha_formateada,
                    'amount_usd': amount_usd,
                }
            else:
                _logger.warning("No se encontró tasa BCV válida (is_bcv_rate=True y bcv_rate_value>0)")
                return {
                    'amount_vef': amount_vef,
                    'exchange_rate': 0.0,
                    'rate_date': '',
                    'amount_usd': 0.0,
                    'error': 'Tasa BCV no disponible temporalmente'
                }
        except Exception as e:
            _logger.error(f"Error en get_order_total_and_rate: {str(e)}", exc_info=True)
            return {'error': f'Error interno: {str(e)}'}
        
    # -------------------------------------------------------------------------
    # Ruta para subir comprobante (POST)
    # -------------------------------------------------------------------------
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

        # Extraer campos adicionales del formulario (vienen en request.params)
        payment_data = {
            'payment_date': post.get('payment_date'),
            'payment_method': post.get('payment_method'),
            'bank_origin': post.get('bank_origin'),
            'bank_destination': post.get('bank_destination', 'N/A'),
            'reference': post.get('reference'),
            'amount_vef': float(post.get('amount_vef', 0)),
            'exchange_rate': float(post.get('exchange_rate', 0)),
            'amount_usd': float(post.get('amount_usd', 0)),
        }
        _logger.info(f"📝 Datos de pago recibidos: {payment_data}")

        # Guardar en sesión (para ser recuperados en confirmación)
        request.session['payment_data'] = payment_data

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

    # -------------------------------------------------------------------------
    # Endpoint JSON: ID del proveedor de transferencia bancaria
    # -------------------------------------------------------------------------
    @http.route('/payment_proof/get_transfer_provider_id', type='json', auth='public', csrf=False)
    def get_transfer_provider_id(self):
        """Devuelve el ID del proveedor de pago marcado como transferencia bancaria"""
        provider = request.env['payment.provider'].sudo().search([('is_wire_transfer', '=', True)], limit=1)
        _logger.info(f"Transfer provider ID: {provider.id if provider else 0}")
        return provider.id if provider else 0

    # -------------------------------------------------------------------------
    # Endpoint JSON: lista de bancos venezolanos
    # -------------------------------------------------------------------------
    @http.route('/payment_proof/get_bank_list', type='json', auth='public', csrf=False)
    def get_bank_list(self):
        """Lista de bancos venezolanos. Puede ampliarse consultando una API externa."""
        banks = [
            {'id': 'banco_de_venezuela', 'name': 'Banco de Venezuela'},
            {'id': 'banesco', 'name': 'Banesco Banco Universal'},
            {'id': 'mercantil', 'name': 'Banco Mercantil'},
            {'id': 'provincial', 'name': 'Banco Provincial'},
            {'id': 'bnc', 'name': 'Banco Nacional de Crédito (BNC)'},
            {'id': 'bancamiga', 'name': 'Bancamiga'},
            {'id': 'del_tesoro', 'name': 'Banco del Tesoro'},
            {'id': 'exterior', 'name': 'Banco Exterior'},
            {'id': 'caribe', 'name': 'Banco Caribe'},
            {'id': 'sofitasa', 'name': 'Sofitasa'},
            {'id': 'bicentenario', 'name': 'Banco Bicentenario'},
            {'id': 'plaza', 'name': 'Banco Plaza'},
            {'id': 'activo', 'name': 'Banco Activo'},
        ]
        _logger.info(f"Devolviendo {len(banks)} bancos")
        return banks

    # -------------------------------------------------------------------------
    # Hook _process_payment (mantenido original)
    # -------------------------------------------------------------------------
    def _process_payment(self, **kwargs):
        """Procesa el pago y recupera los datos de sesión si aún no se han guardado"""
        _logger.info("🔄 Entrando en _process_payment (Payment Custom)")
        sale_order_id = request.session.get('sale_order_id') or request.session.get('sale_last_order_id')
        order = None
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(int(sale_order_id)).exists()

        # Si existe el comprobante en sesión y no se ha guardado aún, lo creamos
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

        # También recuperar datos de pago adicionales si existen
        if order and 'payment_data' in request.session:
            payment_data = request.session.pop('payment_data')
            try:
                order.sudo().write({
                    'payment_date': payment_data.get('payment_date'),
                    'payment_method': payment_data.get('payment_method'),
                    'bank_origin': payment_data.get('bank_origin'),
                    'bank_destination': payment_data.get('bank_destination', 'N/A'),
                    'reference': payment_data.get('reference'),
                    'amount_vef': payment_data.get('amount_vef', 0),
                    'exchange_rate': payment_data.get('exchange_rate', 0),
                    'amount_usd': payment_data.get('amount_usd', 0),
                })
                _logger.info(f"✅ Datos de pago adicionales guardados en orden {order.name}")
            except Exception as e:
                _logger.error(f"Error guardando datos de pago adicionales: {e}", exc_info=True)

        return super()._process_payment(**kwargs)