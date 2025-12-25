# -*- coding: utf-8 -*-
from datetime import datetime
import json
import logging
import requests
from odoo import http, fields
from odoo.http import request

# Importar la clase de utilidades
from .chatbot_utils import ChatBotUtils

_logger = logging.getLogger(__name__)

class UnisaChatBotController(http.Controller):
    
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
               # Formatear fecha de nacimiento para el bot (dd/mm/yyyy)
                fecha_nac_formateada = ''
                if partner.birthdate:
                    fecha_nac_formateada = partner.birthdate.strftime('%d/%m/%Y')
                return {
                    'existe': True,
                    'iniciales': ''.join([n[0] for n in partner.name.split()[:2]]).upper(),
                    'ultima_cita': ChatBotUtils.get_ultima_cita(env, partner.id),
                     'cedula': partner.vat or '',
                    'nombre_completo': partner.name or '',
                    'fecha_nacimiento': fecha_nac_formateada,
                    'telefono': partner.mobile or '',
                    'email': partner.email or '',
                    'es_paciente_nuevo': 'no'
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
            partner = ChatBotUtils.update_create_contact(env_admin, data)
            
            # === BUSCAR EQUIPO DE VENTAS UNISA ===
            team_unisa = ChatBotUtils.get_team_unisa(env_admin)
            
            
            
            # Obtener plataforma del request, con valor por defecto
            platform = data.get('platform', 'whatsapp')

            
            # === CONFIGURAR UTM ===
            medium, source, campaign = ChatBotUtils.setup_utm(env_admin, platform)
            
            # === CREAR ETIQUETA PARA BOT ===
            tag_bot = ChatBotUtils.get_or_create_bot_tag(env_admin, platform)
            
            # === CREAR LEAD ===
            lead = ChatBotUtils.create_lead(env_admin, data, partner, team_unisa, 
                                   medium, source, campaign, tag_bot)
            
            # === ASIGNAR LEAD A USUARIO (ROUND ROBIN) ===
            ChatBotUtils.assign_lead_round_robin(env_admin, lead, team_unisa)
            
            # === MANEJAR IMÁGENES ===
            ChatBotUtils.handle_images(env_admin, data, lead, partner)
            
            # === RESPUESTA FINAL ===
            respuesta = ChatBotUtils.generate_response(data)
            
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

    def _error_response(self, message):
        """Respuesta de error"""
        return request.make_response(
            json.dumps({'success': False, 'error': message}, ensure_ascii=False),
            headers=[('Content-Type', 'application/json')],
            status=400
        )