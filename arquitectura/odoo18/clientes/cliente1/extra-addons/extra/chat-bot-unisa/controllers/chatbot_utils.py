# -*- coding: utf-8 -*-
# Archivo: unisa_chatbot_utils.py
from datetime import datetime
import json
import logging
import requests
from odoo import fields

_logger = logging.getLogger(__name__)

class ChatBotUtils:
    
    @staticmethod
    def create_attachment(env, url, name, res_model, res_id):
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

    @staticmethod
    def convert_fecha_nacimiento(fecha_str):
        """Convierte fecha de dd/mm/yyyy a yyyy-mm-dd para Odoo"""
        if not fecha_str:
            return False
        try:
            fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
            return fecha_obj.strftime('%Y-%m-%d')
        except Exception as e:
            _logger.error(f"Error convirtiendo fecha {fecha_str}: {str(e)}")
            return False

    @staticmethod
    def convert_date(date_str):
        """Convertir fecha de formato dd/mm/yyyy a yyyy-mm-dd"""
        try:
            if date_str and '/' in date_str:
                day, month, year = date_str.split('/')
                return f"{year}-{month}-{day}"
        except:
            pass
        return False

    @staticmethod
    def update_create_contact(env, data):
        """
        Búsqueda optimizada de contacto por múltiples criterios
        Reemplaza al método _get_or_create_partner original
        """
        cedula = data.get('cedula', '').strip()
        telefono = data.get('telefono', '').strip()
        nombre_completo = data.get('nombre_completo', '').strip()
        fecha_nacimiento = data.get('fecha_nacimiento', '').strip()
        
        partner = None
        
        # 1. Buscar por cédula exacta
        if cedula:
            partner = env['res.partner'].search([
                ('vat', '=', cedula),
                ('active', '=', True)
            ], limit=1)
        
        # 2. Si no hay cédula o no se encontró, buscar por teléfono
        if not partner and telefono:
            phone_clean = ''.join(filter(str.isdigit, telefono))
            if len(phone_clean) > 10:
                phone_clean = phone_clean[-10:]
            
            partner = env['res.partner'].search([
                ('mobile', 'ilike', f'%{phone_clean}%'),
                ('active', '=', True)
            ], limit=1)
        
        # 3. Si hay nombre y teléfono, buscar combinación
        if not partner and nombre_completo and telefono:
            phone_clean = ''.join(filter(str.isdigit, telefono))[-10:] if len(telefono) > 10 else telefono
            
            partner = env['res.partner'].search([
                ('name', 'ilike', f'%{nombre.split()[0]}%'),
                ('mobile', 'ilike', f'%{phone_clean}%'),
                ('active', '=', True)
            ], limit=1)
        
        # Preparar datos para crear/actualizar
        partner_data = {
            'name': nombre_completo or 'Sin nombre',
            'vat': cedula,
            'mobile': telefono,
            'type': 'contact',
            'company_type': 'person',
        }
        
        # Solo agregar birthdate si la fecha es válida
        fecha_convertida = ChatBotUtils.convert_fecha_nacimiento(fecha_nacimiento)
        if fecha_convertida:
            # Verificar si el campo existe en el modelo
            if 'birthdate' in env['res.partner']._fields:
                partner_data['birthdate'] = fecha_convertida
            else:
                _logger.warning("Campo 'birthdate' no disponible en res.partner")
            
        if partner:
            # Actualizar solo campos vacíos
            update_data = {}
            for field, value in partner_data.items():
                    update_data[field] = value
            
            if update_data:
                partner.write(update_data)
                _logger.info(f"Contacto actualizado: {partner.id} - {partner.name}")
        else:
            partner = env['res.partner'].create(partner_data)
            _logger.info(f"Contacto creado: {partner.id} - {partner.name}")
        
        return partner

    @staticmethod
    def get_ultima_cita(env, partner_id):
        """Obtiene información de la última cita del paciente"""
        ultima_cita = env['crm.lead'].search([
            ('partner_id', '=', partner_id),
            ('type', '=', 'opportunity'),
            ('active', '=', True)
        ], order='create_date desc', limit=1)
        
        if ultima_cita:
            return {
                'fecha': ultima_cita.create_date.strftime('%d/%m/%Y'),
                'servicio': ultima_cita.name,
                'estado': ultima_cita.stage_id.name if ultima_cita.stage_id else 'Finalizado'
            }
        return None

    @staticmethod
    def get_team_unisa(env):
        """Obtener o crear equipo de UNISA"""
        # Buscar grupo "Grupo Citas"
        team = env['crm.team'].search([
            ('name', '=ilike', 'Grupo Citas')
        ], limit=1)
        
        if not team:
            # CREAR EL GRUPO AUTOMÁTICAMENTE
            try:
                team = env['crm.team'].create({
                    'name': 'Grupo Citas',
                    'active': True,
                    'member_ids': False,  # Sin miembros por defecto
                    'alias_name': 'citas-unisa',  # Opcional: alias para correos
                })
                _logger.info(f"✅ Equipo UNISA creado: {team.name} (ID: {team.id})")
            except Exception as e:
                _logger.error(f"❌ Error creando equipo UNISA: {str(e)}")
                # Fallback: buscar cualquier equipo activo
                team = env['crm.team'].search([('active', '=', True)], limit=1)
                if team:
                    _logger.warning(f"⚠️ Usando equipo existente como fallback: {team.name}")
                else:
                    # Crear equipo genérico si no hay ninguno
                    team = env['crm.team'].create({
                        'name': 'Equipo de Ventas',
                        'active': True,
                    })
                    _logger.warning(f"⚠️ Se creó equipo genérico: {team.name}")
        else:
            _logger.info(f"✅ Equipo UNISA encontrado: {team.name} (ID: {team.id})")
        
        return team

    @staticmethod
    def setup_utm(env, platform='whatsapp'):
        """Configurar medium, source y campaign según la plataforma"""
        
        # Normalizar el nombre de la plataforma para consistencia
        platform = platform.lower().strip() if platform else 'whatsapp'
        
        # Mapeo de nombres amigables para cada plataforma
        platform_names = {
            'whatsapp': 'WhatsApp',
            'instagram': 'Instagram', 
            'telegram': 'Telegram',
            'facebook': 'Facebook',
            'messenger': 'Facebook Messenger',
            'web': 'Web',
            'sms': 'SMS'
        }
        
        # Obtener nombre formateado o usar el valor por defecto
        platform_display = platform_names.get(platform, platform.title())
        
        # Medium (tipo de canal)
        medium_name = platform_display
        medium = env['utm.medium'].search([('name', '=ilike', medium_name)], limit=1)
        if not medium:
            medium = env['utm.medium'].create({'name': medium_name})
        
        # Source (origen específico)
        source_name = f"{platform_display} Bot UNISA"
        source = env['utm.source'].search([('name', '=ilike', source_name)], limit=1)
        if not source:
            source = env['utm.source'].create({'name': source_name})
        
        # Campaign (puede ser compartida o específica)
        campaign_name = f"Campaña {platform_display} UNISA"
        
        campaign = env['utm.campaign'].search([('name', '=ilike', campaign_name)], limit=1)
        if not campaign:
            campaign = env['utm.campaign'].create({'name': campaign_name})
        
        _logger.info(f"✅ UTM configurado para plataforma: {platform_display}")
        _logger.info(f"   Medium: {medium.name} | Source: {source.name} | Campaign: {campaign.name}")
        
        return medium, source, campaign

    @staticmethod
    def get_or_create_bot_tag(env, platform='whatsapp'):
        """Obtener o crear etiqueta para leads del bot según plataforma"""
        
        # Normalizar plataforma
        platform = platform.lower().strip() if platform else 'whatsapp'
        
        # Mapeo de nombres y colores por plataforma
        platform_config = {
            'whatsapp': {
                'name': 'WhatsApp Bot',
                'color': 10,  # Azul
                'icon': 'fa-whatsapp'
            },
            'instagram': {
                'name': 'Instagram Bot',
                'color': 9,   # Rosa/Magenta
                'icon': 'fa-instagram'
            },
            'telegram': {
                'name': 'Telegram Bot',
                'color': 2,   # Celeste/Cian
                'icon': 'fa-telegram'
            },
            'facebook': {
                'name': 'Facebook Bot',
                'color': 4,   # Azul Facebook
                'icon': 'fa-facebook'
            },
            'messenger': {
                'name': 'Messenger Bot',
                'color': 4,   # Azul Facebook
                'icon': 'fa-facebook-messenger'
            }
        }
        
        # Configuración por defecto si la plataforma no está en el mapeo
        default_config = {
            'name': f"{platform.title()} Bot",
            'color': 1,  # Gris por defecto
            'icon': 'fa-comment'
        }
        
        # Obtener configuración
        config = platform_config.get(platform, default_config)
        
        # Buscar etiqueta existente (por nombre exacto)
        tag = env['crm.tag'].sudo().search([
            ('name', '=ilike', config['name'])
        ], limit=1)
        
        if not tag:
            # Crear nueva etiqueta
            tag_vals = {
                'name': config['name'],
                'color': config['color'],
            }
            
            # Intentar añadir icono si el campo existe en el modelo
            try:
                tag_vals['icon'] = config['icon']
            except:
                pass  # Ignorar si el campo no existe
            
            tag = env['crm.tag'].sudo().create(tag_vals)
            _logger.info(f"✅ Etiqueta creada para {platform}: {tag.name} (color: {tag.color})")
        else:
            _logger.info(f"✅ Etiqueta encontrada para {platform}: {tag.name}")
        
        return tag
    
    @staticmethod
    def create_lead(env, data, partner, team, medium, source, campaign, tag):
        """Crear lead en CRM"""
        description = ChatBotUtils.generate_description(data)
        
        lead_data = {
            'name': f"Cita WhatsApp - {data.get('servicio_solicitado', 'Consulta')} - {data.get('nombre_completo', 'Sin nombre')}",
            'partner_id': partner.id,
            'contact_name': data.get('nombre_completo', 'Sin nombre'),
            'phone': data.get('telefono'),
            'mobile': (data.get('telefono') or '').replace('+58', '0'),
            'description': description,
            'medium_id': medium.id,
            'source_id': source.id,
            'campaign_id': campaign.id,
            'team_id': team.id if team else False,
            'tag_ids': [(4, tag.id)],
            'type': 'opportunity',
            'stage_id': ChatBotUtils.get_default_stage(env),
        }
        
        lead = env['crm.lead'].create(lead_data)
        _logger.info(f"Lead creado: ID {lead.id} - {lead.name}")
        
        return lead

    @staticmethod
    def generate_description(data):
        """Generar descripción del lead"""
        return (
            "Cita desde WhatsApp Bot UNISA\n\n"
            f"• Paciente: {data.get('nombre_completo', 'N/A')}\n"
            f"• Cédula: {data.get('cedula', 'N/A')}\n"
            f"• Fecha de nacimiento: {data.get('fecha_nacimiento', 'N/A')}\n"
            f"• Teléfono: {data.get('telefono', 'N/A')}\n"
            f"• Servicio: {data.get('servicio', 'N/A')}\n"
            f"• Fecha preferida: {data.get('fecha_deseada', 'lo antes posible')}\n"
            f"• Horario: {data.get('hora_preferida', 'cualquier hora')}\n"
            f"• Medio de pago: {data.get('medio_pago', 'N/A')}\n"
            f"• Paciente nuevo: {'Sí' if str(data.get('es_paciente_nuevo','')).lower() in ['sí','si','yes','s'] else 'No'}\n"
            f"• Interés Tarjeta Salud: {'Sí' if str(data.get('membresia_interes','')).lower() in ['sí','si','yes','s'] else 'No'}"
        )

    @staticmethod
    def get_default_stage(env):
        """Obtener etapa por defecto para leads"""
        stage = env['crm.stage'].search([
            ('team_id', '=', False),
            ('name', 'ilike', 'nuevo')
        ], limit=1)
        
        if not stage:
            stage = env['crm.stage'].search([], limit=1)
        
        return stage.id if stage else False

    @staticmethod
    def assign_lead_round_robin(env, lead, team):
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

    @staticmethod
    def handle_images(env, data, lead, partner):
        """Manejar imágenes adjuntas"""
        # Foto de cédula
        foto_cedula_url = data.get('foto_cedula_url')
        if foto_cedula_url and foto_cedula_url != 'foto_cedula':  # Si es una URL real
            ChatBotUtils.create_attachment(
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
                    ChatBotUtils.create_attachment(
                        env, img_url,
                        f"Doc_Adicional_{i}_{data.get('cedula', '')}",
                        'crm.lead', lead.id
                    )
        except Exception as e:
            _logger.error(f"Error procesando imágenes adicionales: {str(e)}")

    @staticmethod
    def generate_response(data):
        """Generar respuesta para el bot"""
        return (
            "¡Tu solicitud ha sido registrada exitosamente!\n\n"
            f"• Paciente: {data.get('nombre_completo', 'N/A')}\n"
            f"• Servicio: {data.get('servicio_solicitado', 'N/A')}\n"
            f"• Preferencia: {data.get('fecha_preferida', 'lo antes posible')} por la {data.get('hora_preferida', 'cualquier hora')}\n\n"
            "En breve un ejecutivo de UNISA te contactará.\n"
            "¡Gracias por confiar en nosotros!"
        )