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
        """
        Devuelve la lista de bancos venezolanos desde la tabla res.bank,
        ordenados alfabéticamente por nombre.
        """
        try:
            # Buscar bancos activos en Venezuela (o todos si no filtras por país)
            banks = request.env['res.bank'].sudo().search([
                ('active', '=', True),
                # ('country', '=', request.env.ref('base.ve').id)  # Opcional: filtrar solo Venezuela
            ], order='name ASC')  # Orden alfabético por nombre
            
            # Construir la respuesta con el formato que espera tu frontend
            bank_list = []
            for bank in banks:
                bank_list.append({
                    'id': bank.bic,           # Usamos el código BIC (0102, 0134, etc.)
                    'name': bank.name,        # Nombre del banco
                    'bic': bank.bic,          # Incluimos también el BIC por si lo necesitas
                })
            
            _logger.info(f"Devolviendo {len(bank_list)} bancos desde res.bank")
            return bank_list
            
        except Exception as e:
            _logger.error(f"Error al obtener lista de bancos: {str(e)}")
            # Fallback: lista estática por si hay error
            return [
                {'id': '0102', 'name': 'Banco de Venezuela', 'bic': '0102'},
                {'id': '0134', 'name': 'Banesco Banco Universal', 'bic': '0134'},
                {'id': '0105', 'name': 'Banco Mercantil', 'bic': '0105'},
            ]

    # -------------------------------------------------------------------------
    # Endpoint JSON: lista de bancos desde diarios contables (para banco destino)
    # -------------------------------------------------------------------------
    @http.route('/payment_proof/get_bank_journal_list', type='json', auth='public', csrf=False)
    def get_bank_journal_list(self):
        """
        Devuelve la lista de bancos (diarios) activos donde la empresa recibe pagos.
        """
        try:
            # Buscar diarios de tipo 'bank' que están activos
            bank_journals = request.env['account.journal'].sudo().search([
                ('type', '=', 'bank'),
                ('active', '=', True),
            ], order='name ASC')

            bank_list = []
            for journal in bank_journals:
                # Obtenemos el nombre del banco asociado al diario (si existe)
                bank_name = journal.bank_id.name if journal.bank_id else journal.name
                
                # Usamos el código del banco (bic) si existe, sino el ID del diario
                bank_code = journal.bank_id.bic if journal.bank_id and journal.bank_id.bic else str(journal.id)
                
                bank_list.append({
                    'id': journal.id,
                    'name': bank_name,
                    'journal_id': journal.id,
                    'bic': journal.bank_id.bic if journal.bank_id else '',
                })
            
            _logger.info(f"Devolviendo {len(bank_list)} bancos desde los diarios contables")
            return bank_list
            
        except Exception as e:
            _logger.error(f"Error al obtener lista de bancos: {str(e)}")
            return []

    # -------------------------------------------------------------------------
    # Endpoint JSON: obtener datos del banco destino (para instrucciones de pago)
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Endpoint JSON: obtener datos del banco destino (para instrucciones de pago)
    # -------------------------------------------------------------------------
    @http.route('/payment_proof/get_bank_details', type='json', auth='public', csrf=False)
    def get_bank_details(self, journal_id):
        """
        Devuelve los detalles del banco destino para mostrar en instrucciones de pago.
        """
        try:
            if not journal_id:
                return {'error': 'No se especificó banco destino'}
            
            # Convertir a entero
            try:
                journal_id = int(journal_id)
            except (ValueError, TypeError):
                return {'error': f'ID de banco inválido: {journal_id}'}
            
            # Buscar el diario contable
            journal = request.env['account.journal'].sudo().browse(journal_id).exists()
            if not journal:
                return {'error': f'Banco destino no encontrado con ID: {journal_id}'}
            
            # Obtener los datos bancarios
            bank_details = {
                'bank_name': journal.bank_id.name if journal.bank_id else journal.name,
                'account_number': journal.bank_acc_number or 'No especificado',
                'account_holder': journal.bank_id and journal.bank_id.name or request.env.company.name,
                'phone': journal.bank_id and journal.bank_id.phone or '',
                'email': journal.bank_id and journal.bank_id.email or '',
                'routing_number': journal.bank_id and journal.bank_id.bic or '',
                'instructions': 'Transferencia bancaria - Por favor use su número de orden como referencia',
            }
            
            # También obtener datos desde la compañía
            company = request.env.company
            bank_details['company_name'] = company.name
            bank_details['company_rif'] = company.vat or ''
            
            _logger.info(f"Detalles del banco destino para journal {journal_id}: {bank_details}")
            return bank_details
            
        except Exception as e:
            _logger.error(f"Error al obtener detalles del banco: {str(e)}", exc_info=True)
            return {'error': str(e)}
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