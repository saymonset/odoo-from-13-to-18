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
            
             # === BUSCAR EQUIPO DE VENTAS UNISA ===
            team_unisa = env_admin['crm.team'].search([('name', '=ilike', 'Equipo de Venta Unisa')], limit=1)
            if not team_unisa:
                # Si no existe el equipo, buscar cualquier equipo activo
                team_unisa = env_admin['crm.team'].search([('active', '=', True)], limit=1)
                _logger.warning("Equipo 'Equipo de Venta Unisa' no encontrado. Usando equipo: %s", team_unisa.name if team_unisa else "Ninguno")
            else:
                _logger.info("Equipo UNISA encontrado: %s (ID: %s)", team_unisa.name, team_unisa.id)

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
                    
            # === CAMPAÑA ESPECÍFICA PARA IDENTIFICAR LEADS DEL BOT ===
            campaign = env_admin['utm.campaign'].search([('name', '=ilike', 'WhatsApp Bot UNISA')], limit=1)
            if not campaign:
                try:
                    campaign = env_admin['utm.campaign'].create({'name': 'WhatsApp Bot UNISA'})
                except:
                    campaign = False

            # === ETIQUETA/IDENTIFICADOR PARA LEADS DEL BOT ===
            # Buscar o crear etiqueta específica para estos leads
            tag_bot = env_admin['crm.tag'].search([
                ('name', '=ilike', 'WhatsApp Bot')
            ], limit=1)
            if not tag_bot:
                try:
                    tag_bot = env_admin['crm.tag'].create({
                        'name': 'WhatsApp Bot',
                        'color': 10  # Color azul
                    })
                except:
                    tag_bot = False


            # === TODA LA INFO EN LA DESCRIPCIÓN (NUNCA falla) ===
            description = (
                "Cita desde WhatsApp Bot UNISA\n\n"
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
                'campaign_id': campaign.id if campaign else False,
                'team_id': team_unisa.id if team_unisa else False,  # ASIGNACIÓN AL EQUIPO UNISA
                'tag_ids': [(4, tag_bot.id)] if tag_bot else False,  # ETIQUETA IDENTIFICADORA
            }

            # === CREAR EL LEAD (100% seguro) ===
            lead = env_admin['crm.lead'].create(lead_data)
            _logger.info(f"LEAD CREADO → ID: {lead.id} | {lead.name} | Equipo: {team_unisa.name if team_unisa else 'Sin equipo'}")
            
            # === ASIGNACIÓN ROUND ROBIN SI EL EQUIPO TIENE USUARIOS ===
            if team_unisa and team_unisa.member_ids:
                try:
                    # Obtener el último usuario asignado para hacer round robin
                    last_assigned_user = env_admin['ir.config_parameter'].sudo().get_param(
                        f'unisa_bot_last_user_{team_unisa.id}', 
                        default=False
                    )
                    
                    team_members = team_unisa.member_ids.sorted('id')
                    if last_assigned_user:
                        last_user = env_admin['res.users'].browse(int(last_assigned_user))
                        if last_user in team_members:
                            current_index = team_members.ids.index(last_user.id)
                            next_index = (current_index + 1) % len(team_members)
                            next_user = team_members[next_index]
                        else:
                            next_user = team_members[0]
                    else:
                        next_user = team_members[0]
                    
                    # Asignar el lead al siguiente usuario
                    lead.write({'user_id': next_user.id})
                    
                    # Guardar el último usuario asignado para la próxima vez
                    env_admin['ir.config_parameter'].sudo().set_param(
                        f'unisa_bot_last_user_{team_unisa.id}', 
                        next_user.id
                    )
                    
                    _logger.info(f"Lead asignado a usuario: {next_user.name}")
                    
                except Exception as e:
                    _logger.warning("Error en asignación round robin: %s", str(e))


            # === MENSAJE AL CLIENTE ===
            respuesta = (
                "¡Tu solicitud ha sido registrada exitosamente!\n\n"
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
                    'team_assigned': team_unisa.name if team_unisa else "No asignado",
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