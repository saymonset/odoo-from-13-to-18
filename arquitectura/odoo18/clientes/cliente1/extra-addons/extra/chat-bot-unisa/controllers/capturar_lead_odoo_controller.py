# -*- coding: utf-8 -*-
from datetime import datetime
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


# @http.route('/chat-bot-unisa/capturar_lead',
#                 auth='public',
#                 type='http',
#                 methods=['POST'],
#                 csrf=False,
#                 cors='*')
    @http.route('/chat-bot-unisa/verificar_usuario',
                auth='public',
                type='json',
                methods=['POST'],
                csrf=False,
                cors='*')
    def verificar_usuario(self, **kw):
        """
        Verifica si un usuario existe en el sistema por teléfono o cédula
        para pre-llenar datos en el bot
        """
        try:
            # OPCIÓN 1: Usar los parámetros de kw (recomendado)
            # Odoo automáticamente pasa los parámetros del JSON-RPC aquí
            data = kw.get('params', {}) if 'params' in kw else kw
            
            # OPCIÓN 2: Usar request.params (alternativa)
            # data = request.params
            
            _logger.info("VERIFICANDO USUARIO: %s", json.dumps(data, indent=2))
            
            telefono = data.get('telefono')
            cedula = data.get('cedula')
                
            if not telefono and not cedula:
                return {
                    'success': False,
                    'error': 'Se requiere teléfono o cédula'
                }
            
            # Usar usuario admin para búsqueda
            admin_uid = request.env.ref('base.user_admin').id or 2
            env = request.env(user=admin_uid)
            
            partner = None
            
            # Buscar por cédula (prioridad)
            if cedula:
                partner = env['res.partner'].search([
                    ('vat', '=', cedula),
                    ('active', '=', True)
                ], limit=1)
            
            # Si no se encontró por cédula, buscar por teléfono
            if not partner and telefono:
                # Limpiar teléfono para búsqueda
                phone_clean = telefono.replace('+', '').replace(' ', '').replace('-', '')
                if len(phone_clean) > 10:
                    phone_clean = phone_clean[-10:]  # Últimos 10 dígitos
                
                partner = env['res.partner'].search([
                    ('mobile', 'ilike', f'%{phone_clean}%'),
                    ('active', '=', True)
                ], limit=1)
            
            if partner:
                # Formatear fecha de nacimiento para el bot (dd/mm/yyyy)
                fecha_nac_formateada = ''
                if partner.birthdate:
                    fecha_nac_formateada = partner.birthdate.strftime('%d/%m/%Y')
                
                # Verificar si tiene citas anteriores
                citas_anteriores = env['crm.lead'].search([
                    ('partner_id', '=', partner.id),
                    ('type', '=', 'opportunity'),
                    ('active', '=', True)
                ], order='create_date desc', limit=5)
                
                historial = []
                for cita in citas_anteriores:
                    historial.append({
                        'fecha': cita.create_date.strftime('%d/%m/%Y %H:%M'),
                        'servicio': cita.name,
                        'estado': cita.stage_id.name if cita.stage_id else 'N/A'
                    })
                
                return {
                    'success': True,
                    'existe': True,
                    'datos': {
                        'cedula': partner.vat or '',
                        'nombre_completo': partner.name or '',
                        'fecha_nacimiento': fecha_nac_formateada,
                        'telefono': partner.mobile or '',
                        'email': partner.email or '',
                        'es_paciente_nuevo': 'no',
                        'historial_citas': historial
                    },
                    'mensaje': f'¡Hola de nuevo, {partner.name}! Veo que ya estás registrado en nuestro sistema. 😊'
                }
            else:
                return {
                    'success': True,
                    'existe': False,
                    'mensaje': 'No encontramos tu registro. Te ayudaré a crear uno nuevo.'
                }
                
        except Exception as e:
            _logger.error("ERROR VERIFICANDO USUARIO", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/chat-bot-unisa/buscar_por_telefono',
                auth='public',
                type='json',
                methods=['POST'],
                csrf=False,
                cors='*')
    def buscar_por_telefono(self, **kw):
        """
        Búsqueda rápida solo por teléfono para iniciar conversación
        """
        try:
            # Odoo automáticamente pasa los parámetros del JSON-RPC aquí
            data = kw.get('params', {}) if 'params' in kw else kw
            
            # OPCIÓN 2: Usar request.params (alternativa)
            # data = request.params
            
            _logger.info("VERIFICANDO USUARIO: %s", json.dumps(data, indent=2))
            
            telefono = data.get('telefono')
            
            if not telefono:
                return {'existe': False}
            
            admin_uid = request.env.ref('base.user_admin').id or 2
            env = request.env(user=admin_uid)
            
            # Limpiar y formatear teléfono
            phone_clean = ''.join(filter(str.isdigit, telefono))
            if len(phone_clean) > 10:
                phone_clean = phone_clean[-10:]
            
            partner = env['res.partner'].search([
                '|',
                ('mobile', 'ilike', f'%{phone_clean}%'),
                ('phone', 'ilike', f'%{phone_clean}%'),
                ('active', '=', True)
            ], limit=1)
            
            if partner:
                return {
                    'existe': True,
                    'nombre': partner.name,
                    'iniciales': ''.join([n[0] for n in partner.name.split()[:2]]).upper(),
                    'ultima_cita': self._get_ultima_cita(env, partner.id)
                }
            
            return {'existe': False}
            
        except Exception as e:
            _logger.error("ERROR BUSCANDO POR TELÉFONO", exc_info=True)
            return {'existe': False}

    @http.route('/chat-bot-unisa/precargar_datos',
                auth='public',
                type='json',
                methods=['POST'],
                csrf=False,
                cors='*')
    def precargar_datos(self, **kw):
        """
        Pre-carga todos los datos del usuario para el bot
        """
        try:
                        # Odoo automáticamente pasa los parámetros del JSON-RPC aquí
            data = kw.get('params', {}) if 'params' in kw else kw
            
            # OPCIÓN 2: Usar request.params (alternativa)
            # data = request.params
            
            _logger.info("VERIFICANDO USUARIO: %s", json.dumps(data, indent=2))
            
            telefono = data.get('telefono')

            
            if not telefono:
                return {'success': False, 'error': 'Teléfono requerido'}
            
            admin_uid = request.env.ref('base.user_admin').id or 2
            env = request.env(user=admin_uid)
            
            # Buscar contacto
            phone_clean = ''.join(filter(str.isdigit, telefono))
            if len(phone_clean) > 10:
                phone_clean = phone_clean[-10:]
            
            partner = env['res.partner'].search([
                ('mobile', 'ilike', f'%{phone_clean}%'),
                ('active', '=', True)
            ], limit=1)
            
            if not partner:
                return {'success': False, 'error': 'Usuario no encontrado'}
            
            # Obtener datos completos
            fecha_nac = ''
            if partner.birthdate:
                fecha_nac = partner.birthdate.strftime('%d/%m/%Y')
            
            # Buscar citas anteriores
            leads = env['crm.lead'].search([
                ('partner_id', '=', partner.id),
                ('type', '=', 'opportunity'),
                ('active', '=', True)
            ], order='create_date desc', limit=3)
            
            historial = []
            for lead in leads:
                historial.append({
                    'fecha': lead.create_date.strftime('%d/%m/%Y'),
                    'servicio': lead.name,
                    'estado': lead.stage_id.name if lead.stage_id else 'Finalizado'
                })
            
            return {
                'success': True,
                'datos': {
                    'cedula': partner.vat or '',
                    'nombre_completo': partner.name or '',
                    'fecha_nacimiento': fecha_nac,
                    'telefono': partner.mobile or '',
                    'email': partner.email or '',
                    'historial': historial,
                    'total_citas': len(leads)
                }
            }
            
        except Exception as e:
            _logger.error("ERROR PRECARGANDO DATOS", exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/chat-bot-unisa/capturar_lead',
                auth='public',
                type='json',
                methods=['POST'],
                csrf=False,
                cors='*')
    def capturar_lead_odoo(self, **kw):
        try:

            data = kw.get('params', {}) if 'params' in kw else kw
            
            # OPCIÓN 2: Usar request.params (alternativa)
            # data = request.params
            
            _logger.info("VERIFICANDO USUARIO: %s", json.dumps(data, indent=2))
            


            _logger.info("LEAD RECIBIDO: %s", json.dumps(data, indent=2, ensure_ascii=False))

            # === USUARIO ADMIN ===
            admin_uid = request.env.ref('base.user_admin').id or 2
            env_admin = request.env(user=admin_uid)
            
            # === OPTIMIZACIÓN: Búsqueda inteligente (reemplaza _get_or_create_partner) ===
            partner = self._busqueda_inteligente_partner(env_admin, data)
            
            # === BUSCAR EQUIPO DE VENTAS UNISA ===
            team_unisa = self._get_team_unisa(env_admin)
            
            
            
            # Obtener plataforma del request, con valor por defecto
            platform = data.get('platform', 'whatsapp')

            
            # === CONFIGURAR UTM ===
            medium, source, campaign = self._setup_utm(env_admin, platform)
            
            # === CREAR ETIQUETA PARA BOT ===
            tag_bot = self._get_or_create_bot_tag(env_admin, platform)
            
            # === CREAR LEAD ===
            lead = self._create_lead(env_admin, data, partner, team_unisa, 
                                   medium, source, campaign, tag_bot)
            
            # === ASIGNAR LEAD A USUARIO (ROUND ROBIN) ===
            self._assign_lead_round_robin(env_admin, lead, team_unisa)
            
            # === MANEJAR IMÁGENES ===
            self._handle_images(env_admin, data, lead, partner)
            
            # === RESPUESTA FINAL ===
            respuesta = self._generate_response(data)
            
            return {
                    'success': True,
                    'lead_id': lead.id,
                    'contact_id': partner.id,
                    'team_assigned': team_unisa.name if team_unisa else "No asignado",
                    'respuesta_bot': respuesta
                }

        except Exception as e:
            _logger.error("ERROR CREANDO LEAD", exc_info=True)
            return self._error_response(f"Error interno: {str(e)}")

    def _convert_fecha_nacimiento(self, fecha_str):
        """Convierte fecha de dd/mm/yyyy a yyyy-mm-dd para Odoo"""
        if not fecha_str:
            return False
        try:
            fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
            return fecha_obj.strftime('%Y-%m-%d')
        except Exception as e:
            _logger.error(f"Error convirtiendo fecha {fecha_str}: {str(e)}")
            return False
        
    def _busqueda_inteligente_partner(self, env, data):
        """
        Búsqueda optimizada de contacto por múltiples criterios
        Reemplaza al método _get_or_create_partner original
        """
        cedula = data.get('cedula', '').strip()
        telefono = data.get('telefono', '').strip()
        nombre = data.get('nombre', '').strip()
        
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
        if not partner and nombre and telefono:
            phone_clean = ''.join(filter(str.isdigit, telefono))[-10:] if len(telefono) > 10 else telefono
            
            partner = env['res.partner'].search([
                ('name', 'ilike', f'%{nombre.split()[0]}%'),
                ('mobile', 'ilike', f'%{phone_clean}%'),
                ('active', '=', True)
            ], limit=1)
        
        # Preparar datos para crear/actualizar
        partner_data = {
            'name': nombre or 'Sin nombre',
            'vat': cedula,
            'mobile': telefono,
            'type': 'contact',
            'company_type': 'person',
        }
        
        # Solo agregar birthdate si la fecha es válida
        fecha_convertida = self._convert_fecha_nacimiento(data.get('fecha_nacimiento'))
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
                if value and (not getattr(partner, field) or field == 'mobile'):
                    update_data[field] = value
            
            if update_data:
                partner.write(update_data)
                _logger.info(f"Contacto actualizado: {partner.id} - {partner.name}")
        else:
            partner = env['res.partner'].create(partner_data)
            _logger.info(f"Contacto creado: {partner.id} - {partner.name}")
        
        return partner

    def _get_ultima_cita(self, env, partner_id):
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

    def _get_team_unisa(self, env):
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

    def _setup_utm(self, env, platform='whatsapp'):
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
        # Opción 1: Campaña específica por plataforma
        campaign_name = f"Campaña {platform_display} UNISA"
        # Opción 2: Campaña general (descomenta si prefieres)
        # campaign_name = "Campaña ChatBot UNISA"
        
        campaign = env['utm.campaign'].search([('name', '=ilike', campaign_name)], limit=1)
        if not campaign:
            campaign = env['utm.campaign'].create({'name': campaign_name})
        
        _logger.info(f"✅ UTM configurado para plataforma: {platform_display}")
        _logger.info(f"   Medium: {medium.name} | Source: {source.name} | Campaign: {campaign.name}")
        
        return medium, source, campaign

    def _get_or_create_bot_tag(self, env, platform='whatsapp'):
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
        tag = env['crm.tag'].search([
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
            
            tag = env['crm.tag'].create(tag_vals)
            _logger.info(f"✅ Etiqueta creada para {platform}: {tag.name} (color: {tag.color})")
        else:
            _logger.info(f"✅ Etiqueta encontrada para {platform}: {tag.name}")
        
        return tag
    
    def _create_lead(self, env, data, partner, team, medium, source, campaign, tag):
        """Crear lead en CRM"""
        description = self._generate_description(data)
        
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
            f"• Teléfono: {data.get('telefono', 'N/A')}\n"
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

    def _convert_date(self, date_str):
        """Convertir fecha de formato dd/mm/yyyy a yyyy-mm-dd"""
        try:
            if date_str and '/' in date_str:
                day, month, year = date_str.split('/')
                return f"{year}-{month}-{day}"
        except:
            pass
        return False