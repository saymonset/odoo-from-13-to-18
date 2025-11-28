# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class UnisaChatBotController(http.Controller):

    @http.route('/chat-bot-unisa/capturar_lead',
                auth='public',
                type='http',
                methods=['POST'],
                csrf=False,
                cors='*')
    def capturar_lead_odoo(self, **kw):
        try:
            raw_data = request.httprequest.data
            if not raw_data:
                return self._error_response("No se recibió información")

            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                return self._error_response("JSON inválido")

            _logger.info("LEAD RECIBIDO: %s", json.dumps(data, indent=2, ensure_ascii=False))

            # === USUARIO ADMIN ===
            admin_uid = request.env.ref('base.user_admin').id or 2
            env_admin = request.env(user=admin_uid)

            # === MEDIO Y FUENTE (solo nombre, sin 'active') ===
            medium = env_admin['utm.medium'].search([('name', '=ilike', 'WhatsApp')], limit=1)
            if not medium:
                try:
                    medium = env_admin['utm.medium'].create({'name': 'WhatsApp'})
                except:
                    medium = False

            source = env_admin['utm.source'].search([('name', '=ilike', 'WhatsApp Bot UNISA')], limit=1)
            if not source:
                try:
                    source = env_admin['utm.source'].create({'name': 'WhatsApp Bot UNISA'})
                except:
                    source = False

            # === TODA LA INFO EN LA DESCRIPCIÓN (NUNCA falla) ===
            description = (
                "Cita desde WhatsApp Bot\n\n"
                f"• Paciente: {data.get('nombre_completo', 'N/A')}\n"
                f"• Cédula: {data.get('cedula', 'N/A')}\n"
                f"• Fecha de nacimiento: {data.get('fecha_nacimiento', 'N/A')}\n"
                f"• Teléfono: {data.get('telefono_whatsapp', 'N/A')}\n"
                f"• Servicio: {data.get('servicio_solicitado', 'N/A')}\n"
                f"• Fecha preferida: {data.get('fecha_preferida', 'lo antes posible')}\n"
                f"• Horario: {data.get('hora_preferida', 'cualquier hora')}\n"
                f"• Medio de pago: {data.get('medio_pago', 'N/A')}\n"
                f"• ¿Paciente nuevo?: {'Sí' if str(data.get('es_paciente_nuevo','')).lower() in ['sí','si','yes','s'] else 'No'}\n"
                f"• ¿Interés Tarjeta Salud?: {'Sí' if str(data.get('interes_tarjeta_salud','')).lower() in ['sí','si','yes','s'] else 'No'}"
            )

            # === DATOS DEL LEAD (solo campos que EXISTEN siempre) ===
            lead_data = {
                'name': f"Cita WhatsApp - {data.get('servicio_solicitado','Consulta')} - {data.get('nombre_completo','Sin nombre')}",
                'partner_name': data.get('nombre_completo', 'Sin nombre'),
                'phone': data.get('telefono_whatsapp'),
                'mobile': (data.get('telefono_whatsapp') or '').replace('+58', '0'),
                'description': description,
                'medium_id': medium.id if medium else False,
                'source_id': source.id if source else False,
            }

            # === CREAR EL LEAD (100% seguro) ===
            lead = env_admin['crm.lead'].create(lead_data)
            _logger.info(f"LEAD CREADO → ID: {lead.id} | {lead.name}")

            # === MENSAJE AL CLIENTE ===
            respuesta = (
                "¡Tu cita ha sido registrada exitosamente!\n\n"
                f"• Paciente: {data.get('nombre_completo', 'N/A')}\n"
                f"• Servicio: {data.get('servicio_solicitado', 'N/A')}\n"
                f"• Preferencia: {data.get('fecha_preferida', 'lo antes posible')} por la {data.get('hora_preferida', 'cualquier hora')}\n\n"
                "En breve un ejecutivo de UNISA te contactará.\n"
                "¡Gracias por confiar en nosotros!"
            )

            return request.make_response(
                json.dumps({
                    'success': True,
                    'lead_id': lead.id,
                    'respuesta_bot': respuesta
                }, ensure_ascii=False),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error("ERROR CREANDO LEAD", exc_info=True)
            return self._error_response("Error interno")

    def _error_response(self, message):
        return request.make_response(
            json.dumps({'success': False, 'error': message}, ensure_ascii=False),
            headers=[('Content-Type', 'application/json')],
            status=400
        )