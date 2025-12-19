# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)

class UnisaChatBotController(http.Controller):
    
    def _create_attachment(self, env, url, name, res_model, res_id):
        """Crear adjunto a partir de URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                attachment = env['ir.attachment'].create({
                    'name': name,
                    'type': 'binary',
                    'datas': response.content.encode('base64'),
                    'res_model': res_model,
                    'res_id': res_id,
                    'mimetype': response.headers.get('Content-Type', 'image/jpeg')
                })
                return attachment
        except Exception as e:
            _logger.error(f"Error creando adjunto {name}: {str(e)}")
        return None

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
            
            # === BUSCAR O CREAR CONTACTO ===
            partner = self._get_or_create_partner(env_admin, data)
            
            # === BUSCAR EQUIPO DE VENTAS UNISA ===
            team_unisa = self._get_team_unisa(env_admin)
            
            # === CONFIGURAR UTM ===
            medium, source, campaign = self._setup_utm(env_admin)
            
            # === CREAR ETIQUETA PARA BOT ===
            tag_bot = self._get_or_create_bot_tag(env_admin)
            
            # === CREAR LEAD ===
            lead = self._create_lead(env_admin, data, partner, team_unisa, 
                                   medium, source, campaign, tag_bot)
            
            # === ASIGNAR LEAD A USUARIO (ROUND ROBIN) ===
            self._assign_lead_round_robin(env_admin, lead, team_unisa)
            
            # === MANEJAR IMÁGENES ===
            self._handle_images(env_admin, data, lead, partner)
            
            # === RESPUESTA FINAL ===
            respuesta = self._generate_response(data)
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'lead_id': lead.id,
                    'contact_id': partner.id,
                    'team_assigned': team_unisa.name if team_unisa else "No asignado",
                    'respuesta_bot': respuesta
                }, ensure_ascii=False),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error("ERROR CREANDO LEAD", exc_info=True)
            return self._error_response(f"Error interno: {str(e)}")

    def _get_or_create_partner(self, env, data):
        """Buscar o crear contacto"""
        # Buscar por cédula
        partner = env['res.partner'].search([
            ('vat', '=', data.get('cedula'))
        ], limit=1)
        
        if not partner:
            # Buscar por teléfono
            phone = data.get('telefono_whatsapp')
            if phone:
                partner = env['res.partner'].search([
                    ('mobile', 'ilike', phone[-10:])  # Últimos 10 dígitos
                ], limit=1)
        
        partner_data = {
            'name': data.get('nombre_completo', 'Sin nombre'),
            'vat': data.get('cedula', ''),
            'birthdate_date': self._convert_date(data.get('fecha_nacimiento')),
            'mobile': data.get('telefono_whatsapp'),
            'type': 'contact',
            'company_type': 'person',
        }
        
        if partner:
            partner.write(partner_data)
            _logger.info(f"Contacto actualizado: {partner.id} - {partner.name}")
        else:
            partner = env['res.partner'].create(partner_data)
            _logger.info(f"Contacto creado: {partner.id} - {partner.name}")
        
        return partner

    def _convert_date(self, date_str):
        """Convertir fecha de formato dd/mm/yyyy a yyyy-mm-dd"""
        try:
            if date_str and '/' in date_str:
                day, month, year = date_str.split('/')
                return f"{year}-{month}-{day}"
        except:
            pass
        return False

    def _get_team_unisa(self, env):
        """Obtener equipo de ventas UNISA"""
        team = env['crm.team'].search([
            ('name', '=ilike', 'equipo de venta unisa')
        ], limit=1)
        
        if not team:
            team = env['crm.team'].search([('active', '=', True)], limit=1)
            _logger.warning(f"Equipo UNISA no encontrado. Usando: {team.name if team else 'Ninguno'}")
        else:
            _logger.info(f"Equipo UNISA encontrado: {team.name} (ID: {team.id})")
        
        return team

    def _setup_utm(self, env):
        """Configurar medium, source y campaign"""
        # Medium
        medium = env['utm.medium'].search([('name', '=ilike', 'whatsapp')], limit=1)
        if not medium:
            medium = env['utm.medium'].create({'name': 'WhatsApp'})
        
        # Source
        source = env['utm.source'].search([('name', '=ilike', 'whatsapp bot unisa')], limit=1)
        if not source:
            source = env['utm.source'].create({'name': 'WhatsApp Bot UNISA'})
        
        # Campaign
        campaign = env['utm.campaign'].search([('name', '=ilike', 'whatsapp bot unisa')], limit=1)
        if not campaign:
            campaign = env['utm.campaign'].create({'name': 'WhatsApp Bot UNISA'})
        
        return medium, source, campaign

    def _get_or_create_bot_tag(self, env):
        """Obtener o crear etiqueta para leads del bot"""
        tag = env['crm.tag'].search([
            ('name', '=ilike', 'whatsapp bot')
        ], limit=1)
        
        if not tag:
            tag = env['crm.tag'].create({
                'name': 'WhatsApp Bot',
                'color': 10  # Azul
            })
        
        return tag

    def _create_lead(self, env, data, partner, team, medium, source, campaign, tag):
        """Crear lead en CRM"""
        description = self._generate_description(data)
        
        lead_data = {
            'name': f"Cita WhatsApp - {data.get('servicio_solicitado', 'Consulta')} - {data.get('nombre_completo', 'Sin nombre')}",
            'partner_id': partner.id,
            'contact_name': data.get('nombre_completo', 'Sin nombre'),
            'phone': data.get('telefono_whatsapp'),
            'mobile': (data.get('telefono_whatsapp') or '').replace('+58', '0'),
            'description': description,
            'medium_id': medium.id,
            'source_id': source.id,
            'campaign_id': campaign.id,
            'team_id': team.id if team else False,
            'tag_ids': [(4, tag.id)],
            'type': 'opportunity',
            'stage_id': self._get_default_stage(env),
        }
        
        lead = env['crm.lead'].create(lead_data)
        _logger.info(f"Lead creado: ID {lead.id} - {lead.name}")
        
        return lead

    def _generate_description(self, data):
        """Generar descripción del lead"""
        return (
            "Cita desde WhatsApp Bot UNISA\n\n"
            f"• Paciente: {data.get('nombre_completo', 'N/A')}\n"
            f"• Cédula: {data.get('cedula', 'N/A')}\n"
            f"• Fecha de nacimiento: {data.get('fecha_nacimiento', 'N/A')}\n"
            f"• Teléfono: {data.get('telefono_whatsapp', 'N/A')}\n"
            f"• Servicio: {data.get('servicio_solicitado', 'N/A')}\n"
            f"• Fecha preferida: {data.get('fecha_preferida', 'lo antes posible')}\n"
            f"• Horario: {data.get('hora_preferida', 'cualquier hora')}\n"
            f"• Medio de pago: {data.get('medio_pago', 'N/A')}\n"
            f"• Paciente nuevo: {'Sí' if str(data.get('es_paciente_nuevo','')).lower() in ['sí','si','yes','s'] else 'No'}\n"
            f"• Interés Tarjeta Salud: {'Sí' if str(data.get('interes_tarjeta_salud','')).lower() in ['sí','si','yes','s'] else 'No'}"
        )

    def _get_default_stage(self, env):
        """Obtener etapa por defecto para leads"""
        stage = env['crm.stage'].search([
            ('team_id', '=', False),
            ('name', 'ilike', 'nuevo')
        ], limit=1)
        
        if not stage:
            stage = env['crm.stage'].search([], limit=1)
        
        return stage.id if stage else False

    def _assign_lead_round_robin(self, env, lead, team):
        """Asignar lead usando round robin"""
        if not team or not team.member_ids:
            return
        
        try:
            param_name = f'unisa_bot_last_user_{team.id}'
            last_assigned_user_id = env['ir.config_parameter'].sudo().get_param(param_name)
            
            team_members = team.member_ids.sorted('id')
            
            if last_assigned_user_id:
                last_user = env['res.users'].browse(int(last_assigned_user_id))
                if last_user in team_members:
                    current_index = team_members.ids.index(last_user.id)
                    next_index = (current_index + 1) % len(team_members)
                    next_user = team_members[next_index]
                else:
                    next_user = team_members[0]
            else:
                next_user = team_members[0]
            
            lead.write({'user_id': next_user.id})
            
            env['ir.config_parameter'].sudo().set_param(param_name, next_user.id)
            
            _logger.info(f"Lead {lead.id} asignado a {next_user.name}")
            
        except Exception as e:
            _logger.warning(f"Error en round robin: {str(e)}")

    def _handle_images(self, env, data, lead, partner):
        """Manejar imágenes adjuntas"""
        # Foto de cédula
        foto_cedula_url = data.get('foto_cedula_url')
        if foto_cedula_url and foto_cedula_url != 'foto_cedula':  # Si es una URL real
            self._create_attachment(
                env, foto_cedula_url, 
                f"Cédula_{data.get('cedula', '')}_{partner.name}",
                'crm.lead', lead.id
            )
        
        # Imágenes adicionales
        imagenes_str = data.get('imagenes_adicionales', '[]')
        try:
            imagenes = json.loads(imagenes_str) if isinstance(imagenes_str, str) else imagenes_str
            for i, img_url in enumerate(imagenes, 1):
                if img_url:
                    self._create_attachment(
                        env, img_url,
                        f"Doc_Adicional_{i}_{data.get('cedula', '')}",
                        'crm.lead', lead.id
                    )
        except Exception as e:
            _logger.error(f"Error procesando imágenes adicionales: {str(e)}")

    def _generate_response(self, data):
        """Generar respuesta para el bot"""
        return (
            "¡Tu solicitud ha sido registrada exitosamente!\n\n"
            f"• Paciente: {data.get('nombre_completo', 'N/A')}\n"
            f"• Servicio: {data.get('servicio_solicitado', 'N/A')}\n"
            f"• Preferencia: {data.get('fecha_preferida', 'lo antes posible')} por la {data.get('hora_preferida', 'cualquier hora')}\n\n"
            "En breve un ejecutivo de UNISA te contactará.\n"
            "¡Gracias por confiar en nosotros!"
        )

    def _error_response(self, message):
        """Respuesta de error"""
        return request.make_response(
            json.dumps({'success': False, 'error': message}, ensure_ascii=False),
            headers=[('Content-Type', 'application/json')],
            status=400
        )