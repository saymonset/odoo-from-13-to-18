# -*- coding: utf-8 -*-
# Archivo: unisa_chatbot_utils.py
from datetime import datetime
import json
import logging
import requests
from odoo import fields, _
import re
import base64

_logger = logging.getLogger(__name__)

class ChatBotUtils:
    
    @staticmethod
    def create_attachment(env, url, name, res_model, res_id):
        """Crear adjunto a partir de URL (Versión Python 3)"""
        try:
            _logger.info("Creando adjunto '%s' desde URL para %s:%s", name, res_model, res_id)
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                attachment = env['ir.attachment'].sudo().create({
                    'name': name,
                    'type': 'binary',
                    'datas': base64.b64encode(response.content).decode('ascii'),
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
        """Convierte fecha a formato yyyy-mm-dd para Odoo, aceptando múltiples formatos de entrada."""
        if not fecha_str:
            return False

        # Lista de formatos posibles (ordena por probabilidad de uso)
        formatos = [
            '%Y-%m-%d',      # 1975-05-24 (ISO)
            '%d/%m/%Y',      # 24/05/1975
            '%d-%m-%Y',      # 24-05-1975
            '%Y/%m/%d',      # 1975/05/24
            '%m/%d/%Y',      # 05/24/1975 (US)
            '%d.%m.%Y',      # 24.05.1975
        ]

        for fmt in formatos:
            try:
                fecha_obj = datetime.strptime(fecha_str, fmt)
                return fecha_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # Si ningún formato funciona
        _logger.error(f"Error convirtiendo fecha {fecha_str}: formato no reconocido")
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
    def find_partner_by_phone(env, phone):
        """
        Busca un partner por teléfono o móvil, normalizando a solo dígitos.
        Compara los últimos 10 dígitos para evitar problemas con +58 o 0 inicial.
        """
        if not phone:
            return None
        
        # Limpiar: solo dígitos
        phone_digits = ''.join(filter(str.isdigit, phone))
        if not phone_digits:
            return None
            
        # Tomar los últimos 10 dígitos (ej: 4141234567)
        search_suffix = phone_digits[-10:] if len(phone_digits) >= 10 else phone_digits
        
        if len(search_suffix) < 7:
            return None

        # Buscar en phone
        domain = [('phone', '=like', f'%{search_suffix}'), ('active', '=', True)]
            
        partner = env['res.partner'].sudo().search(domain, limit=1)
        
        if not partner:
            # Segunda opción: buscar el número tal cual aparece pero sin caracteres especiales
            partner = env['res.partner'].sudo().search([
                ('phone', 'ilike', phone_digits),
                ('active', '=', True)
            ], limit=1)
            
        return partner

    @staticmethod
    def update_create_contact(env, data):
        """
        Busca o crea un contacto basado en VAT o Teléfono.
        Si encuentra un contacto existente, actualiza los datos.
        """
        phone = data.get('solicitar_phone', '').strip()
        name = data.get('solicitar_name', '').strip()
        vat = data.get('solicitar_vat', '').strip()
        birthdate = data.get('solicitar_birthdate', '').strip()
        email = data.get('solicitar_email', '').strip() # Intentar capturar email si existe

        partner = None
        
        # 1. Prioridad: Buscar por VAT (Cédula)
        if vat:
            partner = env['res.partner'].sudo().search([('vat', '=', vat)], limit=1)
            if partner:
                _logger.info("Contacto encontrado por VAT: %s", vat)

        # 2. Segunda opción: Buscar por Teléfono (si no se encontró por VAT)
        if not partner and phone:
            partner = ChatBotUtils.find_partner_by_phone(env, phone)
            if partner:
                _logger.info("Contacto encontrado por Teléfono: %s", phone)

        # Preparar datos
        partner_data = {
            'name': name,
            'vat': vat,
            'phone': phone,
            'type': 'contact',
            'company_type': 'person',
        }
        if email:
            partner_data['email'] = email

        # Fecha de nacimiento
        fecha_convertida = ChatBotUtils.convert_fecha_nacimiento(birthdate)
        if fecha_convertida and 'birthdate' in env['res.partner']._fields:
            partner_data['birthdate'] = fecha_convertida

        if partner:
            # Actualizar (sin pisar el nombre si el nuevo viene vacío)
            if not partner_data.get('name'):
                partner_data.pop('name')
            partner.sudo().write(partner_data)
        else:
            # Crear
            if not partner_data.get('name'):
                partner_data['name'] = f"Contacto {phone or vat or 'Nuevo'}"
            partner = env['res.partner'].sudo().create(partner_data)
            
        return partner

    @staticmethod
    def search_contact(env, data):
        """
        Búsqueda de contacto únicamente por teléfono.
        (Método mantenido por compatibilidad; ahora usa find_partner_by_phone)
        """
        phone = data.get('solicitar_phone', '').strip()
        return ChatBotUtils.find_partner_by_phone(env, phone)

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
        """Obtener o crear equipos de UNISA (Grupo Citas y Grupo Ventas)"""
        teams = {}
        
        team_names = ['Grupo Citas', 'Grupo Ventas']
        
        for team_name in team_names:
            team = env['crm.team'].search([
                ('name', '=', team_name)
            ], limit=1)
            
            if not team:
                try:
                    team_data = {
                        'name': team_name,
                        'active': True,
                        'member_ids': False,
                    }
                    
                    if team_name == 'Grupo Citas':
                        team_data['alias_name'] = 'citas-unisa'
                    elif team_name == 'Grupo Ventas':
                        team_data['alias_name'] = 'ventas-unisa'
                    
                    team = env['crm.team'].create(team_data)
                    _logger.info(f"✅ Equipo UNISA creado: {team.name} (ID: {team.id})")
                    
                except Exception as e:
                    _logger.error(f"❌ Error creando equipo {team_name}: {str(e)}")
                    team = env['crm.team'].search([('active', '=', True)], limit=1)
                    if team:
                        _logger.warning(f"⚠️ Usando equipo existente como fallback: {team.name}")
                    else:
                        team = env['crm.team'].create({
                            'name': team_name + ' (Fallback)',
                            'active': True,
                        })
                        _logger.warning(f"⚠️ Se creó equipo genérico: {team.name}")
            else:
                _logger.info(f"✅ Equipo UNISA encontrado: {team.name} (ID: {team.id})")
            
            teams[team_name] = team
        
        return teams

    @staticmethod
    def setup_utm(env, platform='whatsapp'):
        """Configurar medium, source y campaign según la plataforma"""
        platform = platform.lower().strip() if platform else 'whatsapp'
        
        platform_names = {
            'whatsapp': 'WhatsApp',
            'instagram': 'Instagram', 
            'telegram': 'Telegram',
            'facebook': 'Facebook',
            'messenger': 'Facebook Messenger',
            'web': 'Web',
            'sms': 'SMS'
        }
        
        platform_display = platform_names.get(platform, platform.title())
        
        # Medium
        medium_name = platform_display
        medium = env['utm.medium'].search([('name', '=ilike', medium_name)], limit=1)
        if not medium:
            medium = env['utm.medium'].create({'name': medium_name})
        
        # Source
        source_name = f"{platform_display} Bot UNISA"
        source = env['utm.source'].search([('name', '=ilike', source_name)], limit=1)
        if not source:
            source = env['utm.source'].create({'name': source_name})
        
        # Campaign
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
        platform = platform.lower().strip() if platform else 'whatsapp'
        
        platform_config = {
            'whatsapp': {
                'name': 'WhatsApp Bot',
                'color': 10,
                'icon': 'fa-whatsapp'
            },
            'instagram': {
                'name': 'Instagram Bot',
                'color': 9,
                'icon': 'fa-instagram'
            },
            'telegram': {
                'name': 'Telegram Bot',
                'color': 2,
                'icon': 'fa-telegram'
            },
            'facebook': {
                'name': 'Facebook Bot',
                'color': 4,
                'icon': 'fa-facebook'
            },
            'messenger': {
                'name': 'Messenger Bot',
                'color': 4,
                'icon': 'fa-facebook-messenger'
            }
        }
        
        default_config = {
            'name': f"{platform.title()} Bot",
            'color': 1
        }
        
        config = platform_config.get(platform, default_config)
        
        tag = env['crm.tag'].sudo().search([
            ('name', '=ilike', config['name'])
        ], limit=1)
        
        if not tag:
            tag_vals = {
                'name': config['name'],
                'color': config['color'],
            }
            tag = env['crm.tag'].sudo().create(tag_vals)
            _logger.info(f"✅ Etiqueta creada para {platform}: {tag.name} (color: {tag.color})")
        else:
            _logger.info(f"✅ Etiqueta encontrada para {platform}: {tag.name}")
        
        return tag

    @staticmethod
    def create_lead(env, data, partner, team, medium, source, campaign, tag):
        """Crear lead en CRM"""
        description = ChatBotUtils.generate_description(data)
        
        lead_name = f"{data.get('solicitar_servicio', 'Consulta')} - {data.get('solicitar_name', 'Sin nombre')}"
        
        lead_data = {
            'name': lead_name,
            'partner_id': partner.id,
            'contact_name': data.get('solicitar_name', 'Sin nombre'),
            'phone': (data.get('solicitar_phone') or '').replace('+58', '0'),
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
        fecha_creacion = lead.create_date.strftime('%d/%m/%Y') if lead.create_date else datetime.now().strftime('%d/%m/%Y')
        updated_name = f"{lead.name} - ID {lead.id} ({fecha_creacion})"
        lead.write({'name': updated_name})
        _logger.info(f"Lead creado: ID {lead.id} - {lead.name}")
        
        return lead

    @staticmethod
    def generate_description(data):
        """Generar descripción del lead, omitiendo campos ausentes."""
        platform = data.get('plataforma', 'WhatsApp')
        # Normalizar a "WhatsApp" si es 'whatsapp' o 'Whatsapp'
        if platform.lower() == 'whatsapp':
            platform = 'WhatsApp'
        lines = [f"Cita desde {platform} Bot \n"]

        # Valores por defecto para campos que pueden venir vacíos
        defaults = {
            'solicitar_fecha_preferida': 'lo antes posible',
            'hora_preferida': 'cualquier hora',
        }

        fields_order = [
            ('solicitar_name', 'Paciente'),
            ('solicitar_vat', 'Cédula'),
            ('solicitar_birthdate', 'Fecha de nacimiento'),
            ('solicitar_phone', 'Teléfono'),
            ('solicitar_servicio', 'Servicio'),
            ('solicitar_fecha_preferida', 'Fecha preferida'),
            ('hora_preferida', 'Horario'),
            ('solicitar_medio_pago', 'Medio de pago'),
            ('solicitar_es_paciente_nuevo', 'Paciente nuevo'),
            ('solicitar_membresia_interes', 'Interés Tarjeta Salud'),
        ]

        for field, label in fields_order:
            if field in data:
                raw_value = data[field]
                if raw_value and str(raw_value).strip():
                    value = str(raw_value).strip()
                else:
                    if field in defaults:
                        value = defaults[field]
                    else:
                        continue

                if field in ('solicitar_es_paciente_nuevo', 'solicitar_membresia_interes'):
                    value = 'no' if str(value).lower() in ['no', 'No', 'NO', 'n'] else 'Si'

                lines.append(f"• {label}: {value}")

        if len(lines) == 1:
            lines.append("• Sin información adicional")

        return "\n".join(lines)

    @staticmethod
    def get_default_stage(env):
        """Obtener etapa por defecto para leads"""
        stage = env['crm.stage'].search([
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
        """Manejar imágenes adjuntas y publicarlas en el Chatter"""
        _logger.info("Iniciando handle_images para Lead %s y Partner %s", lead.id, partner.id)
        
        attachment_ids_lead = []
        attachment_ids_partner = []
        
        # 1. Foto de Cédula (VAT)
        foto_vat_url = data.get('foto_vat_url') or data.get('solicitar_foto_vat')
        if foto_vat_url and isinstance(foto_vat_url, str) and re.match(r'^https?://', foto_vat_url):
            vat = data.get('solicitar_vat') or 'SIN_CEDULA'
            name_vat = f"Cedula_{vat}_{partner.name or 'Cliente'}.jpg"
            
            att_lead = ChatBotUtils.create_attachment(env, foto_vat_url, name_vat, 'crm.lead', lead.id)
            if att_lead: attachment_ids_lead.append(att_lead.id)
            
            att_partner = ChatBotUtils.create_attachment(env, foto_vat_url, name_vat, 'res.partner', partner.id)
            if att_partner: attachment_ids_partner.append(att_partner.id)
        
        # 2. Imágenes Adicionales
        imgs_adicionales = data.get('imagenes_adicionales') or data.get('solicitar_imagenes_adicionales') or []
        
        if isinstance(imgs_adicionales, str):
            try:
                imgs_adicionales = json.loads(imgs_adicionales)
            except:
                imgs_adicionales = [imgs_adicionales] if imgs_adicionales.startswith('http') else []
        
        if isinstance(imgs_adicionales, list):
            vat = data.get('solicitar_vat') or 'SIN_CEDULA'
            for i, img_url in enumerate(imgs_adicionales, 1):
                if img_url and isinstance(img_url, str) and re.match(r'^https?://', img_url):
                    name_img = f"Doc_Adicional_{i}_{vat}.jpg"
                    
                    att_l = ChatBotUtils.create_attachment(env, img_url, name_img, 'crm.lead', lead.id)
                    if att_l: attachment_ids_lead.append(att_l.id)
                    
                    att_p = ChatBotUtils.create_attachment(env, img_url, name_img, 'res.partner', partner.id)
                    if att_p: attachment_ids_partner.append(att_p.id)
        
        # 3. Publicar en el Chatter para visibilidad inmediata
        if attachment_ids_lead:
            lead.sudo().message_post(
                body=_("Imágenes recibidas desde el Chatbot."),
                attachment_ids=attachment_ids_lead
            )
            _logger.info("Publicadas %d imágenes en Chatter del Lead", len(attachment_ids_lead))
            
        if attachment_ids_partner:
            partner.sudo().message_post(
                body=_("Imágenes recibidas desde el Chatbot."),
                attachment_ids=attachment_ids_partner
            )
            _logger.info("Publicadas %d imágenes en Chatter del Partner", len(attachment_ids_partner))

    @staticmethod
    def validate_image_urls(data):
        """Validar que las URLs de imágenes sean accesibles"""
        validated_data = {
            'foto_vat_url': data.get('solicitar_foto_vat', ''),
            'imagenes_adicionales': []
        }
        
        foto_url = data.get('solicitar_foto_vat', '')
        if foto_url and re.match(r'^https?://', foto_url):
            validated_data['foto_vat_url'] = foto_url
        
        imagenes_str = data.get('solicitar_imagenes_adicionales', '[]')
        try:
            imagenes = json.loads(imagenes_str) if isinstance(imagenes_str, str) else imagenes_str
            for img_url in imagenes:
                if img_url and re.match(r'^https?://', img_url):
                    validated_data['imagenes_adicionales'].append(img_url)
        except:
            validated_data['imagenes_adicionales'] = []
        
        return validated_data

    @staticmethod
    def generate_response(data):
        """Generar respuesta para el bot, omitiendo campos que no están presentes."""
        lines = ["¡Tu solicitud ha sido registrada exitosamente!\n"]

        # Solo agregar línea si el campo existe y no es None/vacío (según tu criterio)
        if data.get('solicitar_name'):
            lines.append(f"• Paciente: {data['solicitar_name']}")

        if data.get('solicitar_servicio'):
            lines.append(f"• Servicio: {data['solicitar_servicio']}")

        # Manejo especial para fecha y hora preferida (pueden venir por separado)
        fecha = data.get('solicitar_fecha_preferida')
        hora = data.get('solicitar_hora_preferida')
        if fecha or hora:
            pref = f"• Preferencia: {fecha if fecha else 'lo antes posible'}"
            if hora:
                pref += f" por la {hora}"
            else:
                pref += " a cualquier hora"
            lines.append(pref)

        # Líneas fijas finales
        lines.append("\nEn breve un ejecutivo te contactará.\n¡Gracias por confiar en nosotros!")

        return "\n".join(lines)

    @staticmethod   
    def validar_valor(valor, tipo_dato, paso=None):
        """
        Valida un valor según el tipo de dato del paso.
        :param valor: valor a validar
        :param tipo_dato: tipo de dato esperado (text, integer, float, date, etc.)
        :param paso: opcional, identificador del paso (ej. 'solicitar_phone') para validaciones especiales.
        :return: (bool, valor_transformado o mensaje_error)
        """
        # Validaciones especiales por paso
        if paso == 'solicitar_phone':
            if not valor:
                return False, "El teléfono no puede estar vacío"
            valor_str = str(valor).strip()
            digits = ''.join(filter(str.isdigit, valor_str))
            if not digits:
                return False, "El teléfono debe contener al menos un dígito"
            if len(digits) < 7:
                return False, "El teléfono debe tener al menos 7 dígitos (incluyendo código de área)"
            return True, valor_str

        # Si no hay paso especial, validar según tipo_dato
        if tipo_dato == 'text':
            return True, valor
        elif tipo_dato == 'integer':
            try:
                return True, int(valor)
            except:
                return False, "Debe ser un número entero"
        elif tipo_dato == 'float':
            try:
                return True, float(valor)
            except:
                return False, "Debe ser un número decimal"
        elif tipo_dato == 'date':
            formatos = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%d.%m.%Y',
                '%m/%d/%Y',
            ]
            valor_str = str(valor).strip()
            for fmt in formatos:
                try:
                    fecha = datetime.strptime(valor_str, fmt).date()
                    return True, fecha.isoformat()
                except ValueError:
                    continue
            return False, "Fecha inválida. Use formato DD/MM/YYYY o YYYY-MM-DD"
        elif tipo_dato == 'datetime':
            try:
                dt = fields.Datetime.from_string(valor)
                return True, dt.isoformat()
            except:
                return False, "Fecha y hora inválida"
        elif tipo_dato == 'boolean':
            if isinstance(valor, bool):
                return True, valor
            if isinstance(valor, str):
                v = valor.lower()
                if v in ['true', '1', 'yes', 'sí']:
                    return True, True
                elif v in ['false', '0', 'no']:
                    return True, False
            return False, "Debe ser un booleano (true/false)"
        elif tipo_dato == 'image':
            return True, valor
        elif tipo_dato == 'selection':
            return True, valor
        else:
            return False, f"Tipo de dato no soportado: {tipo_dato}"